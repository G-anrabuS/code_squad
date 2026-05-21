from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.api import auth
from app.core.config import JWT_SECRET

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET)

app.include_router(auth.router, prefix="/auth")
