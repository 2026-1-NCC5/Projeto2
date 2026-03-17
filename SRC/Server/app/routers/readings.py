from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Header
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.reading import Reading
from app.schemas.reading import ReadingCreate, ReadingResponse
from app.services.inference import save_upload, run_inference
from app.core.security import decode_access_token

router = APIRouter(prefix="/api/readings", tags=["Readings"])


def get_current_user_id(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        return None
    return int(payload["sub"])


@router.post("/predict")
async def predict(image: UploadFile = File(...)):
    content = await image.read()
    image_path = save_upload(content, image.filename)
    result = run_inference(image_path)
    return result


@router.post("", response_model=ReadingResponse)
def create_reading(
    data: ReadingCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(default="")
):
    user_id = get_current_user_id(authorization)

    reading = Reading(
        team_id=data.team_id,
        user_id=user_id,
        category=data.category,
        confidence=data.confidence,
        image_path=data.image_path,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("", response_model=list[ReadingResponse])
def list_readings(db: Session = Depends(get_db)):
    return db.query(Reading).order_by(Reading.id.desc()).all()