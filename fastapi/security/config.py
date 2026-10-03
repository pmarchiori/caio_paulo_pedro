from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

env_file = Path(__file__).resolve().parents[2] / ".env"

class SecuritySettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    
    model_config = SettingsConfigDict(env_file = env_file)

security_settings = SecuritySettings()