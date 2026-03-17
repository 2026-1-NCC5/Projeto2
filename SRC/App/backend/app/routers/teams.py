from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("/", response_model=list[TeamResponse])
def list_teams(db: Session = Depends(get_db),
               user = Depends(get_current_user)):
    return db.query(Team).all()


@router.post("/", response_model=TeamResponse)
def create_team(team: TeamCreate,
                db: Session = Depends(get_db),
                user = Depends(get_current_user)):

    existing = db.query(Team).filter(Team.name == team.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Equipe já existe")

    new_team = Team(name=team.name)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    return new_team


@router.delete("/{team_id}")
def delete_team(team_id: int,
                db: Session = Depends(get_db),
                user = Depends(get_current_user)):

    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Equipe não encontrada")

    db.delete(team)
    db.commit()

    return {"message": "Equipe removida"}