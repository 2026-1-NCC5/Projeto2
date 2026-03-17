from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamResponse

router = APIRouter(prefix="/api/teams", tags=["Teams"])


@router.get("", response_model=list[TeamResponse])
def list_teams(db: Session = Depends(get_db)):
    return db.query(Team).order_by(Team.id.asc()).all()


@router.post("", response_model=TeamResponse)
def create_team(data: TeamCreate, db: Session = Depends(get_db)):
    exists = db.query(Team).filter(Team.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Equipe já existe")

    team = Team(name=data.name, active=True)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Equipe não encontrada")

    db.delete(team)
    db.commit()
    return {"message": "Equipe removida com sucesso"}