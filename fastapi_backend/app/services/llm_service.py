import json
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY

# Gemini 1.5 Flash is incredibly fast, free-tier friendly, and perfect for large contexts
DEFAULT_MODEL = "gemini-3.1-flash-lite"


def _get_gemini_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please add GEMINI_API_KEY to .env."
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def _extract_json_payload(text: str) -> Dict[str, Any]:
    candidate = text.strip()

    # Clean up any potential markdown code blocks
    if candidate.startswith("```json"):
        candidate = candidate[7:]
    elif candidate.startswith("```"):
        candidate = candidate[3:]

    if candidate.endswith("```"):
        candidate = candidate[:-3]

    candidate = candidate.strip()

    if "{" not in candidate:
        raise ValueError("LLM response did not contain a JSON object.")

    # Ensure we only parse the actual JSON object
    start = candidate.index("{")
    end = candidate.rindex("}") + 1
    candidate = candidate[start:end]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse LLM response as JSON: {exc}\n{candidate}")


def _chunk_list(chunks: List[Dict[str, Any]]) -> str:
    if not chunks:
        return "No chunks were retrieved from Qdrant."

    chunk_texts = []
    for idx, chunk in enumerate(chunks, start=1):
        payload = chunk.get("payload", {})
        path = payload.get("path", "<unknown>")
        snippet = payload.get("content", "")
        snippet_preview = snippet[:500].replace("\n", " ").strip()
        chunk_texts.append(f"{idx}. path={path}\nsnippet={snippet_preview}")
    return "\n\n".join(chunk_texts)


async def analyze_agent(
    agent_name: str,
    repo_context: Dict[str, Any],
    chunks: List[Dict[str, Any]],
    model: Optional[str] = None,
) -> Dict[str, Any]:
    client = _get_gemini_client()
    model_name = model or DEFAULT_MODEL

    system_instruction = (
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

    response = await client.aio.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            response_mime_type="application/json",  # Forces Gemini to return valid JSON
        ),
    )

    return _extract_json_payload(response.text)
