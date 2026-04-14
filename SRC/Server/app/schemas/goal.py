from typing import Optional
from pydantic import BaseModel


class GoalCreate(BaseModel):
    team_id: int
    category: str
    target_kg: float


class GoalResponse(BaseModel):
    id: int
    team_id: int
    team_name: Optional[str] = None
    category: str
    target_kg: float

    class Config:
        from_attributes = True
