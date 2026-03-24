from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    category = Column(String(50))
    confidence = Column(Float)

    image_path = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
