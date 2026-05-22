from fastapi import APIRouter, HTTPException, Request
from authlib.integrations.starlette_client import OAuth
from app.core.config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
import httpx
from app.core.security import create_access_token
from app.core.token_store import consume_pending_login, create_pending_login
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
async def github_login(
    request: Request, platform: str = "mobile", web_origin: str = None
):
    # Only add web_origin to the URL if it actually exists (prevents the "None" string bug)
    params = {"platform": platform}
    if web_origin:
        params["web_origin"] = web_origin

    redirect_uri = str(
        request.url_for("github_callback").include_query_params(**params)
    )
    return await oauth.github.authorize_redirect(request, redirect_uri, prompt="login")


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
    login_code = create_pending_login(
        github_username=user["login"],
        github_token=access_token,
    )

    if platform == "web":
        # Guard against the literal string "None" just in case
        if web_origin and web_origin != "None":
            base_url = web_origin
        else:
            # PUT YOUR ACTUAL FIREBASE URL HERE
            base_url = "https://codesquad-88e63.web.app/"

        redirect_url = f"{base_url}/auth.html?code={login_code}"
    else:
        # Android / iOS behavior
        redirect_url = f"codesquad://callback?code={login_code}"

    return RedirectResponse(url=redirect_url)


@router.post("/exchange")
async def exchange_login_code(payload: dict):
    login_code = payload.get("code")
    if not login_code:
        raise HTTPException(status_code=400, detail="Login code is required")

    session = consume_pending_login(login_code)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired login code")

    app_token = create_access_token(
        {
            "sub": session["github_username"],
            "github_username": session["github_username"],
            "session_id": session["session_id"],
        }
    )

    return {
        "jwt": app_token,
        "username": session["github_username"],
    }
