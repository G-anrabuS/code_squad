import os
import uuid
from typing import Any, Dict, List, Optional

from sentence_transformers import SentenceTransformer
from qdrant_client.http import models as rest_models

from app.core.config import (
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    QDRANT_URL,
    QDRANT_DISTANCE,
)
from app.db.qdrant import (
    create_collection_if_not_exists,
    get_qdrant_client,
    upsert_points,
)
from app.services.chunk_service import chunk_repository

# Define the new local model
LOCAL_MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_DIMENSIONS = {
    LOCAL_MODEL_NAME: 384,  # Updated to MiniLM's dimension size
}

BATCH_SIZE = 32

# Load the model once in memory (it will download automatically the first time)
_embedding_model = None


def _get_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        print(
            "Loading local embedding model (this may take a moment the first time)..."
        )
        _embedding_model = SentenceTransformer(LOCAL_MODEL_NAME)
    return _embedding_model


def semantic_search(
    query: str,
    top_k: int = 5,
    collection_name: Optional[str] = None,
    model: Optional[str] = None,
    repo_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Perform semantic search against Qdrant for the given query."""
    collection_name = collection_name or QDRANT_COLLECTION
    model = model or LOCAL_MODEL_NAME

    transformer = _get_model()

    # encode returns a numpy array, .tolist() converts it to standard Python floats
    query_vector = transformer.encode(query).tolist()

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


def embed_texts(texts: List[str], model: str) -> List[List[float]]:
    transformer = _get_model()
    # SentenceTransformers handles batching natively and efficiently
    embeddings = transformer.encode(texts, batch_size=BATCH_SIZE).tolist()
    return embeddings


def ingest_repository_to_qdrant(
    repo_path: str,
    collection_name: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, object]:
    collection_name = collection_name or QDRANT_COLLECTION
    model = model or LOCAL_MODEL_NAME

    chunks = chunk_repository(repo_path)
    if not chunks:
        raise ValueError(f"No eligible code files found under {repo_path}.")

    if model not in MODEL_DIMENSIONS:
        raise ValueError(f"Unsupported embedding model. Use {LOCAL_MODEL_NAME}.")

    qdrant_client = get_qdrant_client(QDRANT_URL, QDRANT_API_KEY)

    # This will create a new collection requiring 384 dimensions
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

            # Generate a valid UUID from your string ID using uuid5
            valid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["id"]))

            points.append(
                {
                    "id": valid_uuid,  # <--- Use the newly generated UUID here
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

    return {
        "status": "success",
        "collection_name": collection_name,
        "model": model,
        "ingested_points": total_points,
        "repo_path": repo_path,
    }
