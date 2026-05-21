from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.api import auth, repos
from app.core.config import JWT_SECRET

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET, same_site="lax")

app.include_router(auth.router, prefix="/auth")
app.include_router(repos.router, prefix="/user")
