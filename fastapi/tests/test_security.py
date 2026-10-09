import asyncio
import os
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from starlette.requests import Request


FASTAPI_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FASTAPI_DIR))
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from database import get_session  # noqa: E402
from main import app  # noqa: E402
from models import Prediction, PredictRequest, User  # noqa: E402
from rate_limit import limiter  # noqa: E402
from routers.router import get_my_prediction  # noqa: E402
from security import hash_password  # noqa: E402
from security.oauth2 import oauth2_scheme  # noqa: E402


@pytest.fixture
def api_client():
    """Cliente HTTP com banco isolado; não lê nem altera database.db."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        alice = User(username="alice_http", hashed_password=hash_password("senha-segura"))
        bruno = User(username="bruno_http", hashed_password=hash_password("outra-senha"))
        session.add(alice)
        session.add(bruno)
        session.commit()
        session.refresh(alice)
        session.refresh(bruno)

        session.add(
            Prediction(
                text="Prediction da Alice",
                intent="saudacao",
                confidence=0.95,
                owner_id=alice.id,
            )
        )
        bruno_prediction = Prediction(
            text="Prediction do Bruno",
            intent="reclamacao",
            confidence=0.91,
            owner_id=bruno.id,
        )
        session.add(bruno_prediction)
        session.commit()
        session.refresh(bruno_prediction)
        bruno_prediction_id = bruno_prediction.id

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    limiter.reset()
    client = TestClient(app, raise_server_exceptions=False)

    yield client, bruno_prediction_id

    app.dependency_overrides.clear()
    limiter.reset()
    engine.dispose()


def signin(client: TestClient, username: str = "alice_http", password: str = "senha-segura"):
    return client.post(
        "/auth/signin",
        json={"username": username, "password": password},
    )


def alice_headers(client: TestClient) -> dict[str, str]:
    response = signin(client)
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


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


def test_valid_credentials_return_bearer_token(api_client):
    client, _ = api_client

    response = signin(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_invalid_credentials_return_401_without_token(api_client):
    client, _ = api_client

    response = signin(client, password="senha-incorreta")

    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário ou senha incorretos"
    assert response.headers["www-authenticate"] == "Bearer"
    assert "access_token" not in response.json()


def test_tampered_bearer_token_is_rejected(api_client):
    client, _ = api_client

    response = client.get(
        "/predictions",
        headers={"Authorization": "Bearer token.adulterado.invalido"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_prediction_list_does_not_expose_other_users_records(api_client):
    client, bruno_prediction_id = api_client

    response = client.get("/predictions", headers=alice_headers(client))

    assert response.status_code == 200
    predictions = response.json()
    assert len(predictions) == 1
    assert predictions[0]["text"] == "Prediction da Alice"
    assert all(item["id"] != bruno_prediction_id for item in predictions)


def test_predict_rejects_missing_required_text(api_client):
    client, _ = api_client

    response = client.post("/predict", json={}, headers=alice_headers(client))

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"


def test_token_endpoint_blocks_requests_above_rate_limit(api_client):
    client, _ = api_client
    credentials = {"username": "alice_http", "password": "senha-incorreta"}

    first_ten = [client.post("/auth/token", data=credentials) for _ in range(10)]
    blocked = client.post("/auth/token", data=credentials)

    assert all(response.status_code == 401 for response in first_ten)
    assert blocked.status_code == 429
    assert "Rate limit exceeded" in blocked.json()["error"]
