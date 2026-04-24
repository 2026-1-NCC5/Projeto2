import asyncio

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from config import BASE_DIR, load_config, save_config
from routers import auth, camera, data

app = FastAPI(title="Camera AI — Lideranças Empáticas")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(camera.router)
app.include_router(data.router)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    if not load_config().get("admin_token"):
        return RedirectResponse(url="/login")
    return (BASE_DIR / "templates" / "dashboard.html").read_text(encoding="utf-8")


async def _auto_refresh_token():
    await asyncio.sleep(60)
    while True:
        cfg = load_config()
        token = cfg.get("admin_token", "")
        if token:
            try:
                r = requests.post(
                    cfg["server_url"] + "/api/auth/refresh",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=6,
                )
                if r.status_code == 200:
                    cfg["admin_token"] = r.json().get("access_token", token)
                    save_config(cfg)
            except Exception:
                pass
        await asyncio.sleep(20 * 3600)


@app.on_event("startup")
async def startup():
    asyncio.create_task(_auto_refresh_token())
