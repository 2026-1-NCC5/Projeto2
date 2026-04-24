import requests
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from config import BASE_DIR, load_config, save_config

router = APIRouter()


def _login_html() -> str:
    return (BASE_DIR / "templates" / "login.html").read_text(encoding="utf-8")


@router.get("/login", response_class=HTMLResponse)
def login_page():
    return _login_html()


@router.post("/login")
async def do_login(request: Request):
    body = await request.json()
    cfg = load_config()
    try:
        r = requests.post(
            cfg["server_url"] + "/api/auth/login",
            json={"email": body.get("email"), "password": body.get("password")},
            timeout=6,
        )
        if r.status_code == 200:
            cfg["admin_token"] = r.json().get("access_token", "")
            cfg["admin_email"] = body.get("email", "")
            save_config(cfg)
            return {"ok": True}
        return JSONResponse(status_code=401, content={"ok": False, "detail": "Credenciais inválidas"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "detail": str(e)})


@router.post("/logout")
def do_logout():
    cfg = load_config()
    cfg["admin_token"] = ""
    cfg["admin_email"] = ""
    save_config(cfg)
    return {"ok": True}
