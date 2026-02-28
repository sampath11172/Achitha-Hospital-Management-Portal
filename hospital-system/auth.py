import hashlib
import hmac
import os
from http import cookies

_SECRET = os.environ.get("SHMS_SECRET", "shms-local-secret")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_session_token(username: str, role: str) -> str:
    payload = f"{username}:{role}"
    signature = hmac.new(_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def parse_session_token(token: str):
    parts = token.split(":")
    if len(parts) != 3:
        return None
    username, role, signature = parts
    expected = hmac.new(_SECRET.encode(), f"{username}:{role}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    return {"username": username, "role": role}


def read_cookie(cookie_header: str, name: str):
    if not cookie_header:
        return None
    jar = cookies.SimpleCookie()
    jar.load(cookie_header)
    if name in jar:
        return jar[name].value
    return None


def make_session_cookie(token: str) -> str:
    return f"session={token}; HttpOnly; Path=/; SameSite=Lax"
