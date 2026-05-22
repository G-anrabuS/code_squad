from typing import Optional

from pydantic import BaseModel


class ScanRepoRequest(BaseModel):
    repo_name: Optional[str] = None
    repo_url: Optional[str] = None
    branch: str = "main"
