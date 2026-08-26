from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from .config import security_settings

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        security_settings.SECRET_KEY,
        algorithm=security_settings.ALGORITHM,
    )

def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            security_settings.SECRET_KEY,
            algorithms=[security_settings.ALGORITHM],
        )
    except JWTError:
        return None