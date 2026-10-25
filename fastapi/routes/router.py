import hashlib
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import select

from database import SessionDep
from models import Prediction, PredictionRead, PredictRequest, PredictResponse, User, UserRead
from rate_limit import limiter
from security import get_admin_user, get_current_user

api_router = APIRouter()

UNAUTHORIZED = {401: {"description": "Token ausente, inválido ou expirado."}}
TOO_MANY = {429: {"description": "Limite de requisições excedido."}}

MOCK_INTENTS = ["saudacao", "duvida_produto", "reclamacao", "despedida"]

def mock_predict(text: str) -> tuple[str, float]:
    """Gera uma previsão determinística para facilitar os testes."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    intent = MOCK_INTENTS[digest[0] % len(MOCK_INTENTS)]
    confidence = round(0.7 + (digest[1] / 255) * 0.29, 2)
    return intent, confidence


@api_router.get(
    "/health",
    tags=["sistema"],
    summary="Verifica se a API está no ar",
    description="Rota pública, sem autenticação. Usada em health checks.",
)

async def health() -> dict:
    return {
        "status": "Funcionando..."
    }

# [Auditoria final - vazamento de hash de senha]
# CORRIGIDO: havia um /me duplicado em main.py sem response_model, que devolvia
# o usuário inteiro (incluindo hashed_password). Foi removido; esta rota usa
# response_model=UserRead, que só expõe id e username.

@api_router.get(
    "/me",
    response_model=UserRead,
    tags=["usuários"],
    summary="Dados do usuário autenticado",
    description="Retorna id e username do dono do token. Nunca expõe a senha/hash.",
    responses=UNAUTHORIZED,
)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@api_router.post(
    "/predict",
    response_model=PredictResponse,
    tags=["predições"],
    summary="Classifica a intenção de um texto de atendimento",
    description=(
        "Recebe um texto (1 a 2000 caracteres) e devolve a intenção prevista. "
        "A previsão é salva no histórico do usuário autenticado. "
        "Limite: 30 requisições por minuto por IP."
    ),
    responses={**UNAUTHORIZED, **TOO_MANY, 422: {"description": "Corpo inválido."}},
)
@limiter.limit("30/minute")
def predict(
    request: Request,
    payload: PredictRequest,
    session: SessionDep,
    current_user: User = Depends(get_admin_user),
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


@api_router.get(
    "/predictions",
    response_model=list[PredictionRead],
    tags=["predições"],
    summary="Lista as predições do usuário autenticado",
    description="Retorna apenas as predições cujo dono é o usuário do token.",
    responses=UNAUTHORIZED,
)
def list_my_predictions(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    statement = select(Prediction).where(Prediction.owner_id == current_user.id)
    return session.exec(statement).all()


@api_router.get("/predictions/{prediction_id}",response_model=PredictionRead,tags=["predições"],
                summary="Busca uma predição do usuário autenticado por id",
                description=(
                    "Retorna 404 tanto se o id não existe quanto se a predição pertence a outro "
                    "usuário, para não revelar a existência de recursos alheios (proteção BOLA)."
                ),
    responses={**UNAUTHORIZED, 404: {"description": "Predição não encontrada."}},
)
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
