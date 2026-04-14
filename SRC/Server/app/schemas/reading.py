from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReadingCreate(BaseModel):
    team_id: int
    category: str
    kg_amount: float


class ReadingResponse(BaseModel):
    id: int
    team_id: int
    team_name: Optional[str] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    category: str
    kg_amount: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReadingSummaryItem(BaseModel):
    team_id: int
    team_name: str
    category: str
    total_kg: float
