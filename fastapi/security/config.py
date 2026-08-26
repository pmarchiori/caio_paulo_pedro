from pydantic_settings import BaseSettings

class SecuritySettings(BaseSettings):
    SECRET_KEY: str = "troque-isso-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

security_settings = SecuritySettings()