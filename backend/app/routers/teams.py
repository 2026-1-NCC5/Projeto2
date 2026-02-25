from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Team
from app.schemas.teams import TeamOut, TeamCreateIn
from app.services.auth_deps import require_coord_or_admin, get_current_user

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("", response_model=list[TeamOut])
def list_teams(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Team).order_by(Team.name.asc()).all()


@router.post("", response_model=TeamOut)
def create_team(data: TeamCreateIn, db: Session = Depends(get_db), _=Depends(require_coord_or_admin)):
    name = data.name.strip()
    if not name:
        raise HTTPException(400, "Nome inválido")

    exists = db.query(Team).filter(Team.name.ilike(name)).first()
    if exists:
        raise HTTPException(400, "Equipe já existe")

    t = Team(name=name)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db), _=Depends(require_coord_or_admin)):
    t = db.query(Team).filter(Team.id == team_id).first()
    if not t:
        raise HTTPException(404, "Equipe não encontrada")
    db.delete(t)
    db.commit()
    return {"ok": True}