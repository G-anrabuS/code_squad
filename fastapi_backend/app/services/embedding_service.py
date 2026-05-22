import uuid
import time
import logging
from typing import Any, Dict, List, Optional

from google import genai
from qdrant_client.http import models as rest_models

from app.core.config import (
    GEMINI_API_KEY,
    QDRANT_API_KEY,
    QDRANT_URL,
    QDRANT_DISTANCE,
)
from app.db.qdrant import (
    create_collection_if_not_exists,
    get_qdrant_client,
    upsert_points,
)
from app.services.chunk_service import chunk_repository

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-2"

# Updated to 3072 to match Gemini's native output dimension
MODEL_DIMENSIONS = {
    EMBEDDING_MODEL: 3072,
}

BATCH_SIZE = 32


def generate_collection_name() -> str:
    """
    Generate unique temporary Qdrant collection name.
    """
    return f"repo_{uuid.uuid4().hex}"


def cleanup_qdrant_collection(collection_name: str):
    """
    Delete temporary Qdrant collection after analysis.
    """
    try:
        qdrant_client = get_qdrant_client(QDRANT_URL, QDRANT_API_KEY)
        qdrant_client.delete_collection(collection_name=collection_name)
    except Exception:
        pass


def embed_texts(
    texts: List[str],
    model: str = EMBEDDING_MODEL,
) -> List[List[float]]:
    """
    Generate embeddings for a list of text chunks using Gemini's native batching
    and exponential backoff retry for rate limits.
    """
    if not texts:
        return []

    max_retries = 6
    base_delay = 4.0  # Seconds to wait initially on rate limit hits

    for attempt in range(max_retries):
        try:
            # Pass the entire list at once to utilize batching (1 request instead of 32)
            response = client.models.embed_content(
                model=model,
                contents=texts,
            )
            return [emb.values for emb in response.embeddings]

        except Exception as e:
            err_str = str(e).lower()
            # Catch 429, Resource Exhausted, or Rate Limit errors
            if "429" in err_str or "exhausted" in err_str or "rate limit" in err_str:
                delay = base_delay * (2**attempt)
                logger.warning(
                    f"Gemini Rate Limit Hit (TPM/RPM). Retrying attempt {attempt + 1}/{max_retries} after sleeping {delay}s..."
                )
                time.sleep(delay)
            else:
                raise e

    raise RuntimeError("Max retries exceeded for Gemini embedding due to rate limits.")


def semantic_search(
    query: str,
    top_k: int = 5,
    collection_name: Optional[str] = None,
    model: Optional[str] = None,
    repo_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Perform semantic search against Qdrant.
    """
    if not collection_name:
        raise ValueError("collection_name is required for semantic search.")

    model = model or EMBEDDING_MODEL

    response = client.models.embed_content(
        model=model,
        contents=query,
    )

    query_vector = response.embeddings[0].values

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

    response = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter=query_filter,
    )

    results: List[Dict[str, Any]] = []

    for hit in response.points:
        payload = getattr(hit, "payload", None) or {}

        results.append(
            {
                "id": getattr(hit, "id", None),
                "score": getattr(hit, "score", None),
                "payload": payload,
            }
        )

    return results


def ingest_repository_to_qdrant(
    repo_path: str,
    collection_name: Optional[str] = None,
    model: Optional[str] = None,
    repo_id: Optional[str] = None,
) -> Dict[str, object]:
    """
    Chunk repository, generate embeddings, and store in Qdrant.
    """
    collection_name = collection_name or generate_collection_name()
    model = model or EMBEDDING_MODEL

    if model not in MODEL_DIMENSIONS:
        raise ValueError(
            f"Unsupported embedding model. Supported: {list(MODEL_DIMENSIONS.keys())}"
        )

    chunks = chunk_repository(repo_path)

    if not chunks:
        raise ValueError(f"No eligible code files found under {repo_path}.")

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
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["id"]))

            points.append(
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": {
                        "repo_id": repo_id,
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

        upsert_points(
            qdrant_client,
            collection_name=collection_name,
            points=points,
        )

        total_points += len(points)

        # Add a minor delay between batch requests to safely respect the TPM quota
        time.sleep(1.5)

    return {
        "status": "success",
        "collection_name": collection_name,
        "model": model,
        "ingested_points": total_points,
        "repo_path": repo_path,
    }
