import json
import logging
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY
from app.services.analysis_errors import AnalysisError

# Gemini 1.5 Flash is incredibly fast, free-tier friendly, and perfect for large contexts
DEFAULT_MODEL = "gemini-3.1-flash-lite"
logger = logging.getLogger(__name__)


def _get_gemini_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please add GEMINI_API_KEY to .env."
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def _extract_json_payload(text: str) -> Dict[str, Any]:
    if not text:
        raise AnalysisError(
            error_type="parsing_error",
            message="Gemini returned an empty response.",
            http_status=502,
        )

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
        raise AnalysisError(
            error_type="parsing_error",
            message="Gemini response did not contain a JSON object.",
            http_status=502,
        )

    # Ensure we only parse the actual JSON object
    start = candidate.index("{")
    end = candidate.rindex("}") + 1
    candidate = candidate[start:end]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        raise AnalysisError(
            error_type="parsing_error",
            message="Failed to parse Gemini response as JSON.",
            http_status=502,
        )


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


def _normalize_gemini_error(exc: Exception) -> AnalysisError:
    message = str(exc).lower()
    logger.warning("Gemini request failed: %s", exc)

    if isinstance(exc, AnalysisError):
        return exc

    if isinstance(exc, ValueError) and "GEMINI_API_KEY is not set" in str(exc):
        return AnalysisError(
            error_type="invalid_api_key",
            message="Gemini API key is missing or invalid.",
            http_status=401,
        )

    if "429" in message or "resource_exhausted" in message or "quota" in message:
        return AnalysisError(
            error_type="quota_exceeded",
            message="Gemini API quota exceeded. Please try again later.",
            http_status=429,
        )

    if "api key" in message or "authentication" in message or "permission denied" in message or "unauthorized" in message or "403" in message or "401" in message:
        return AnalysisError(
            error_type="invalid_api_key",
            message="Gemini API key is invalid or unauthorized.",
            http_status=401,
        )

    if "timeout" in message or "timed out" in message or "deadline" in message:
        return AnalysisError(
            error_type="timeout",
            message="Gemini API request timed out.",
            http_status=504,
        )

    if "connection" in message or "network" in message or "dns" in message or "unreachable" in message or "socket" in message:
        return AnalysisError(
            error_type="network_error",
            message="Network error while contacting Gemini API.",
            http_status=503,
        )

    return AnalysisError(
        error_type="agent_failure",
        message="Gemini analysis failed unexpectedly.",
        http_status=502,
    )


async def analyze_agent(
    agent_name: str,
    repo_context: Dict[str, Any],
    chunks: List[Dict[str, Any]],
    model: Optional[str] = None,
) -> Dict[str, Any]:
    try:
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
                response_mime_type="application/json",
            ),
        )

        return _extract_json_payload(response.text)
    except Exception as exc:
        raise _normalize_gemini_error(exc) from None
