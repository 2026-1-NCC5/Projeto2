from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.camera_reading import CameraReading
from app.models.team import Team

router = APIRouter(prefix="/api/public", tags=["Public"])


@router.get("/camera-readings")
def public_camera_readings(
    category: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(CameraReading)
    if category:
        q = q.filter(CameraReading.category == category)
    if from_date:
        q = q.filter(CameraReading.created_at >= from_date)
    if to_date:
        q = q.filter(CameraReading.created_at <= to_date)

    readings = q.order_by(CameraReading.id.desc()).all()
    result = []
    for r in readings:
        team = db.query(Team).filter(Team.id == r.team_id).first()
        result.append({
            "id": r.id,
            "team_id": r.team_id,
            "team_name": team.name if team else None,
            "category": r.category,
            "confidence": r.confidence,
            "kg_amount": r.kg_amount,
            "price": r.price or 0.0,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return result
