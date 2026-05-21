from fastapi import APIRouter, Request
from app.services.clone_service import clone_repo
from app.services.parser_service import get_relevant_files

router = APIRouter()


@router.post("/repo")
async def scan_repo(payload: dict, request: Request):
    token = request.session.get("github_token")
    username = request.session.get("github_username")

    repo_name = payload["repo_name"]
    branch = payload["branch"]

    repo_path = clone_repo(
        username=username, repo_name=repo_name, token=token, branch=branch
    )

    files = get_relevant_files(repo_path)

    return {"repo_path": repo_path, "file_count": len(files), "files": files[:20]}
