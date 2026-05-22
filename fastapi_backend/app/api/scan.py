from fastapi import APIRouter, Depends, HTTPException

from app.core.auth_dependency import get_current_user
from app.models.scan import ScanRepoRequest
from app.services.clone_service import clone_repo, clone_repo_from_url
from app.services.parser_service import get_relevant_files

router = APIRouter()


@router.post("/repo")
async def scan_repo(payload: ScanRepoRequest, user=Depends(get_current_user)):
    repo_url = payload.repo_url
    branch = payload.branch

    if repo_url:
        repo_path = clone_repo_from_url(repo_url=repo_url, branch=branch)
    else:
        if not payload.repo_name:
            raise HTTPException(status_code=400, detail="repo_name is required.")

        full_repo_name = payload.repo_name

        if "/" in full_repo_name:
            owner, repo = full_repo_name.split("/", 1)
        else:
            owner = user["github_username"]
            repo = full_repo_name

        repo_path = clone_repo(
            username=owner,
            repo_name=repo,
            token=user["github_token"],
            branch=branch,
        )

    if not repo_path:
        raise HTTPException(status_code=400, detail="Unable to clone repository.")

    files = get_relevant_files(repo_path)

    return {
        "repo_path": repo_path,
        "file_count": len(files),
        "files": files[:20],
    }
