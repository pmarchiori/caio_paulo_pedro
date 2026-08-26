from fastapi import APIRouter, Path, Depends
import random

from models import Event, PredictRequest, PredictResponse
from database import add_event, get_all_events, get_event_by_id
from security import get_current_user


api_router = APIRouter()

MOCK_INTENTS = ["saudacao", "duvida_produto", "reclamacao", "despedida"]

@api_router.get("/health")
async def health() -> dict:
    return {
        "status": "Funcionando..."
    }

@api_router.post("/predict", response_model=PredictResponse)
def predict(
    payload: PredictRequest,
    current_user: dict = Depends(get_current_user),
):
    fake_intent = random.choice(MOCK_INTENTS)
    fake_confidence = round(random.uniform(0.7, 0.99), 2)

    return PredictResponse(intent=fake_intent, confidence=fake_confidence)


### Endpoints da API

@api_router.get("/event")
async def retrieve_event() -> dict:
    return {
        "events": get_all_events()
    }


@api_router.get("/event/{event_id}")
async def get_single_event(
    event_id: int = Path(..., title="The ID of the event to retrieve.")
) -> dict:
    event = get_event_by_id(event_id)
    if event is not None:
        return {
            "event": event
        }
    return {
        "message": "event with supplied ID doesn't exist."
    }


@api_router.post("/event")
async def add_event_new(event: Event) -> Event:
    return add_event(event)