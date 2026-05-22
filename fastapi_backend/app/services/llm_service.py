import json
from typing import Any, Dict, List, Optional

import openai

from app.core.config import OPENAI_API_KEY, OPENAI_LLM_MODEL


def _configure_openai() -> None:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set. Please add OPENAI_API_KEY to .env.")
    openai.api_key = OPENAI_API_KEY


def _extract_json_payload(text: str) -> Dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith('```'):
        candidate = candidate.strip('`')

    if '{' not in candidate:
        raise ValueError('LLM response did not contain a JSON object.')

    start = candidate.index('{')
    candidate = candidate[start:]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse LLM response as JSON: {exc}\n{candidate}")


def _chunk_list(chunks: List[Dict[str, Any]]) -> str:
    if not chunks:
        return 'No chunks were retrieved from Qdrant.'

    chunk_texts = []
    for idx, chunk in enumerate(chunks, start=1):
        payload = chunk.get('payload', {})
        path = payload.get('path', '<unknown>')
        snippet = payload.get('content', '')
        snippet_preview = snippet[:500].replace('\n', ' ').strip()
        chunk_texts.append(f"{idx}. path={path}\nsnippet={snippet_preview}")
    return '\n\n'.join(chunk_texts)


async def analyze_agent(
    agent_name: str,
    repo_context: Dict[str, Any],
    chunks: List[Dict[str, Any]],
    model: Optional[str] = None,
) -> Dict[str, Any]:
    _configure_openai()
    model = model or OPENAI_LLM_MODEL

    system_prompt = (
        "You are a software analysis specialist. You MUST return a single JSON object only. "
        "Do not add any explanation, markdown, or text outside the JSON object."
    )

    user_prompt = (
        f"Agent: {agent_name}\n"
        f"Repository summary: {repo_context.get('project_summary', '')}\n"
        f"Tech stack: {', '.join(repo_context.get('tech_stack', []))}\n"
        f"Folder tree: {repo_context.get('folder_tree', '')}\n"
        f"Entry points: {', '.join(repo_context.get('entry_points', []))}\n"
        f"Important files: {', '.join(repo_context.get('important_files', []))}\n"
        f"Dependency files: {', '.join(repo_context.get('dependency_files', []))}\n"
        "Use only the retrieved code chunks from Qdrant below to answer. "
        "Do not analyze the full repository directly."
        "\n\nRetrieved chunks:\n"
        f"{_chunk_list(chunks)}\n\n"
        "Return strict JSON with the fields: summary (string), findings (object), recommendations (array), insights (object). "
        "Optionally include severity (string) and analysis_details (object)."
    )

    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=900,
    )

    return _extract_json_payload(response.choices[0].message.content)
