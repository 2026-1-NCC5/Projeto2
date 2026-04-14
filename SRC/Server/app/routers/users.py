from fastapi import APIRouter, Depends, HTTPException, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.team import Team
from app.schemas.user import UserCreateRequest, UserUpdateRequest, UserResponse
from app.core.security import hash_password, decode_access_token

router = APIRouter(prefix="/api/users", tags=["Users"])

security = HTTPBearer()


def get_current_payload(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return payload


def require_admin(payload: dict):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")


def _enrich_user(user: User, db: Session) -> dict:
    team_name = None
    if user.team_id:
        team = db.query(Team).filter(Team.id == user.team_id).first()
        team_name = team.name if team else None
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "team_id": user.team_id,
        "team_name": team_name,
        "active": user.active,
    }


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload)
):
    require_admin(payload)
    users = db.query(User).order_by(User.id.asc()).all()
    return [_enrich_user(u, db) for u in users]


@router.post("", response_model=UserResponse)
def create_user(
    data: UserCreateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload)
):
    require_admin(payload)

    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        team_id=data.team_id,
        active=data.active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _enrich_user(user, db)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload)
):
    require_admin(payload)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        user.email = data.email
    if data.role is not None:
        user.role = data.role
    if data.team_id is not None:
        user.team_id = data.team_id
    if data.active is not None:
        user.active = data.active
    if data.password is not None and data.password.strip() != "":
        user.password_hash = hash_password(data.password)

    db.commit()
    db.refresh(user)
    return _enrich_user(user, db)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload)
):
    require_admin(payload)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(user)
    db.commit()
    return {"message": "Usuário removido com sucesso"}
