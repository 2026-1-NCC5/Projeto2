import random
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Reading, User
from app.models.enums import FoodCategory
from app.schemas.readings import PredictOut, ReadingOut, ReadingCreateIn
from app.services.auth_deps import get_current_user

router = APIRouter(prefix="/api/readings", tags=["readings"])


@router.post("/predict", response_model=PredictOut)
async def predict(
    image: UploadFile = File(...),
    _user: User = Depends(get_current_user),
):
    # MVP: classificação fake, mas com estrutura pronta.
    # (depois troca isso por YOLO sem mudar o app)
    raw = await image.read()
    seed = sum(raw[:200]) if raw else 0
    random.seed(seed)

    category = random.choice([FoodCategory.arroz, FoodCategory.feijao, FoodCategory.outros])
    confidence = round(random.uniform(0.55, 0.92), 2)

    return PredictOut(category=category, confidence=confidence)


@router.post("", response_model=ReadingOut)
def create_reading(
    data: ReadingCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = Reading(
        team_id=data.team_id,
        user_id=user.id,
        category=data.category.value,
        confidence=data.confidence,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("", response_model=list[ReadingOut])
def list_readings(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
    team_id: int | None = None,
    category: FoodCategory | None = None,
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    limit: int = 200,
):
    q = db.query(Reading).order_by(Reading.created_at.desc())

    if team_id is not None:
        q = q.filter(Reading.team_id == team_id)
    if category is not None:
        q = q.filter(Reading.category == category.value)
    if start is not None:
        q = q.filter(Reading.created_at >= start)
    if end is not None:
        q = q.filter(Reading.created_at <= end)

    return q.limit(limit).all()