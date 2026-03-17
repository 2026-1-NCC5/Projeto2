import os
import uuid
from PIL import Image
from app.core.config import settings

CLASS_NAMES = ["arroz", "feijao", "outros"]


def save_upload(file_bytes: bytes, filename: str) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(filename)[1] or ".jpg"
    new_name = f"{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(settings.UPLOAD_DIR, new_name)

    with open(full_path, "wb") as f:
        f.write(file_bytes)

    return full_path


def run_inference(image_path: str) -> dict:
    # MVP inicial:
    # abre imagem só para validar
    Image.open(image_path)

    # depois vamos trocar por YOLO real
    return {
        "category": "outros",
        "confidence": 0.75,
        "image_path": image_path
    }