from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    agent_name: str
    summary: str
    findings: Dict[str, Any]
    recommendations: List[str]
    insights: Dict[str, Any]
    severity: Optional[str] = None
    analysis_details: Optional[Dict[str, Any]] = None


class AgentFailure(BaseModel):
    status: str = "error"
    message: str
    error_type: str = "agent_failure"
    agent_name: str


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
