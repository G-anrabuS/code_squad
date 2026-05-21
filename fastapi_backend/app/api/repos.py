from fastapi import APIRouter, Depends
from app.core.auth_dependency import get_current_user
import httpx

router = APIRouter()


@router.get("/repos")
async def get_repos(user=Depends(get_current_user)):
    headers = {"Authorization": f"Bearer {user['github_token']}"}

    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.github.com/user/repos", headers=headers)

    repos = res.json()

    return [{"name": repo["name"], "private": repo["private"]} for repo in repos]


@router.get("/branches/{repo_name}")
async def get_branches(repo_name: str, user=Depends(get_current_user)):
    headers = {"Authorization": f"Bearer {user['github_token']}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api.github.com/repos/{user['github_username']}/{repo_name}/branches",
            headers=headers,
        )

    return [branch["name"] for branch in res.json()]
