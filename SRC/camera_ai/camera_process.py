import os
import subprocess
import sys
from typing import Optional

from config import BASE_DIR, STOP_FILE, load_config

_camera_process: Optional[subprocess.Popen] = None


def is_running() -> bool:
    return _camera_process is not None and _camera_process.poll() is None


def start() -> dict:
    global _camera_process
    if is_running():
        return {"ok": False, "detail": "Câmera já está rodando"}

    cfg = load_config()
    env = os.environ.copy()
    env["SERVER_URL"] = cfg.get("server_url", "")
    env["CAMERA_API_KEY"] = cfg.get("camera_api_key", "")
    env["TEAM_ID"] = str(cfg.get("team_id", 1))

    _camera_process = subprocess.Popen(
        [sys.executable, str(BASE_DIR / "detector.py")],
        env=env,
        cwd=str(BASE_DIR),
    )
    return {"ok": True, "detail": "Câmera iniciada"}


def stop() -> dict:
    global _camera_process
    if not is_running():
        _camera_process = None
        return {"ok": False, "detail": "Câmera não está rodando"}
    STOP_FILE.write_text("stop")
    try:
        _camera_process.wait(timeout=20)
    except Exception:
        _camera_process.terminate()
    _camera_process = None
    STOP_FILE.unlink(missing_ok=True)
    return {"ok": True, "detail": "Câmera encerrada"}


def finish() -> dict:
    global _camera_process
    if not is_running():
        _camera_process = None
        return {"ok": True, "detail": "Câmera já estava inativa"}
    STOP_FILE.write_text("stop")
    try:
        _camera_process.wait(timeout=30)
    except Exception:
        _camera_process.terminate()
    _camera_process = None
    STOP_FILE.unlink(missing_ok=True)
    return {"ok": True, "detail": "Sessão finalizada"}
