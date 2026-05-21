from jose import jwt
from datetime import datetime, timedelta
from app.core.config import JWT_SECRET

ALGORITHM = "HS256"


def create_access_token(data: dict):
    payload = data.copy()

    payload["exp"] = datetime.utcnow() + timedelta(days=1)

    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

    return token
