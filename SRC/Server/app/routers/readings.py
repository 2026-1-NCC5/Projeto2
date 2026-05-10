from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.reading import Reading
from app.models.team import Team
from app.models.user import User
from app.schemas.reading import ReadingCreate, ReadingResponse, ReadingSummaryItem
from app.core.security import decode_access_token

router = APIRouter(prefix="/api/readings", tags=["Readings"])

VALID_CATEGORIES = {"arroz", "feijao", "macarrao", "acucar", "fuba", "oleo", "outros"}


def _get_payload(authorization: str) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")
    payload = decode_access_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return payload


@router.post("", response_model=ReadingResponse)
def create_reading(
    data: ReadingCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(default=""),
):
    payload = _get_payload(authorization)
    user_id = int(payload["sub"])
    role = payload.get("role")
    user_team_id = payload.get("team_id")

    if data.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Categoria inválida: {data.category}")

    # Operador e Coordenador só podem registrar no próprio time
    if role in ("operador", "coordenador") and user_team_id != data.team_id:
        raise HTTPException(status_code=403, detail="Registro apenas para seu próprio time")

    reading = Reading(
        team_id=data.team_id,
        user_id=user_id,
        category=data.category,
        kg_amount=data.kg_amount,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    team = db.query(Team).filter(Team.id == reading.team_id).first()
    user = db.query(User).filter(User.id == reading.user_id).first()

    return {
        "id": reading.id,
        "team_id": reading.team_id,
        "team_name": team.name if team else None,
        "user_id": reading.user_id,
        "user_name": user.name if user else None,
        "category": reading.category,
        "kg_amount": reading.kg_amount,
        "created_at": reading.created_at,
    }


@router.get("/summary", response_model=list[ReadingSummaryItem])
def readings_summary(
    team_id: Optional[int] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    authorization: str = Header(default=""),
):
    payload = _get_payload(authorization)
    role = payload.get("role")
    user_team_id = payload.get("team_id")

    q = (
        db.query(
            Reading.team_id,
            Team.name.label("team_name"),
            Reading.category,
            func.sum(Reading.kg_amount).label("total_kg"),
        )
        .join(Team, Reading.team_id == Team.id)
    )

    if role == "coordenador":
        q = q.filter(Reading.team_id == user_team_id)
    elif team_id:
        q = q.filter(Reading.team_id == team_id)

    if from_date:
        q = q.filter(Reading.created_at >= from_date)
    if to_date:
        q = q.filter(Reading.created_at <= to_date)

    rows = q.group_by(Reading.team_id, Team.name, Reading.category).all()

    return [
        {
            "team_id": r.team_id,
            "team_name": r.team_name,
            "category": r.category,
            "total_kg": r.total_kg or 0.0,
        }
        for r in rows
    ]


@router.get("", response_model=list[ReadingResponse])
def list_readings(
    team_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    authorization: str = Header(default=""),
):
    payload = _get_payload(authorization)
    role = payload.get("role")
    user_team_id = payload.get("team_id")

    q = db.query(Reading)

    # Coordenador só vê seu próprio time
    if role == "coordenador":
        q = q.filter(Reading.team_id == user_team_id)
    elif team_id:
        q = q.filter(Reading.team_id == team_id)

    if category:
        q = q.filter(Reading.category == category)
    if from_date:
        q = q.filter(Reading.created_at >= from_date)
    if to_date:
        q = q.filter(Reading.created_at <= to_date)

    readings = q.order_by(Reading.id.desc()).all()

    result = []
    for r in readings:
        team = db.query(Team).filter(Team.id == r.team_id).first()
        user = db.query(User).filter(User.id == r.user_id).first() if r.user_id else None
        result.append({
            "id": r.id,
            "team_id": r.team_id,
            "team_name": team.name if team else None,
            "user_id": r.user_id,
            "user_name": user.name if user else None,
            "category": r.category,
            "kg_amount": r.kg_amount,
            "created_at": r.created_at,
        })
    return result
