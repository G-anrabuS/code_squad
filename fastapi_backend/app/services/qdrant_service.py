import hashlib
import os
from typing import Any, Dict, List, Optional

from app.services.codebase_parser import CodebaseParser

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


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def _summarize_folder_tree(
    tree: Dict[str, Any],
    max_children: int = 5,
) -> str:
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


def build_repo_context(
    repo_path: str,
    repo_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build repository metadata context for analysis agents.
    """
    parser = CodebaseParser(repo_path)
    codebase_data = parser.parse()

    file_paths = list(parser.files.keys())

    generated_repo_id = (
        repo_id or hashlib.sha1(repo_path.encode("utf-8")).hexdigest()[:10]
    )

    return {
        "repo_id": generated_repo_id,
        "project_summary": _build_project_summary(codebase_data),
        "tech_stack": codebase_data.get("tech_stack", []),
        "folder_tree": _summarize_folder_tree(codebase_data.get("file_tree", {})),
        "important_files": codebase_data.get("important_files", []),
        "entry_points": _find_entry_points(file_paths),
        "dependency_files": _find_dependency_files(file_paths),
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
