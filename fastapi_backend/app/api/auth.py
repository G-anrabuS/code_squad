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


# 1. Accept the web_origin parameter
@router.get("/github/login")
async def github_login(
    request: Request, platform: str = "mobile", web_origin: str = None
):
    # Pass BOTH parameters to the callback using Starlette's safe query builder
    redirect_uri = str(
        request.url_for("github_callback").include_query_params(
            platform=platform, web_origin=web_origin
        )
    )
    return await oauth.github.authorize_redirect(request, redirect_uri)


# 2. Receive the web_origin in the callback
@router.get("/github/callback", name="github_callback")
async def github_callback(
    request: Request, platform: str = "mobile", web_origin: str = None
):
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
        # 3. Use the dynamic origin if provided, otherwise fallback to Firebase
        base_url = web_origin if web_origin else "https://your-project-id.web.app"
        redirect_url = f"{base_url}/auth.html?jwt={app_token}&username={user['login']}"
    else:
        # Android / iOS behavior
        redirect_url = f"codesquad://callback?jwt={app_token}&username={user['login']}"

    return RedirectResponse(url=redirect_url)
