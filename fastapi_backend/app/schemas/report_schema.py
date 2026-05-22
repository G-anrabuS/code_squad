from typing import Any, Dict, List, Union
from pydantic import BaseModel

from app.schemas.agent_output_schema import (
    AgentFailure,
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
    summary: Union[SummaryReview, AgentFailure]
    judge_review: Union[JudgeReview, AgentFailure]
    architecture_review: Union[ArchitectReview, AgentFailure]
    performance_review: Union[PerformanceReview, AgentFailure]
    security_review: Union[SecurityReview, AgentFailure]
    priority_fixes: List[str]
    improved_architecture: Dict[str, Any]
    final_recommendations: List[str]
