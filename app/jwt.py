from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt
import os

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
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

    if username is None:
        raise ValueError("Nieprawidłowy token")

    return {
        "username": username,
        "role": role
    }