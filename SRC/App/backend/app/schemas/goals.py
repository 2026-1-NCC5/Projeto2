from pydantic import BaseModel
from app.models.enums import FoodCategory


class GoalUpsertIn(BaseModel):
    team_id: int
    category: FoodCategory
    target: int


class GoalOut(BaseModel):
    id: int
    team_id: int
    category: FoodCategory
    target: int

    class Config:
        from_attributes = True