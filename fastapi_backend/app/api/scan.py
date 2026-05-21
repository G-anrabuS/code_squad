from fastapi import APIRouter, Depends
from app.core.auth_dependency import get_current_user
from app.services.clone_service import clone_repo
from app.services.parser_service import get_relevant_files

router = APIRouter()


@router.post("/repo")
async def scan_repo(payload: dict, user=Depends(get_current_user)):
    repo_path = clone_repo(
        username=user["github_username"],
        repo_name=payload["repo_name"],
        token=user["github_token"],
        branch=payload["branch"],
    )

    files = get_relevant_files(repo_path)

    return {"repo_path": repo_path, "file_count": len(files), "files": files[:20]}
