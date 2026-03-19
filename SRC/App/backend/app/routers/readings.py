from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.reading import Reading
from app.schemas.readings import PredictOut, ReadingCreate, ReadingResponse
from app.services.yolo_service import predict_image

router = APIRouter(prefix="/api/readings", tags=["Readings"])


@router.post("/predict", response_model=PredictOut)
def predict(image: UploadFile = File(...)):
    return predict_image(image)


@router.post("", response_model=ReadingResponse)
def create_reading(data: ReadingCreate, db: Session = Depends(get_db)):
    reading = Reading(
        team_id=data.team_id,
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