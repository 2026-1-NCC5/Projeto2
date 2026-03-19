from datetime import datetime
from pydantic import BaseModel


class PredictOut(BaseModel):
    category: str
    confidence: float
    image_path: str | None = None


class ReadingCreate(BaseModel):
    team_id: int | None = None
    category: str
    confidence: float | None = None
    image_path: str | None = None


class ReadingResponse(BaseModel):
    id: int
    team_id: int | None = None
    user_id: int | None = None
    category: str
    confidence: float | None = None
    image_path: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True