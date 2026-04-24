import csv as _csv
import shutil
import tempfile
from pathlib import Path

import requests
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from config import BASE_DIR, DEFAULT_CONFIG, load_config, save_config
from fastapi import Request
import ml

router = APIRouter()


# ── Config ────────────────────────────────────────────────────────────────────

@router.get("/config")
def get_config():
    cfg = load_config()
    return {
        "server_url": cfg.get("server_url", ""),
        "team_id": cfg.get("team_id", 1),
        "admin_email": cfg.get("admin_email", ""),
    }


@router.post("/config")
async def set_config(request: Request):
    body = await request.json()
    cfg = load_config()
    if "server_url" in body:
        cfg["server_url"] = body["server_url"]
    if "team_id" in body:
        cfg["team_id"] = body["team_id"]
    save_config(cfg)
    return {"ok": True}


# ── Teams ─────────────────────────────────────────────────────────────────────

@router.get("/teams")
def get_teams():
    cfg = load_config()
    try:
        r = requests.get(cfg["server_url"] + "/api/teams", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


# ── Readings ──────────────────────────────────────────────────────────────────

@router.get("/readings")
def get_readings(limit: int = 500):
    cfg = load_config()
    token = cfg.get("admin_token", "")
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Não autenticado"})
    try:
        r = requests.get(
            cfg["server_url"] + f"/api/camera-readings?limit={limit}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=6,
        )
        return r.json() if r.status_code == 200 else JSONResponse(
            status_code=r.status_code, content={"detail": r.text}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


# ── Connection test ───────────────────────────────────────────────────────────

@router.get("/test-connection")
def test_connection():
    cfg = load_config()
    try:
        r = requests.get(cfg["server_url"] + "/", timeout=4)
        return {"ok": True, "detail": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "detail": str(e)}


# ── Debug ─────────────────────────────────────────────────────────────────────

@router.get("/debug")
def debug_info():
    cfg = load_config()
    token = cfg.get("admin_token", "")
    server = cfg.get("server_url", "")
    result = {
        "config": {
            "server_url": server,
            "team_id": cfg.get("team_id"),
            "admin_email": cfg.get("admin_email"),
            "token_present": bool(token),
            "token_preview": token[:30] + "..." if token else "VAZIO",
        },
        "server_ping": None,
        "token_valid": None,
        "camera_readings_count": None,
        "camera_readings_error": None,
        "local_csv_count": None,
        "local_csv_last5": [],
    }
    try:
        r = requests.get(server + "/", timeout=4)
        result["server_ping"] = f"OK ({r.status_code})"
    except Exception as e:
        result["server_ping"] = f"FALHOU: {e}"

    if token:
        try:
            r = requests.get(server + "/api/auth/me",
                             headers={"Authorization": f"Bearer {token}"}, timeout=4)
            result["token_valid"] = r.status_code == 200 or f"INVÁLIDO ({r.status_code}): {r.text}"
        except Exception as e:
            result["token_valid"] = f"ERRO: {e}"

        try:
            r = requests.get(server + "/api/camera-readings?limit=5",
                             headers={"Authorization": f"Bearer {token}"}, timeout=6)
            if r.status_code == 200:
                result["camera_readings_count"] = len(r.json())
            else:
                result["camera_readings_error"] = f"HTTP {r.status_code}: {r.text}"
        except Exception as e:
            result["camera_readings_error"] = str(e)

    log = BASE_DIR / "outputs" / "logs" / "readings.csv"
    if log.exists():
        with open(log, encoding="utf-8") as f:
            rows = list(_csv.reader(f))
        result["local_csv_count"] = max(0, len(rows) - 1)
        result["local_csv_last5"] = rows[-5:] if len(rows) > 1 else []
    else:
        result["local_csv_count"] = "arquivo não encontrado"

    return result


# ── Predict ───────────────────────────────────────────────────────────────────

@router.post("/predict")
async def predict(image: UploadFile = File(...)):
    try:
        model = ml.get_model()
    except FileNotFoundError as e:
        return JSONResponse(status_code=503, content={"detail": str(e)})

    suffix = Path(image.filename or "frame.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(image.file, tmp)
        temp_path = Path(tmp.name)
    try:
        results = model(str(temp_path), conf=ml.CONFIDENCE_THRESHOLD, verbose=False)
        if not results or results[0].boxes is None or len(results[0].boxes) == 0:
            return {"category": "outros", "confidence": 0.0}
        best = max(results[0].boxes, key=lambda b: float(b.conf[0].item()))
        cls_id = int(best.cls[0].item())
        conf = float(best.conf[0].item())
        return {"category": model.names[cls_id], "confidence": round(conf, 4)}
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
