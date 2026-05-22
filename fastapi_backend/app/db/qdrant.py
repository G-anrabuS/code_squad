import warnings
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models


def get_qdrant_client(
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    prefer_grpc: bool = False,
    check_compatibility: bool = False,
) -> QdrantClient:
    url = url or "http://localhost:6333"
    client_args = {
        "url": url,
        "prefer_grpc": prefer_grpc,
        "check_compatibility": check_compatibility,
    }

    if api_key:
        client_args["api_key"] = api_key

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Api key is used with an insecure connection.",
        )
        return QdrantClient(**client_args)


def create_collection_if_not_exists(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
    distance: str = "Cosine",
) -> None:
    try:
        client.get_collection(collection_name=collection_name)
    except Exception:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=rest_models.VectorParams(
                size=vector_size,
                distance=rest_models.Distance[distance.upper()],
            ),
        )


def upsert_points(
    client: QdrantClient,
    collection_name: str,
    points: List[Dict[str, Any]],
) -> None:
    client.upsert(collection_name=collection_name, points=points)
