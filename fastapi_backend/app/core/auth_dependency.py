from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import JWT_SECRET
from app.core.token_store import get_github_session

ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        session_id = payload.get("session_id")

        if not session_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        github_session = get_github_session(session_id)
        if not github_session:
            raise HTTPException(status_code=401, detail="Session expired")

        payload["github_token"] = github_session["github_token"]
        payload["github_username"] = github_session["github_username"]

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
