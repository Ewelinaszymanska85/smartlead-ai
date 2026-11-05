from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt
import os


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY or len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError(
        "SECRET_KEY nie jest ustawiony lub jest zbyt krótki. "
        "Wymagane minimum to 32 bajty."
    )


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(token: str):
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    username = payload.get("sub")
    role = payload.get("role")
    user_id = payload.get("user_id")

    if username is None or role is None or user_id is None:
        raise ValueError("Nieprawidłowy token")

    return {
        "id": user_id,
        "username": username,
        "role": role
    }