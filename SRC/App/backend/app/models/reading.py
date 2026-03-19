from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func

from app.db.database import Base


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    category = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=True)
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())