from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.camera_reading import CameraReading
from app.models.team import Team
from app.core.config import settings
from app.core.security import decode_access_token
from app.schemas.camera_reading import (
    CameraReadingCreate,
    CameraReadingResponse,
    CameraReadingSummaryItem,
)

router = APIRouter(prefix="/api/camera-readings", tags=["Camera Readings"])

VALID_CATEGORIES = {"arroz", "feijao", "macarrao", "acucar", "outros", "cafe"}


def _require_camera_key(x_camera_key: str = Header(default="")):
    if x_camera_key != settings.CAMERA_API_KEY:
        raise HTTPException(status_code=401, detail="Camera API key inválida")


def _require_admin(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")
    payload = decode_access_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin pode acessar")
    return payload


@router.post("", response_model=CameraReadingResponse)
def create_camera_reading(
    data: CameraReadingCreate,
    db: Session = Depends(get_db),
    _: None = Depends(_require_camera_key),
):
    if data.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Categoria inválida: {data.category}")

    team = db.query(Team).filter(Team.id == data.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Equipe não encontrada")

    reading = CameraReading(
        team_id=data.team_id,
        category=data.category,
        confidence=data.confidence,
        kg_amount=data.kg_amount,
        price=data.price,
        evidence_path=data.evidence_path,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    return {
        "id": reading.id,
        "team_id": reading.team_id,
        "team_name": team.name,
        "category": reading.category,
        "confidence": reading.confidence,
        "kg_amount": reading.kg_amount,
        "price": reading.price,
        "evidence_path": reading.evidence_path,
        "created_at": reading.created_at,
    }


@router.get("/summary", response_model=list[CameraReadingSummaryItem])
def camera_summary(
    team_id: Optional[int] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(_require_admin),
):
    q = (
        db.query(
            CameraReading.team_id,
            Team.name.label("team_name"),
            CameraReading.category,
            func.sum(CameraReading.kg_amount).label("total_kg"),
            func.sum(CameraReading.price).label("total_price"),
            func.avg(CameraReading.confidence).label("avg_confidence"),
            func.count(CameraReading.id).label("count"),
        )
        .join(Team, CameraReading.team_id == Team.id)
    )

    if team_id:
        q = q.filter(CameraReading.team_id == team_id)
    if from_date:
        q = q.filter(CameraReading.created_at >= from_date)
    if to_date:
        q = q.filter(CameraReading.created_at <= to_date)

    rows = q.group_by(CameraReading.team_id, Team.name, CameraReading.category).all()

    return [
        {
            "team_id": r.team_id,
            "team_name": r.team_name,
            "category": r.category,
            "total_kg": r.total_kg or 0.0,
            "total_price": round(r.total_price or 0.0, 2),
            "avg_confidence": round(r.avg_confidence or 0.0, 4),
            "count": r.count,
        }
        for r in rows
    ]


@router.get("", response_model=list[CameraReadingResponse])
def list_camera_readings(
    team_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    _: dict = Depends(_require_admin),
):
    q = db.query(CameraReading)

    if team_id:
        q = q.filter(CameraReading.team_id == team_id)
    if category:
        q = q.filter(CameraReading.category == category)
    if from_date:
        q = q.filter(CameraReading.created_at >= from_date)
    if to_date:
        q = q.filter(CameraReading.created_at <= to_date)

    readings = q.order_by(CameraReading.id.desc()).limit(limit).all()

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
            "price": r.price,
            "evidence_path": r.evidence_path,
            "created_at": r.created_at,
        })
    return result
