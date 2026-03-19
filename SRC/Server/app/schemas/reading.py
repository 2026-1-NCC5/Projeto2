from pydantic import BaseModel
from typing import Optional


class ReadingCreate(BaseModel):
    team_id: int
    category: str
    confidence: Optional[float] = None
    image_path: Optional[str] = None


class ReadingResponse(BaseModel):
    id: int
    team_id: int
    user_id: Optional[int]
    category: str
    confidence: Optional[float]
    image_path: Optional[str]

    class Config:
        from_attributes = True

