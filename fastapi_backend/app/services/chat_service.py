from os import path

import openai
from typing import Any, Dict, List, Optional

from app.core.config import OPENAI_API_KEY, OPENAI_LLM_MODEL
from app.services.embedding_service import semantic_search


def _configure_openai() -> None:
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set. Please add OPENAI_API_KEY to .env."
        )
    openai.api_key = OPENAI_API_KEY


def _build_chat_prompt(
    query: str, repo_context: Dict[str, Any], chunks: List[Dict[str, Any]]
) -> str:
    chunk_text_items = []
    for idx, hit in enumerate(chunks, start=1):
        payload = hit.get("payload", {})
        snippet = payload.get("content", "")
        path = payload.get("path", "<unknown>")
        clean_snippet = snippet[:400].replace("\n", " ")
        chunk_text_items.append(f"{idx}. Path: {path}\nSnippet: {clean_snippet}")

    chunk_text = (
        "\n\n".join(chunk_text_items)
        if chunk_text_items
        else "No relevant chunks were retrieved."
    )

    return (
        f"You are a codebase-aware assistant. Use only the retrieved repository chunks to answer the user query. "
        f"Do not make up any facts or claim to read files that are not included below.\n\n"
        f"Repository summary: {repo_context.get('project_summary', '')}\n"
        f"Folder tree: {repo_context.get('folder_tree', '')}\n"
        f"Entry points: {', '.join(repo_context.get('entry_points', []))}\n"
        f"Important files: {', '.join(repo_context.get('important_files', []))}\n\n"
        f"User question: {query}\n\n"
        f"Retrieved chunks:\n{chunk_text}\n\n"
        "Answer in a clear and concise manner based on the chunks. If the answer is not available, say so honestly."
    )


async def rag_chat(
    query: str,
    repo_context: Dict[str, Any],
    repo_id: Optional[str] = None,
    top_k: int = 8,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    _configure_openai()
    model = model or OPENAI_LLM_MODEL

    chunks = semantic_search(
        query,
        top_k=top_k,
        repo_id=repo_id,
    )

    prompt = _build_chat_prompt(query, repo_context, chunks)

    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert developer assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=700,
    )

    return {
        "query": query,
        "answer": response.choices[0].message.content.strip(),
        "retrieved_chunks": [
            {
                "path": hit.get("payload", {}).get("path"),
                "score": hit.get("score"),
                "snippet": hit.get("payload", {}).get("content", "")[:400],
            }
            for hit in chunks
        ],
    }
