from typing import Optional
from ultralytics import YOLO
from config import MODEL_PATH

_model: Optional[YOLO] = None
CONFIDENCE_THRESHOLD = 0.60


def get_model() -> YOLO:
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado em: {MODEL_PATH}\n"
                "Execute: python training/train.py"
            )
        _model = YOLO(str(MODEL_PATH))
    return _model
