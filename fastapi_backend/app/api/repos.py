from fastapi import APIRouter, Depends, HTTPException
from app.core.auth_dependency import get_current_user
import httpx

router = APIRouter()


@router.get("/repos")
async def get_repos(user=Depends(get_current_user)):
    headers = {"Authorization": f"Bearer {user['github_token']}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.github.com/user/repos",
            headers=headers,
        )

    if res.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch repositories",
        )

    repos = res.json()

    return [
        {
            "name": repo["name"],
            "full_name": repo["full_name"],
            "private": repo["private"],
        }
        for repo in repos
    ]


@router.get("/branches/{full_repo_name:path}")
async def get_branches(
    full_repo_name: str,
    user=Depends(get_current_user),
):
    headers = {"Authorization": f"Bearer {user['github_token']}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api.github.com/repos/{full_repo_name}/branches",
            headers=headers,
        )

    if res.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch branches",
        )

    branches = res.json()

    return [branch["name"] for branch in branches]
