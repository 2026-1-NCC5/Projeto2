from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CameraReadingCreate(BaseModel):
    team_id: int
    category: str
    confidence: float
    kg_amount: float
    price: Optional[float] = None
    evidence_path: Optional[str] = None


class CameraReadingResponse(BaseModel):
    id: int
    team_id: int
    team_name: Optional[str] = None
    category: str
    confidence: float
    kg_amount: float
    price: Optional[float] = None
    evidence_path: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CameraReadingSummaryItem(BaseModel):
    team_id: int
    team_name: str
    category: str
    total_kg: float
    total_price: float
    avg_confidence: float
    count: int
