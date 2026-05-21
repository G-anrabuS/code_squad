from fastapi import Header, HTTPException
from jose import jwt, JWTError
from app.core.config import JWT_SECRET

ALGORITHM = "HS256"


def get_current_user(authorization: str = Header(None)):
    print("AUTH HEADER RECEIVED:", authorization)
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
