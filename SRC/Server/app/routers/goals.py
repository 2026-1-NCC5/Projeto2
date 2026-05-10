from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.goal import Goal
from app.models.team import Team
from app.schemas.goal import GoalCreate, GoalResponse
from app.core.security import decode_access_token

router = APIRouter(prefix="/api/goals", tags=["Goals"])

VALID_CATEGORIES = {"arroz", "feijao", "macarrao", "acucar", "fuba", "oleo", "outros"}


def _require_admin(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")
    payload = decode_access_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito ao admin")
    return payload


def _get_payload(authorization: str) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")
    payload = decode_access_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return payload


def _enrich(goal: Goal, db: Session) -> dict:
    team = db.query(Team).filter(Team.id == goal.team_id).first()
    return {
        "id": goal.id,
        "team_id": goal.team_id,
        "team_name": team.name if team else None,
        "category": goal.category,
        "target_kg": goal.target_kg,
    }


@router.get("", response_model=list[GoalResponse])
def list_goals(
    team_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    authorization: str = Header(default=""),
):
    payload = _get_payload(authorization)
    role = payload.get("role")
    user_team_id = payload.get("team_id")

    q = db.query(Goal)

    if role == "coordenador":
        q = q.filter(Goal.team_id == user_team_id)
    elif team_id:
        q = q.filter(Goal.team_id == team_id)

    goals = q.order_by(Goal.team_id, Goal.category).all()
    return [_enrich(g, db) for g in goals]


@router.post("", response_model=GoalResponse)
def upsert_goal(
    data: GoalCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(default=""),
):
    _require_admin(authorization)

    if data.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Categoria inválida: {data.category}")

    existing = db.query(Goal).filter(
        Goal.team_id == data.team_id,
        Goal.category == data.category,
    ).first()

    if existing:
        existing.target_kg = data.target_kg
        db.commit()
        db.refresh(existing)
        return _enrich(existing, db)

    goal = Goal(team_id=data.team_id, category=data.category, target_kg=data.target_kg)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _enrich(goal, db)


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(default=""),
):
    _require_admin(authorization)

    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    db.delete(goal)
    db.commit()
    return {"message": "Meta removida"}
