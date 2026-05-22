import os
from typing import Any, Dict, List, Optional

import openai

from app.core.config import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    QDRANT_URL,
    QDRANT_DISTANCE,
)
from app.db.qdrant import create_collection_if_not_exists, get_qdrant_client, upsert_points
from app.services.chunk_service import chunk_repository

MODEL_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}


def semantic_search(
    query: str,
    top_k: int = 5,
    collection_name: Optional[str] = None,
    model: Optional[str] = None,
    repo_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Perform semantic search against Qdrant for the given query."""
    collection_name = collection_name or QDRANT_COLLECTION
    model = model or OPENAI_EMBEDDING_MODEL

    _configure_openai()
    response = openai.Embedding.create(model=model, input=[query])
    query_vector = response["data"][0]["embedding"]

    qdrant_client = get_qdrant_client(QDRANT_URL, QDRANT_API_KEY)

    query_filter = None
    if repo_id:
        query_filter = rest_models.Filter(
            must=[
                rest_models.FieldCondition(
                    key="repo_id",
                    match=rest_models.MatchValue(value=repo_id),
                )
            ]
        )

    hits = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter=query_filter,
    )

    results: List[Dict[str, Any]] = []
    for hit in hits:
        payload = getattr(hit, "payload", None) or {}
        results.append(
            {
                "id": getattr(hit, "id", None),
                "score": getattr(hit, "score", None),
                "payload": payload,
            }
        )

    return results

BATCH_SIZE = 32


def _configure_openai() -> None:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set. Please add OPENAI_API_KEY to .env.")

    openai.api_key = OPENAI_API_KEY


def embed_texts(texts: List[str], model: str) -> List[List[float]]:
    _configure_openai()

    embeddings: List[List[float]] = []
    for i in range(0, len(texts), 100):
        batch = texts[i : i + 100]
        response = openai.Embedding.create(model=model, input=batch)
        embeddings.extend([item["embedding"] for item in response["data"]])

    return embeddings


def ingest_repository_to_qdrant(
    repo_path: str,
    collection_name: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, object]:
    collection_name = collection_name or QDRANT_COLLECTION
    model = model or OPENAI_EMBEDDING_MODEL

    chunks = chunk_repository(repo_path)
    if not chunks:
        raise ValueError(f"No eligible code files found under {repo_path}.")

    if model not in MODEL_DIMENSIONS:
        raise ValueError(
            "Unsupported embedding model. Use text-embedding-3-small or text-embedding-3-large."
        )

    qdrant_client = get_qdrant_client(QDRANT_URL, QDRANT_API_KEY)
    create_collection_if_not_exists(
        qdrant_client,
        collection_name=collection_name,
        vector_size=MODEL_DIMENSIONS[model],
        distance=QDRANT_DISTANCE,
    )

    total_points = 0
    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]
        texts = [chunk["content"] for chunk in batch]
        vectors = embed_texts(texts, model)

        points = []
        for chunk, vector in zip(batch, vectors):
            points.append(
                {
                    "id": chunk["id"],
                    "vector": vector,
                    "payload": {
                        "chunk_id": chunk["chunk_id"],
                        "path": chunk["path"],
                        "filename": chunk["filename"],
                        "language": chunk["language"],
                        "chunk_index": chunk["chunk_index"],
                        "line_range": chunk["line_range"],
                        "content": chunk["content"],
                    },
                }
            )

        upsert_points(qdrant_client, collection_name=collection_name, points=points)
        total_points += len(points)

    return {
        "status": "success",
        "collection_name": collection_name,
        "model": model,
        "ingested_points": total_points,
        "repo_path": repo_path,
    }
