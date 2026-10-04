import asyncio
import os
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlmodel import Session, SQLModel, create_engine
from starlette.requests import Request


FASTAPI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FASTAPI_DIR))
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from models import Prediction, PredictRequest, User  # noqa: E402
from routers.router import get_my_prediction  # noqa: E402
from security.oauth2 import oauth2_scheme  # noqa: E402


@pytest.fixture
def ownership_context():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        alice = User(username="alice", hashed_password="not-used")
        bruno = User(username="bruno", hashed_password="not-used")
        session.add(alice)
        session.add(bruno)
        session.commit()
        session.refresh(alice)
        session.refresh(bruno)

        prediction = Prediction(
            text="Prediction do Bruno",
            intent="reclamacao",
            confidence=0.9,
            owner_id=bruno.id,
        )
        session.add(prediction)
        session.commit()
        session.refresh(prediction)

        yield session, alice, prediction.id

    engine.dispose()


def test_access_without_token_returns_401():
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/predictions/1",
            "headers": [],
        }
    )

    with pytest.raises(HTTPException) as exception:
        asyncio.run(oauth2_scheme(request))

    assert exception.value.status_code == 401


def test_access_to_another_users_resource_returns_404(ownership_context):
    session, alice, bruno_prediction_id = ownership_context

    with pytest.raises(HTTPException) as exception:
        get_my_prediction(bruno_prediction_id, session, alice)

    assert exception.value.status_code == 404


def test_extra_body_field_is_rejected():
    with pytest.raises(ValidationError) as exception:
        PredictRequest.model_validate(
            {"text": "Preciso de ajuda", "extra_field": "não permitido"}
        )

    assert exception.value.errors()[0]["type"] == "extra_forbidden"
