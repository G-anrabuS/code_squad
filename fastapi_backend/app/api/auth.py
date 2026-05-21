from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth
from app.core.config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
import httpx
from app.core.security import create_access_token
from fastapi.responses import RedirectResponse

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
async def github_login(request: Request, platform: str = "mobile"):
    redirect_uri = str(request.url_for("github_callback")) + f"?platform={platform}"
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback", name="github_callback")
async def github_callback(request: Request, platform: str = "mobile"):
    token = await oauth.github.authorize_access_token(request)
    access_token = token["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        user_res = await client.get("https://api.github.com/user", headers=headers)

    user = user_res.json()
    app_token = create_access_token(
        {"github_token": access_token, "github_username": user["login"]}
    )

    if platform == "web":
        redirect_url = (
            f"http://localhost:8080/auth.html?jwt={app_token}&username={user['login']}"
        )
    else:
        # Android / iOS behavior
        redirect_url = f"codesquad://callback?jwt={app_token}&username={user['login']}"

    return RedirectResponse(url=redirect_url)
