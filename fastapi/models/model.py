from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
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
    model_config = ConfigDict(extra="forbid")
    
    text: str


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str


class SigninRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"



class PredictResponse(BaseModel):
    intent: str
    confidence: float


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
