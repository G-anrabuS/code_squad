import hashlib
import os
import uuid
from typing import Any, Dict, List, Optional

import openai

from app.core.config import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    QDRANT_DISTANCE,
    QDRANT_URL,
)
from app.db.qdrant import (
    create_collection_if_not_exists,
    get_qdrant_client,
    upsert_points,
)
from app.services.chunk_service import chunk_repository
from app.services.codebase_parser import CodebaseParser
from app.services.embedding_service import embed_texts

ENTRY_POINT_PATTERNS = [
    "main.py",
    "app.py",
    "server.py",
    "index.js",
    "index.ts",
    "routes",
    "controllers",
    "application.py",
    "startup.py",
    "handler.py",
    "bootstrap.py",
    "cli.py",
    "manage.py",
]

DEPENDENCY_FILES = [
    "requirements.txt",
    "package.json",
    "pyproject.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "go.mod",
    "mix.exs",
    "Cargo.toml",
    "composer.json",
    "package-lock.json",
]


def _configure_openai() -> None:
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set. Please add OPENAI_API_KEY to .env."
        )
    openai.api_key = OPENAI_API_KEY


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def _summarize_folder_tree(tree: Dict[str, Any], max_children: int = 5) -> str:
    if not tree or "children" not in tree:
        return ""

    children = tree.get("children", [])
    top_dirs = [
        child.get("name") for child in children if child.get("type") == "directory"
    ][:max_children]
    top_files = [
        child.get("name") for child in children if child.get("type") == "file"
    ][:max_children]
    summary_lines = [
        f"Top-level directories: {', '.join(top_dirs) if top_dirs else 'None'}",
        f"Top-level files: {', '.join(top_files) if top_files else 'None'}",
        f"Total top-level items: {len(children)}",
    ]
    return " | ".join(summary_lines)


def _find_entry_points(file_paths: List[str]) -> List[str]:
    entry_points = []
    for path in file_paths:
        normalized = _normalize_path(path).lower()
        if any(pattern in normalized for pattern in ENTRY_POINT_PATTERNS):
            entry_points.append(path)
    return sorted(set(entry_points))[:20]


def _find_dependency_files(file_paths: List[str]) -> List[str]:
    found = [path for path in file_paths if os.path.basename(path) in DEPENDENCY_FILES]
    return sorted(found)


def _build_project_summary(codebase_data: Dict[str, Any]) -> str:
    tech_stack = codebase_data.get("tech_stack", [])
    project_type = codebase_data.get("project_type", "Unknown")
    total_files = codebase_data.get("total_files", 0)
    dependencies = codebase_data.get("dependencies", {})
    dependency_count = sum(len(values) for values in dependencies.values())

    parts = [
        f"Project type: {project_type}",
        f"Total files: {total_files}",
        f"Tech stack: {', '.join(tech_stack) if tech_stack else 'Unknown'}",
        f"Dependency files: {dependency_count} detected",
    ]
    return "; ".join(parts)


def build_repo_context(repo_path: str, repo_id: Optional[str] = None) -> Dict[str, Any]:
    parser = CodebaseParser(repo_path)
    codebase_data = parser.parse()

    entry_points = _find_entry_points(list(parser.files.keys()))
    dependency_files = _find_dependency_files(list(parser.files.keys()))
    folder_tree = _summarize_folder_tree(codebase_data.get("file_tree", {}))
    project_summary = _build_project_summary(codebase_data)

    return {
        "repo_id": repo_id or hashlib.sha1(repo_path.encode("utf-8")).hexdigest()[:10],
        "project_summary": project_summary,
        "tech_stack": codebase_data.get("tech_stack", []),
        "folder_tree": folder_tree,
        "important_files": codebase_data.get("important_files", []),
        "entry_points": entry_points,
        "dependency_files": dependency_files,
        "repository_name": os.path.basename(repo_path),
        "repository_path": repo_path,
        "repository_info": {
            "total_files": codebase_data.get("total_files", 0),
            "project_type": codebase_data.get("project_type", "Unknown"),
            "tech_stack": codebase_data.get("tech_stack", []),
            "dependency_count": sum(
                len(v) for v in codebase_data.get("dependencies", {}).values()
            ),
        },
    }


def ingest_repository_to_qdrant(
    repo_path: str,
    collection_name: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    collection_name = collection_name or QDRANT_COLLECTION
    model = model or OPENAI_EMBEDDING_MODEL

    repo_context = build_repo_context(repo_path)
    chunks = chunk_repository(repo_path)
    if not chunks:
        raise ValueError(f"No eligible code files found under {repo_path}.")

    qdrant_client = get_qdrant_client(
        QDRANT_URL, QDRANT_API_KEY, check_compatibility=False
    )
    create_collection_if_not_exists(
        qdrant_client,
        collection_name=collection_name,
        vector_size=384,  # <--- Changed from '1536 if ...'
        distance=QDRANT_DISTANCE,
    )

    texts = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(texts, model)

    points = []
    for chunk, vector in zip(chunks, vectors):

        # Generate the valid UUID here
        valid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["id"]))

        payload = {
            "repo_id": repo_context["repo_id"],
            "chunk_id": chunk["chunk_id"],
            "path": chunk["path"],
            "filename": chunk["filename"],
            "language": chunk["language"],
            "chunk_index": chunk["chunk_index"],
            "line_range": chunk["line_range"],
            "content": chunk["content"],
        }
        points.append(
            {
                "id": valid_uuid,  # <--- Use the valid UUID instead of chunk['id']
                "vector": vector,
                "payload": payload,
            }
        )

    upsert_points(qdrant_client, collection_name=collection_name, points=points)

    return {
        "status": "success",
        "repo_id": repo_context["repo_id"],
        "collection_name": collection_name,
        "model": model,
        "ingested_points": len(points),
        "repo_summary": repo_context["project_summary"],
    }
