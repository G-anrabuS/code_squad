from typing import Any, Dict, List
from pydantic import BaseModel

from app.schemas.agent_output_schema import (
    ArchitectReview,
    JudgeReview,
    PerformanceReview,
    SecurityReview,
    SummaryReview,
)


class FinalAnalysisReport(BaseModel):
    repo_id: str
    timestamp: str
    repository_info: Dict[str, Any]
    repo_context: Dict[str, Any]
    overall_score: float
    summary: SummaryReview
    judge_review: JudgeReview
    architecture_review: ArchitectReview
    performance_review: PerformanceReview
    security_review: SecurityReview
    priority_fixes: List[str]
    improved_architecture: Dict[str, Any]
    final_recommendations: List[str]
