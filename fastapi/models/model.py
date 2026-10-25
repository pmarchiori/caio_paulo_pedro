from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field as PField
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str


class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    intent: str
    confidence: float
    owner_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    text: str = PField(
        min_length=1,
        max_length=2000,
        description="Texto do atendimento ao cliente a ser classificado.",
        examples=["Quero cancelar minha assinatura e receber o reembolso."],
    )


USERNAME_PATTERN = r"^[A-Za-z0-9_.-]+$"


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = PField(
        min_length=3,
        max_length=50,
        pattern=USERNAME_PATTERN,
        description="Nome de usuário (3 a 50 caracteres: letras, números, _ . -).",
        examples=["maria.silva"],
    )
    password: str = PField(
        min_length=8,
        max_length=72,
        description="Senha (8 a 72 caracteres; 72 é o limite do bcrypt).",
        examples=["uma-senha-forte-123"],
    )


class SigninRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = PField(min_length=1, max_length=50, examples=["alice"])
    password: str = PField(min_length=1, max_length=72, examples=["alice123"])


class TokenResponse(BaseModel):
    access_token: str = PField(description="JWT para o header Authorization: Bearer <token>.")
    token_type: str = "bearer"



class PredictResponse(BaseModel):
    intent: str = PField(description="Intenção prevista para o texto.", examples=["Refund request"])
    confidence: float = PField(description="Confiança da previsão (0 a 1).", examples=[0.91])


class PredictionRead(BaseModel):
    id: int
    text: str
    intent: str
    confidence: float
    owner_id: int
    created_at: datetime


class UserRead(BaseModel):
    id: int
    username: str