import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from app.schemas.agent_output_schema import (
    AgentFailure,
    AgentOutput,
    ArchitectReview,
    JudgeReview,
    PerformanceReview,
    SecurityReview,
    SummaryReview,
)
from app.schemas.report_schema import FinalAnalysisReport
from app.services.analysis_errors import AnalysisError
from app.services.llm_service import analyze_agent
from app.services.qdrant_service import build_repo_context, ingest_repository_to_qdrant
from app.services.retriever_service import retrieve_agent_chunks

AGENT_MODEL_MAP = {
    "summary": "gemini-3.1-flash-lite",
    "judge": "gemini-3.1-flash-lite",
    "architect": "gemini-3.1-flash-lite",
    "performance": "gemini-3.1-flash-lite",
    "security": "gemini-3.1-flash-lite",
}

AGENT_NAMES = ["summary", "judge", "architect", "performance", "security"]
logger = logging.getLogger(__name__)


class CodebaseAnalysisPipeline:
    """Pipeline orchestrating repository analysis using Qdrant and Gemini."""

    async def analyze_repository(
        self,
        repo_path: str,
        progress_callback: Optional[Callable[[str, str, Optional[str]], None]] = None,
    ) -> FinalAnalysisReport:
        if progress_callback:
            progress_callback("scan", "running", None)

        try:
            repo_context = build_repo_context(repo_path)
            ingestion_summary = ingest_repository_to_qdrant(repo_path)
        except Exception:
            if progress_callback:
                progress_callback(
                    "scan",
                    "failed",
                    "Failed to prepare repository context for analysis.",
                )
            raise AnalysisError(
                error_type="unknown_error",
                message="Failed to prepare repository context for analysis.",
                http_status=500,
            ) from None
        if progress_callback:
            progress_callback("scan", "completed", None)

        analysis_tasks = [
            asyncio.create_task(
                self._run_agent(agent_name, repo_context, progress_callback)
            )
            for agent_name in AGENT_NAMES
        ]
        results = await asyncio.gather(*analysis_tasks, return_exceptions=False)

        agent_outputs = {result["agent_name"]: result["result"] for result in results}
        if all(result["status"] == "error" for result in results):
            first_error = next(
                (
                    result["result"]
                    for result in results
                    if isinstance(result["result"], dict)
                ),
                {},
            )
            raise AnalysisError(
                error_type="analysis_failed",
                message="All analysis agents failed.",
                http_status=502,
            ) from None

        return self._build_final_report(repo_context, agent_outputs, ingestion_summary)

    async def _run_agent(
        self,
        agent_name: str,
        repo_context: Dict[str, Any],
        progress_callback: Optional[Callable[[str, str, Optional[str]], None]] = None,
    ) -> Dict[str, Any]:
        label = agent_name.upper()
        logger.info("[%s] started", label)
        if progress_callback:
            progress_callback(agent_name, "running", None)

        try:
            chunks = retrieve_agent_chunks(agent_name, repo_context, top_k=6)
            result = await analyze_agent(
                agent_name=agent_name,
                repo_context=repo_context,
                chunks=chunks,
                model=AGENT_MODEL_MAP.get(agent_name),
            )
            logger.info("[%s] success", label)
            if progress_callback:
                progress_callback(agent_name, "completed", None)
            return {"agent_name": agent_name, "status": "success", "result": result}
        except AnalysisError as exc:
            logger.warning("[%s] failed: %s", label, exc.message)
            if progress_callback:
                progress_callback(agent_name, "failed", exc.message)
            return {
                "agent_name": agent_name,
                "status": "error",
                "result": {
                    "status": "error",
                    "error_type": exc.error_type,
                    "message": exc.message,
                    "agent_name": agent_name,
                },
            }
        except Exception:
            logger.exception("[%s] failed: unknown error", label)
            if progress_callback:
                progress_callback(
                    agent_name,
                    "failed",
                    f"Gemini analysis failed for {agent_name}.",
                )
            return {
                "agent_name": agent_name,
                "status": "error",
                "result": {
                    "status": "error",
                    "error_type": "unknown_error",
                    "message": f"Gemini analysis failed for {agent_name}.",
                    "agent_name": agent_name,
                },
            }

    def _build_agent_review(
        self,
        agent_name: str,
        data: Dict[str, Any],
        review_model: Any,
    ) -> Any:
        if data.get("status") == "error":
            return AgentFailure(
                agent_name=agent_name,
                message=data.get("message", f"{agent_name} analysis failed."),
                error_type=data.get("error_type", "agent_failure"),
            )

        return review_model.model_validate(
            {
                "agent_name": agent_name,
                "summary": data.get("summary", ""),
                "findings": data.get("findings", {}),
                "recommendations": data.get("recommendations", []),
                "insights": data.get("insights", {}),
                "severity": data.get("severity"),
                "analysis_details": data.get("analysis_details"),
            }
        )

    def _build_final_report(
        self,
        repo_context: Dict[str, Any],
        agent_outputs: Dict[str, Dict[str, Any]],
        ingestion_summary: Dict[str, Any],
    ) -> FinalAnalysisReport:
        summary_data = agent_outputs.get("summary", {})
        judge_data = agent_outputs.get("judge", {})
        architect_data = agent_outputs.get("architect", {})
        performance_data = agent_outputs.get("performance", {})
        security_data = agent_outputs.get("security", {})

        summary_review = self._build_agent_review(
            "summary",
            summary_data,
            SummaryReview,
        )

        judge_review = self._build_agent_review(
            "judge",
            judge_data,
            JudgeReview,
        )

        architect_review = self._build_agent_review(
            "architect",
            architect_data,
            ArchitectReview,
        )

        performance_review = self._build_agent_review(
            "performance",
            performance_data,
            PerformanceReview,
        )

        security_review = self._build_agent_review(
            "security",
            security_data,
            SecurityReview,
        )

        priority_fixes = []
        if isinstance(judge_review, AgentOutput):
            priority_fixes.extend(judge_review.recommendations[:3])
        if isinstance(performance_review, AgentOutput):
            priority_fixes.extend(performance_review.recommendations[:3])
        if isinstance(security_review, AgentOutput):
            priority_fixes.extend(security_review.recommendations[:3])
        priority_fixes = [fix for fix in priority_fixes if fix]

        final_recommendations = []
        for review in [
            summary_review,
            architect_review,
            judge_review,
            performance_review,
            security_review,
        ]:
            if isinstance(review, AgentOutput):
                final_recommendations.extend(review.recommendations[:2])
        final_recommendations = [rec for rec in final_recommendations if rec]

        severity_scores = {
            "low": 90,
            "medium": 70,
            "high": 45,
            "critical": 20,
        }

        scores = []

        for review in [
            summary_review,
            judge_review,
            architect_review,
            performance_review,
            security_review,
        ]:
            if isinstance(review, AgentOutput):
                score = review.findings.get("code_quality_score")

                if isinstance(score, (int, float)):
                    scores.append(float(score))
                else:
                    severity = str(review.severity).lower()
                    if severity in severity_scores:
                        scores.append(severity_scores[severity])

        overall_score = sum(scores) / len(scores) if scores else 70.0

        return FinalAnalysisReport(
            repo_id=repo_context.get("repo_id", ""),
            timestamp=datetime.now().isoformat(),
            repository_info=repo_context.get("repository_info", {}),
            repo_context={
                "project_summary": repo_context.get("project_summary", ""),
                "tech_stack": repo_context.get("tech_stack", []),
                "folder_tree": repo_context.get("folder_tree", ""),
                "important_files": repo_context.get("important_files", []),
                "entry_points": repo_context.get("entry_points", []),
                "dependency_files": repo_context.get("dependency_files", []),
                "ingestion_summary": ingestion_summary,
            },
            overall_score=overall_score,
            summary=summary_review,
            judge_review=judge_review,
            architecture_review=architect_review,
            performance_review=performance_review,
            security_review=security_review,
            priority_fixes=priority_fixes,
            improved_architecture=(
                architect_review.findings.get("improved_architecture", {})
                if isinstance(architect_review, AgentOutput)
                else {}
            ),
            final_recommendations=final_recommendations,
        )
