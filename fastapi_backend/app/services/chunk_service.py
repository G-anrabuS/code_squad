import ast
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    "build",
    "dist",
    ".idea",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".gradle",
    ".dart_tool",
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".dart",
    ".java",
    ".cpp",
    ".c",
    ".go",
    ".rs",
    ".kt",
    ".swift",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".json",
    ".md",
    ".xml",
    ".html",
    ".css",
}

MAX_FILE_SIZE = 5 * 1024 * 1024
DEFAULT_CHUNK_SIZE = 1200
DEFAULT_OVERLAP = 200


def is_code_file(path: Path) -> bool:
    return path.suffix.lower() in ALLOWED_EXTENSIONS


def should_ignore_dir(dir_name: str) -> bool:
    return dir_name.startswith(".") or dir_name in IGNORE_DIRS


def collect_code_files(repo_path: str) -> List[Path]:
    repo_root = Path(repo_path)
    collected: List[Path] = []

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if not should_ignore_dir(d)]

        for file_name in files:
            file_path = Path(root) / file_name
            if not is_code_file(file_path):
                continue

            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            collected.append(file_path)

    return sorted(collected)


def read_file_text(file_path: Path) -> str:
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def _extract_python_blocks(text: str) -> List[Dict[str, int | str]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    blocks: List[Dict[str, int | str]] = []
    lines = text.splitlines(keepends=True)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, "end_lineno", node.lineno) - 1
            blocks.append({
                "start": sum(len(line) for line in lines[:start]),
                "end": sum(len(line) for line in lines[:end + 1]),
                "content": "".join(lines[start:end + 1]).strip(),
            })

    return blocks


def _extract_js_ts_blocks(text: str) -> List[Dict[str, int | str]]:
    pattern = re.compile(
        r"^(?P<header>(?:export\s+)?(?:async\s+)?(?:function|class)\s+[A-Za-z0-9_]+|(?:const|let|var)\s+[A-Za-z0-9_]+\s*=\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z0-9_]+)\s*=>)|^\s*module\.exports\s*=|^\s*exports\.[A-Za-z0-9_]+\s*=",
        re.MULTILINE,
    )
    blocks: List[Dict[str, int | str]] = []
    positions = [match.start() for match in pattern.finditer(text)]

    if not positions:
        return []

    positions.append(len(text))
    for i in range(len(positions) - 1):
        start = positions[i]
        end = positions[i + 1]
        content = text[start:end].strip()
        if content:
            blocks.append({"start": start, "end": end, "content": content})

    return blocks


def _extract_config_blocks(text: str, suffix: str) -> List[Dict[str, int | str]]:
    blocks: List[Dict[str, int | str]] = []
    lines = text.splitlines(keepends=True)

    if suffix in {".yaml", ".yml"}:
        current = []
        current_key = None
        for line in lines:
            if re.match(r"^[A-Za-z0-9_.-]+:\s*", line):
                if current_key is not None:
                    blocks.append({
                        "start": sum(len(l) for l in lines[:lines.index(current[0])]),
                        "end": sum(len(l) for l in lines[:lines.index(current[-1]) + 1]),
                        "content": "".join(current).strip(),
                    })
                current = [line]
                current_key = line.strip().split(":")[0]
            elif current is not None:
                current.append(line)
        if current:
            blocks.append({"start": 0, "end": sum(len(l) for l in lines), "content": "".join(current).strip()})
    elif suffix == ".toml":
        for match in re.finditer(r"^\[([^\]]+)\]", text, re.MULTILINE):
            start = match.start()
            next_match = re.search(r"^\[([^\]]+)\]", text[match.end():], re.MULTILINE)
            end = len(text) if not next_match else match.end() + next_match.start()
            blocks.append({"start": start, "end": end, "content": text[start:end].strip()})
    elif suffix == ".ini":
        for match in re.finditer(r"^\[([^\]]+)\]", text, re.MULTILINE):
            start = match.start()
            next_match = re.search(r"^\[([^\]]+)\]", text[match.end():], re.MULTILINE)
            end = len(text) if not next_match else match.end() + next_match.start()
            blocks.append({"start": start, "end": end, "content": text[start:end].strip()})
    elif suffix == ".json":
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                offset = 0
                for key in parsed.keys():
                    key_pattern = re.compile(rf'"{re.escape(key)}"\s*:\s*')
                    match = key_pattern.search(text, offset)
                    if match:
                        start = match.start()
                        next_match = key_pattern.search(text, match.end())
                        end = len(text) if not next_match else next_match.start()
                        blocks.append({"start": start, "end": end, "content": text[start:end].strip()})
                        offset = end
        except json.JSONDecodeError:
            pass

    return blocks


def _extract_logical_chunks(file_path: Path, content: str) -> List[Dict[str, int | str]]:
    suffix = file_path.suffix.lower()
    if suffix == ".py":
        blocks = _extract_python_blocks(content)
    elif suffix in {".js", ".ts", ".tsx", ".jsx"}:
        blocks = _extract_js_ts_blocks(content)
    elif suffix in {".yaml", ".yml", ".toml", ".ini", ".json"}:
        blocks = _extract_config_blocks(content, suffix)
    else:
        blocks = []

    if blocks:
        return blocks

    if len(content) <= DEFAULT_CHUNK_SIZE:
        return [{"start": 0, "end": len(content), "content": content.strip()}]

    return split_text_into_chunks(content)


def split_text_into_chunks(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> List[Dict[str, int | str]]:
    if not text:
        return []

    text = text.strip()
    if len(text) <= chunk_size:
        return [{"start": 0, "end": len(text), "content": text}]

    chunks: List[Dict[str, int | str]] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = text[start:end]

        if end < text_length:
            split_at = chunk_text.rfind("\n")
            if split_at > chunk_size // 2:
                end = start + split_at
            else:
                split_at = chunk_text.rfind(" ")
                if split_at > chunk_size // 2:
                    end = start + split_at

        chunk_text = text[start:end].strip()
        chunks.append({
            "start": start,
            "end": end,
            "content": chunk_text,
        })

        if end >= text_length:
            break

        start = max(0, end - overlap)

    return chunks


def chunk_repository(repo_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> List[Dict[str, str | int]]:
    repo_root = Path(repo_path)
    chunks: List[Dict[str, str | int]] = []

    for file_path in collect_code_files(repo_path):
        relative_path = str(file_path.relative_to(repo_root))
        content = read_file_text(file_path)
        if not content.strip():
            continue

        file_blocks = _extract_logical_chunks(file_path, content)

        if not file_blocks:
            continue

        for index, block in enumerate(file_blocks):
            start = block["start"]
            end = block["end"]
            chunk_text = block["content"].strip()
            if not chunk_text:
                continue

            start_line = content[:start].count("\n") + 1
            end_line = content[:end].count("\n") + 1
            chunks.append({
                "id": f"{relative_path}:{index}",
                "chunk_id": f"{relative_path}:{index}",
                "path": relative_path,
                "filename": file_path.name,
                "language": file_path.suffix.lower().lstrip('.'),
                "chunk_index": index,
                "line_range": f"{start_line}-{end_line}",
                "content": chunk_text,
            })

    return chunks
