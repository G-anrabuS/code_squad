import asyncio
import json
import re
from typing import Any, Dict, List, Optional

import openai

from app.agents.base_agent import AgentResponse, BaseAnalysisAgent
from app.core.config import OPENAI_API_KEY, OPENAI_LLM_MODEL
from app.services.embedding_service import semantic_search


def _configure_openai() -> None:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set. Please add OPENAI_API_KEY to .env.")

    openai.api_key = OPENAI_API_KEY


def _extract_json_payload(text: str) -> Dict[str, Any]:
    """Extract the first JSON object from model output."""
    json_text = text.strip()
    match = re.search(r"\{.*\}", json_text, re.S)
    if not match:
        raise ValueError("LLM response did not contain valid JSON payload.")

    candidate = match.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse LLM JSON payload: {exc}\nText:\n{candidate}")


class LLMWrapperAgent(BaseAnalysisAgent):
    """Wraps an existing agent and makes the LLM the primary brain for structured analysis."""

    def __init__(self, inner_agent: BaseAnalysisAgent, llm_model: str = OPENAI_LLM_MODEL):
        super().__init__(inner_agent.agent_name)
        self.inner_agent = inner_agent
        self.llm_model = llm_model

    async def analyze(self, codebase_data: Dict[str, Any]) -> AgentResponse:
        retrieval_results = await self._retrieve_relevant_context(codebase_data)
        prompt = self._build_prompt(codebase_data, retrieval_results)

        llm_result = await self._call_llm(prompt)
        parsed = _extract_json_payload(llm_result)

        if not isinstance(parsed, dict):
            raise ValueError("LLM returned invalid JSON payload.")

        findings = parsed.get("findings", {})
        summary = parsed.get("summary", "")
        recommendations = parsed.get("recommendations", [])
        severity = parsed.get("severity", None)

        return self.format_findings(
            findings,
            summary,
            recommendations=recommendations,
            severity=severity,
        )

    def _build_prompt(
        self,
        codebase_data: Dict[str, Any],
        retrieval_results: List[Dict[str, Any]],
    ) -> str:
        metadata = {
            "total_files": codebase_data.get("total_files"),
            "project_type": codebase_data.get("project_type"),
            "tech_stack": codebase_data.get("tech_stack"),
            "important_files": codebase_data.get("important_files"),
            "dependencies": codebase_data.get("dependencies"),
        }

        retrieved_context = "No retrieval results available."
        if retrieval_results:
            retrieved_context = "Retrieved Qdrant semantic context:\n"
            for idx, result in enumerate(retrieval_results, start=1):
                payload = result.get("payload", {})
                snippet = payload.get("content") or payload.get("filename") or "<no content>"
                score = result.get("score")
                score_text = f"{score:.4f}" if isinstance(score, (float, int)) else "n/a"
                retrieved_context += (
                    f"{idx}. score={score_text}, path={payload.get('path')}\n"
                    f"   snippet: {snippet[:300]}\n"
                )

        return (
            "You are the Gemini LLM and the only analysis brain for this task. "
            f"Your role is '{self.agent_name}'. Use the retrieved Qdrant code context to inform your results. "
            "Produce valid JSON only with no markdown, explanation, or commentary outside the JSON object. "
            "The output JSON must include the fields: summary (string), findings (object), recommendations (array of strings), insights (object). "
            "Optionally include severity (string) and analysis_details (object).\n\n"
            "Retrieved context:\n"
            f"{retrieved_context}\n\n"
            "Repository metadata:\n"
            f"{json.dumps(metadata, indent=2, default=str)}\n\n"
            "Instructions:\n"
            "1. Analyze the retrieved code chunks from Qdrant and generate the final structured response.\n"
            "2. Do not return heuristic or fallback results; the output must be from LLM reasoning only.\n"
            "3. Keep the summary concise and targeted for the agent role.\n"
            "4. Use findings to capture the core analysis, and recommendations to capture next steps.\n"
            "5. Include insights that clarify risks, opportunities, and important observations.\n"
        )

    async def _retrieve_relevant_context(
        self, codebase_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Perform semantic retrieval from Qdrant to enrich the prompt context."""
        query_parts = [self.agent_name]
        if codebase_data.get("project_type"):
            query_parts.append(codebase_data["project_type"])
        if codebase_data.get("tech_stack"):
            query_parts.append(" ".join(codebase_data["tech_stack"]))
        if codebase_data.get("important_files"):
            query_parts.append(" ".join(codebase_data["important_files"][:10]))

        query = "\n".join(part for part in query_parts if part)

        try:
            return await asyncio.to_thread(semantic_search, query, 5)
        except Exception:
            return []

    async def _call_llm(self, prompt: str) -> str:
        _configure_openai()

        response = await openai.ChatCompletion.acreate(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "You are an expert software engineering reviewer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=800,
        )

        return response.choices[0].message.content
