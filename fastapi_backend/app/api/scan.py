from fastapi import APIRouter, Request
from app.services.clone_service import clone_repo

router = APIRouter()


@router.post("/repo")
async def scan_repo(payload: dict, request: Request):
    token = request.session.get("github_token")
    username = request.session.get("github_username")

    if not token:
        return {"error": "Not authenticated"}

    repo_name = payload["repo_name"]
    branch = payload["branch"]

    repo_path = clone_repo(
        username=username, repo_name=repo_name, token=token, branch=branch
    )

    return {"message": "Repo cloned successfully", "repo_path": repo_path}
