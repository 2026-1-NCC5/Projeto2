import shutil
import tempfile
from pathlib import Path

from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = Path(r"C:\Users\leona\OneDrive\Documentos\GitHub\ProjetoScanner\Projeto2\SRC\camera_ai\runs\detect\treino_alimentos\weights\best.pt")
CONFIDENCE_THRESHOLD = 0.60

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Modelo YOLO não encontrado em: {MODEL_PATH}")

model = YOLO(str(MODEL_PATH))


def predict_image(upload_file):
    suffix = Path(upload_file.filename or "frame.jpg").suffix or ".jpg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
      shutil.copyfileobj(upload_file.file, tmp)
      temp_path = Path(tmp.name)

    saved_path = None

    try:
        results = model(str(temp_path), conf=CONFIDENCE_THRESHOLD, verbose=False)

        if not results or results[0].boxes is None or len(results[0].boxes) == 0:
            saved_path = _persist_frame(temp_path, prefix="outros")
            return {
                "category": "outros",
                "confidence": 0.0,
                "image_path": str(saved_path),
            }

        best_box = max(results[0].boxes, key=lambda b: float(b.conf[0].item()))
        cls_id = int(best_box.cls[0].item())
        conf = float(best_box.conf[0].item())
        label = model.names[cls_id]

        saved_path = _persist_frame(temp_path, prefix=str(label))

        return {
            "category": str(label),
            "confidence": round(conf, 4),
            "image_path": str(saved_path),
        }
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def _persist_frame(temp_path: Path, prefix: str):
    filename = f"{prefix}_{temp_path.stem}{temp_path.suffix}"
    destination = UPLOAD_DIR / filename
    shutil.copy(str(temp_path), str(destination))
    return destination