from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AnalysisError(Exception):
    error_type: str
    message: str
    http_status: int = 500

    def to_response(self) -> Dict[str, Any]:
        return {
            "status": "error",
            "error_type": self.error_type,
            "message": self.message,
        }
