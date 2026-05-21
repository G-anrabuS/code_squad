from fastapi import APIRouter, Request
import httpx

router = APIRouter()


@router.get("/branches/{repo_name}")
async def get_branches(repo_name: str, request: Request):
    token = request.session.get("github_token")

    if not token:
        return {"error": "Not authenticated"}

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api.github.com/repos/{request.session['github_username']}/{repo_name}/branches",
            headers=headers,
        )

    branches = res.json()

    return [branch["name"] for branch in branches]
