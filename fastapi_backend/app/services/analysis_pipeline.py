"""
Analysis Pipeline - wrapper for the modern repository analysis pipeline.
"""
from typing import Any

from app.pipelines.codebase_analysis_pipeline import CodebaseAnalysisPipeline


async def run_full_analysis(repo_path: str) -> Any:
    pipeline = CodebaseAnalysisPipeline()
    return await pipeline.analyze_repository(repo_path)
