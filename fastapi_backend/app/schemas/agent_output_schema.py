from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AgentOutput(BaseModel):
    agent_name: str
    summary: str
    findings: Dict[str, Any]
    recommendations: List[str]
    insights: Dict[str, Any]
    severity: Optional[str] = None
    analysis_details: Optional[Dict[str, Any]] = None


class SummaryReview(AgentOutput):
    pass


class JudgeReview(AgentOutput):
    pass


class ArchitectReview(AgentOutput):
    pass


class PerformanceReview(AgentOutput):
    pass


class SecurityReview(AgentOutput):
    pass
