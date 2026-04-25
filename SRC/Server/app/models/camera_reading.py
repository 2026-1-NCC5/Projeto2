from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class CameraReading(Base):
    __tablename__ = "camera_readings"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    category = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    kg_amount = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=True, default=0.0)
    evidence_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
