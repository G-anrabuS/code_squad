"""
Base Agent - Abstract base class for all analysis agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Standard response structure for agents."""
    agent_name: str
    findings: Dict[str, Any]
    summary: str
    severity: Optional[str] = None  # for security/performance agents
    recommendations: List[str] = []


class BaseAnalysisAgent(ABC):
    """Base class for all codebase analysis agents."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        
    @abstractmethod
    async def analyze(self, codebase_data: Dict[str, Any]) -> AgentResponse:
        """
        Analyze codebase and return findings.
        
        Args:
            codebase_data: Dictionary containing parsed codebase information
            
        Returns:
            AgentResponse with findings
        """
        pass
    
    def format_findings(self, findings: Dict[str, Any], summary: str, 
                       recommendations: list = None, severity: str = None) -> AgentResponse:
        """Format findings into standard response."""
        return AgentResponse(
            agent_name=self.agent_name,
            findings=findings,
            summary=summary,
            severity=severity,
            recommendations=recommendations or []
        )
