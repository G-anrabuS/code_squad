from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth
from app.core.config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

import httpx

router = APIRouter()

oauth = OAuth()

oauth.register(
    name="github",
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user repo"},
)


@router.get("/github/login")
async def github_login(request: Request):
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback", name="github_callback")
async def github_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)

    access_token = token["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        user_res = await client.get("https://api.github.com/user", headers=headers)

        repos_res = await client.get(
            "https://api.github.com/user/repos", headers=headers
        )

    user = user_res.json()

    request.session["github_token"] = access_token
    request.session["github_username"] = user["login"]

    return {"user": user, "repos": repos_res.json()}
