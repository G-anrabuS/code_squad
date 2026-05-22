"""
Analysis Pipeline - wrapper for the modern repository analysis pipeline.
"""
from typing import Any, Callable, Optional

from app.pipelines.codebase_analysis_pipeline import CodebaseAnalysisPipeline


async def run_full_analysis(
    repo_path: str,
    progress_callback: Optional[Callable[[str, str, Optional[str]], None]] = None,
) -> Any:
    pipeline = CodebaseAnalysisPipeline()
    return await pipeline.analyze_repository(
        repo_path,
        progress_callback=progress_callback,
    )
