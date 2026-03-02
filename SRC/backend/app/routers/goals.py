from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Goal
from app.schemas.goals import GoalUpsertIn, GoalOut
from app.services.auth_deps import require_admin, get_current_user

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.get("", response_model=list[GoalOut])
def list_goals(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Goal).all()


@router.post("/upsert", response_model=GoalOut)
def upsert_goal(data: GoalUpsertIn, db: Session = Depends(get_db), _=Depends(require_admin)):
    if data.target <= 0:
        raise HTTPException(400, "Meta inválida")

    existing = db.query(Goal).filter(
        Goal.team_id == data.team_id,
        Goal.category == data.category.value,
    ).first()

    if existing:
        existing.target = data.target
        db.commit()
        db.refresh(existing)
        return existing

    g = Goal(team_id=data.team_id, category=data.category.value, target=data.target)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    g = db.query(Goal).filter(Goal.id == goal_id).first()
    if not g:
        raise HTTPException(404, "Meta não encontrada")
    db.delete(g)
    db.commit()
    return {"ok": True}