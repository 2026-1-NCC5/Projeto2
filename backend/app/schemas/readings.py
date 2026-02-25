from datetime import datetime
from pydantic import BaseModel
from app.models.enums import FoodCategory


class PredictOut(BaseModel):
    category: FoodCategory
    confidence: float


class ReadingCreateIn(BaseModel):
    team_id: int | None
    category: FoodCategory
    confidence: float | None = None


class ReadingOut(BaseModel):
    id: int
    team_id: int | None
    user_id: int | None
    category: FoodCategory
    confidence: float | None
    created_at: datetime

    class Config:
        from_attributes = True