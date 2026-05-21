from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- ADD THIS IMPORT
from starlette.middleware.sessions import SessionMiddleware
from app.api import auth, repos, scan
from app.core.config import JWT_SECRET

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET, same_site="lax")

app.include_router(auth.router, prefix="/auth")
app.include_router(repos.router, prefix="/user")
app.include_router(scan.router, prefix="/scan")
