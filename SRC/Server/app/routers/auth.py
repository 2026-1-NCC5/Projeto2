from fastapi import APIRouter, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.database import get_db
from app.models.user import User
from app.models.team import Team
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _build_user_response(user: User, db: Session) -> dict:
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


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        team_id=data.team_id,
        active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Usuário criado com sucesso"}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not user.active:
        raise HTTPException(status_code=403, detail="Usuário inativo")

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "name": user.name,
        "team_id": user.team_id,
    })
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def me(authorization: str = Header(default=""), db: Session = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")

    payload = decode_access_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return _build_user_response(user, db)
