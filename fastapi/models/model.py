from pydantic import BaseModel


class Event(BaseModel):
    id: int
    item: str
    date: str
    organizer_id: int
    audit_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "item": "Example Schema!",
                "date": "2026-10-30",
                "organizer_id": 42,
                "audit_token": "a1b2c3d4-audit-9f8e"
            }
        }


class EventItem(BaseModel):
    item: str

    class Config:
        json_schema_extra = {
            "example": {
                "item": "Read the next chapter of the book"
            }
        }

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    intent: str
    confidence: float