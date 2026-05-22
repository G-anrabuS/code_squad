"""
Analysis Pipeline - wrapper for the modern repository analysis pipeline.
"""
import asyncio
from typing import Any, Dict

from app.pipelines.codebase_analysis_pipeline import CodebaseAnalysisPipeline


async def run_full_analysis(repo_path: str) -> Any:
    pipeline = CodebaseAnalysisPipeline()
    return await pipeline.analyze_repository(repo_path)


async def run_analysis_export(repo_path: str, format_type: str = 'json') -> Dict[str, Any]:
    report = await run_full_analysis(repo_path)
    if format_type == 'markdown':
        return {'markdown': _render_markdown(report)}
    return report.dict()


def _render_markdown(report: Any) -> str:
    summary = report.summary
    markdown = [
        "# Repository Analysis Report",
        "",
        "## Summary",
        summary.summary,
        "",
        "### Top Recommendations",
    ]
    markdown.extend(f"- {rec}" for rec in summary.recommendations[:5])
    markdown.extend([
        "",
        "## Security Review",
        report.security_review.summary,
        "",
        "## Performance Review",
        report.performance_review.summary,
        "",
        "## Architecture Review",
        report.architecture_review.summary,
        "",
        "## Priority Fixes",
    ])
    markdown.extend(f"- {fix}" for fix in report.priority_fixes)
    return "\n".join(markdown)
