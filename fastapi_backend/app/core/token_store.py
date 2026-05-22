from datetime import datetime, timedelta
from secrets import token_urlsafe


_PENDING_LOGINS: dict[str, dict] = {}
_GITHUB_SESSIONS: dict[str, dict] = {}

LOGIN_CODE_TTL = timedelta(minutes=5)
SESSION_TTL = timedelta(days=1)


def create_pending_login(github_username: str, github_token: str) -> str:
    code = token_urlsafe(32)
    _PENDING_LOGINS[code] = {
        "github_username": github_username,
        "github_token": github_token,
        "expires_at": datetime.utcnow() + LOGIN_CODE_TTL,
    }
    return code


def consume_pending_login(code: str) -> dict | None:
    login = _PENDING_LOGINS.pop(code, None)
    if not login or login["expires_at"] < datetime.utcnow():
        return None

    session_id = token_urlsafe(32)
    _GITHUB_SESSIONS[session_id] = {
        "github_username": login["github_username"],
        "github_token": login["github_token"],
        "expires_at": datetime.utcnow() + SESSION_TTL,
    }

    return {
        "session_id": session_id,
        "github_username": login["github_username"],
    }


def get_github_session(session_id: str) -> dict | None:
    session = _GITHUB_SESSIONS.get(session_id)
    if not session:
        return None

    if session["expires_at"] < datetime.utcnow():
        _GITHUB_SESSIONS.pop(session_id, None)
        return None

    return session
