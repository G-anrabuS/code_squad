from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api import auth, repos, scan, analysis
from app.core.config import JWT_SECRET

app = FastAPI(
    title="CodeSquad API",
    description="AI-powered codebase analysis system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://codesquad-88e63.web.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET, same_site="lax")

# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(repos.router, prefix="/user")
app.include_router(scan.router, prefix="/scan")
app.include_router(analysis.router, prefix="/analysis")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CodeSquad API",
        "version": "1.0.0",
        "docs": "/docs",
        "analysis_endpoints": [
            "/analysis/analyze - POST",
            "/analysis/analyze/background - POST",
            "/analysis/result/{task_id} - GET",
            "/analysis/summary/{task_id} - GET",
        ],
    }
