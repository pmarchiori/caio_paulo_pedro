import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from database import SessionDep
from models import Prediction, PredictionRead, PredictRequest, PredictResponse, User, UserRead
from security import get_current_user


api_router = APIRouter()

MOCK_INTENTS = ["saudacao", "duvida_produto", "reclamacao", "despedida"]


def mock_predict(text: str) -> tuple[str, float]:
    """Simula a saída de um modelo de classificação de forma determinística:
    o mesmo texto sempre produz a mesma intenção e confiança, facilitando testes."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    intent = MOCK_INTENTS[digest[0] % len(MOCK_INTENTS)]
    confidence = round(0.7 + (digest[1] / 255) * 0.29, 2)
    return intent, confidence


@api_router.get("/health")
async def health() -> dict:
    return {
        "status": "Funcionando..."
    }


@api_router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@api_router.post("/predict", response_model=PredictResponse)
def predict(
    payload: PredictRequest,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    fake_intent, fake_confidence = mock_predict(payload.text)

    prediction = Prediction(
        text=payload.text,
        intent=fake_intent,
        confidence=fake_confidence,
        owner_id=current_user.id,
    )
    session.add(prediction)
    session.commit()

    return PredictResponse(intent=fake_intent, confidence=fake_confidence)


@api_router.get("/predictions", response_model=list[PredictionRead])
def list_my_predictions(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    statement = select(Prediction).where(Prediction.owner_id == current_user.id)
    return session.exec(statement).all()


@api_router.get("/predictions/{prediction_id}", response_model=PredictionRead)
def get_my_prediction(
    prediction_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    statement = select(Prediction).where(
        Prediction.id == prediction_id,
        Prediction.owner_id == current_user.id,
    )
    prediction = session.exec(statement).first()
    if prediction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction não encontrada")
    return prediction
