import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from ultralytics import YOLO

# ── Processo da câmera ────────────────────────────────────────────────────────
_camera_process: Optional[subprocess.Popen] = None

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "runs" / "detect" / "treino_alimentos" / "weights" / "best.pt"
CONFIG_FILE = BASE_DIR / "camera_config.json"
STOP_FILE = BASE_DIR / ".camera_stop"
CONFIDENCE_THRESHOLD = 0.60

DEFAULT_CONFIG = {
    "server_url": "http://3.80.36.248:8000",
    "camera_api_key": "camera-secret-key",  # nunca exposto na UI
    "team_id": 1,
    "admin_token": "",
    "admin_email": "",
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            # garante que campos novos existam
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


# ── YOLO (lazy) ───────────────────────────────────────────────────────────────
_model = None


def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado em: {MODEL_PATH}\n"
                "Execute: python training/train.py"
            )
        _model = YOLO(str(MODEL_PATH))
    return _model


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Camera AI — Lideranças Empáticas")


async def _auto_refresh_token():
    """Renova o token a cada 20 horas enquanto a app está rodando."""
    await asyncio.sleep(60)  # aguarda 1 min antes do primeiro ciclo
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
        await asyncio.sleep(20 * 3600)  # renova a cada 20 horas


@app.on_event("startup")
async def startup():
    asyncio.create_task(_auto_refresh_token())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
#  PÁGINA DE LOGIN
# ─────────────────────────────────────────────────────────────────────────────
LOGIN_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Login — Camera AI</title>
  <style>
    :root { --primary: #FF6B00; --primary-dark: #e05a00; --green: #2E7D32; --red: #c62828; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #FF6B00 0%, #ff9a4d 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .card {
      background: #fff;
      border-radius: 20px;
      padding: 40px 36px;
      width: 100%;
      max-width: 400px;
      box-shadow: 0 20px 60px rgba(0,0,0,.2);
    }
    .logo {
      text-align: center;
      margin-bottom: 28px;
    }
    .logo .icon {
      font-size: 48px;
      display: block;
      margin-bottom: 8px;
    }
    .logo h1 {
      font-size: 22px;
      font-weight: 800;
      color: var(--primary);
    }
    .logo p {
      font-size: 13px;
      color: #888;
      margin-top: 4px;
    }
    label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      color: #555;
      margin-bottom: 5px;
      margin-top: 16px;
    }
    input {
      width: 100%;
      border: 1.5px solid #e0e0e0;
      border-radius: 10px;
      padding: 11px 14px;
      font-size: 14px;
      transition: border-color .2s;
      outline: none;
    }
    input:focus { border-color: var(--primary); }
    button {
      margin-top: 24px;
      width: 100%;
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 10px;
      padding: 13px;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      transition: background .2s;
    }
    button:hover { background: var(--primary-dark); }
    button:disabled { opacity: .6; cursor: default; }
    .msg {
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 13px;
      margin-top: 14px;
      display: none;
    }
    .msg.ok { background: #e8f5e9; color: var(--green); display: block; }
    .msg.err { background: #ffebee; color: var(--red); display: block; }
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">
      <span class="icon">📷</span>
      <h1>Camera AI</h1>
      <p>Lideranças Empáticas</p>
    </div>
    <form id="login-form">
      <label>Email</label>
      <input type="email" id="email" placeholder="admin@admin.com" required autofocus/>
      <label>Senha</label>
      <input type="password" id="password" placeholder="••••••" required/>
      <button type="submit" id="btn">Entrar</button>
      <div class="msg" id="msg"></div>
    </form>
  </div>
  <script>
    document.getElementById('login-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('btn');
      const msg = document.getElementById('msg');
      btn.disabled = true; btn.textContent = 'Entrando...';
      const r = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: document.getElementById('email').value.trim(),
          password: document.getElementById('password').value,
        }),
      });
      const data = await r.json();
      if (r.ok && data.ok) {
        window.location.href = '/';
      } else {
        msg.className = 'msg err';
        msg.textContent = '✗ ' + (data.detail || 'Credenciais inválidas');
        btn.disabled = false; btn.textContent = 'Entrar';
      }
    });
  </script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Camera AI — Lideranças Empáticas</title>
  <style>
    :root { --primary: #FF6B00; --primary-light: #fff3e8; --green: #2E7D32; --red: #c62828; --gray: #f5f5f5; --border: #e0e0e0; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #f0f0f0; color: #222; }
    header {
      background: var(--primary); color: #fff;
      padding: 14px 24px;
      display: flex; align-items: center; justify-content: space-between;
      box-shadow: 0 2px 8px rgba(0,0,0,.2);
    }
    .header-left { display: flex; align-items: center; gap: 12px; }
    header h1 { font-size: 18px; font-weight: 700; }
    header .sub { font-size: 12px; opacity: .8; margin-top: 2px; }
    .logout-btn {
      background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.4);
      color: #fff; border-radius: 8px; padding: 7px 14px;
      font-size: 13px; font-weight: 600; cursor: pointer;
    }
    .logout-btn:hover { background: rgba(255,255,255,.25); }
    main { max-width: 1100px; margin: 24px auto; padding: 0 16px; display: grid; gap: 20px; }
    .card { background: #fff; border-radius: 14px; padding: 20px 24px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    .card h2 { font-size: 15px; font-weight: 700; color: var(--primary); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
    .stat-box { background: var(--primary-light); border-radius: 10px; padding: 14px 16px; }
    .stat-box .val { font-size: 26px; font-weight: 800; color: var(--primary); }
    .stat-box .lbl { font-size: 12px; color: #888; margin-top: 2px; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    label { font-size: 13px; font-weight: 600; color: #555; display: block; margin-bottom: 4px; }
    input, select {
      width: 100%; border: 1.5px solid var(--border); border-radius: 8px;
      padding: 9px 12px; font-size: 14px; outline: none;
    }
    input:focus, select:focus { border-color: var(--primary); }
    .btn-row { display: flex; gap: 10px; margin-top: 14px; flex-wrap: wrap; }
    button { background: var(--primary); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-size: 14px; font-weight: 600; cursor: pointer; }
    button:hover { opacity: .88; }
    button.secondary { background: #fff; color: var(--primary); border: 2px solid var(--primary); }
    .msg { border-radius: 8px; padding: 10px 14px; font-size: 13px; margin-top: 10px; display: none; }
    .msg.ok { background: #e8f5e9; color: var(--green); display: block; }
    .msg.err { background: #ffebee; color: var(--red); display: block; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th { background: var(--gray); text-align: left; padding: 10px 12px; font-weight: 600; color: #555; }
    td { padding: 9px 12px; border-top: 1px solid var(--border); }
    tr:hover td { background: var(--primary-light); }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; background: var(--primary-light); color: var(--primary); }
    .conf-bar { height: 6px; border-radius: 3px; background: #eee; margin-top: 4px; }
    .conf-bar span { display: block; height: 100%; border-radius: 3px; background: var(--primary); }
    .empty { text-align: center; color: #aaa; padding: 32px; }
    @media (max-width: 600px) { .row { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <div class="header-left">
      <span style="font-size:24px">📷</span>
      <div>
        <h1>Camera AI</h1>
        <div class="sub" id="header-sub">Carregando...</div>
      </div>
    </div>
    <button class="logout-btn" onclick="doLogout()">Sair</button>
  </header>

  <main>
    <!-- Stats -->
    <div class="card">
      <h2>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
        Resumo
      </h2>
      <div class="stats-grid">
        <div class="stat-box"><div class="val" id="stat-count">—</div><div class="lbl">Detecções</div></div>
        <div class="stat-box"><div class="val" id="stat-kg">—</div><div class="lbl">Total kg</div></div>
        <div class="stat-box"><div class="val" id="stat-conf">—</div><div class="lbl">Confiança média</div></div>
        <div class="stat-box"><div class="val" id="stat-team">—</div><div class="lbl">Equipe</div></div>
      </div>
    </div>

    <!-- Câmera -->
    <div class="card">
      <h2>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>
        Controle da Câmera
      </h2>
      <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap; margin-bottom:12px">
        <div style="display:flex; align-items:center; gap:8px;">
          <div id="cam-dot" style="width:12px;height:12px;border-radius:50%;background:#ccc;transition:background .3s"></div>
          <span id="cam-text" style="font-size:14px;color:#666;">Verificando...</span>
        </div>
      </div>
      <div class="btn-row">
        <button id="cam-start-btn" onclick="startCamera()">Iniciar Câmera</button>
        <button id="cam-finish-btn" onclick="finishSession()" style="background:#2E7D32;display:none">
          ✓ Finalizar Sessão
        </button>
      </div>
      <div class="msg" id="cam-msg"></div>
    </div>

    <!-- Configuração -->
    <div class="card">
      <h2>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93A10 10 0 0 0 4.93 19.07M4.93 4.93A10 10 0 0 0 19.07 19.07"/></svg>
        Configuração
      </h2>
      <form id="config-form">
        <div class="row">
          <div>
            <label>URL do Servidor</label>
            <input type="text" id="cfg-server" placeholder="http://3.80.36.248:8000"/>
          </div>
          <div>
            <label>Equipe</label>
            <select id="cfg-team">
              <option value="">Carregando equipes...</option>
            </select>
          </div>
        </div>
        <div class="btn-row">
          <button type="submit">Salvar</button>
          <button type="button" class="secondary" onclick="testConnection()">Testar conexão</button>
        </div>
        <div class="msg" id="cfg-msg"></div>
      </form>
    </div>

    <!-- Leituras -->
    <div class="card">
      <h2>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        Últimas Detecções
      </h2>
      <div class="btn-row" style="margin-bottom:12px">
        <button onclick="loadReadings()" class="secondary">↻ Atualizar</button>
      </div>
      <div id="readings-container"><div class="empty">Carregando...</div></div>
    </div>
  </main>

  <script>
    let _cameraRunning = false;

    // ── Câmera ────────────────────────────────────────────────────────────────
    async function checkCameraStatus() {
      try {
        const data = await fetch('/camera/status').then(r => r.json());
        _cameraRunning = data.running;
        document.getElementById('cam-dot').style.background = _cameraRunning ? '#4caf50' : '#ccc';
        document.getElementById('cam-text').textContent = _cameraRunning ? 'Câmera ativa — detectando...' : 'Câmera inativa';
        document.getElementById('cam-start-btn').style.display = _cameraRunning ? 'none' : '';
        document.getElementById('cam-finish-btn').style.display = _cameraRunning ? '' : 'none';
      } catch {}
    }

    async function startCamera() {
      const msg = document.getElementById('cam-msg');
      const data = await fetch('/camera/start', { method: 'POST' }).then(r => r.json());
      msg.className = data.ok ? 'msg ok' : 'msg err';
      msg.textContent = data.detail;
      setTimeout(() => { msg.className = 'msg'; }, 4000);
      await checkCameraStatus();
    }

    async function finishSession() {
      const btn = document.getElementById('cam-finish-btn');
      const msg = document.getElementById('cam-msg');
      btn.disabled = true;
      btn.textContent = '⏳ Encerrando e enviando...';
      msg.className = 'msg ok';
      msg.textContent = 'Aguardando envio dos dados ao servidor...';

      await fetch('/camera/finish', { method: 'POST' });

      msg.textContent = 'Sessão finalizada! Atualizando leituras...';
      await checkCameraStatus();
      await loadReadings();
      msg.textContent = '✓ Dados enviados e tabela atualizada.';
      setTimeout(() => { msg.className = 'msg'; btn.disabled = false; btn.textContent = '✓ Finalizar Sessão'; }, 4000);
    }

    // ── Config ────────────────────────────────────────────────────────────────
    async function loadTeams(savedId) {
      const sel = document.getElementById('cfg-team');
      try {
        const teams = await fetch('/teams').then(r => r.json());
        sel.innerHTML = teams.length === 0
          ? '<option value="">Nenhuma equipe encontrada</option>'
          : teams.map(t => `<option value="${t.id}" ${t.id == savedId ? 'selected' : ''}>${t.name}</option>`).join('');
      } catch {
        sel.innerHTML = '<option value="">Erro ao carregar equipes</option>';
      }
    }

    async function loadConfig() {
      const cfg = await fetch('/config').then(r => r.json());
      document.getElementById('cfg-server').value = cfg.server_url || '';
      await loadTeams(cfg.team_id);
      const sel = document.getElementById('cfg-team');
      const teamName = sel.options[sel.selectedIndex]?.text || '—';
      document.getElementById('header-sub').textContent = 'Equipe: ' + teamName + ' · ' + (cfg.admin_email || '');
      document.getElementById('stat-team').textContent = teamName;
    }

    document.getElementById('config-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const sel = document.getElementById('cfg-team');
      const body = {
        server_url: document.getElementById('cfg-server').value.trim(),
        team_id: parseInt(sel.value),
      };
      const r = await fetch('/config', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
      const msg = document.getElementById('cfg-msg');
      if (r.ok) {
        msg.className = 'msg ok'; msg.textContent = 'Configuração salva!';
        loadConfig();
      } else {
        msg.className = 'msg err'; msg.textContent = 'Erro ao salvar.';
      }
      setTimeout(() => { msg.className = 'msg'; }, 3000);
    });

    async function testConnection() {
      const msg = document.getElementById('cfg-msg');
      msg.className = 'msg'; msg.textContent = 'Testando...'; msg.style.display = 'block';
      const data = await fetch('/test-connection').then(r => r.json());
      msg.className = data.ok ? 'msg ok' : 'msg err';
      msg.textContent = data.ok ? '✓ Servidor acessível: ' + data.detail : '✗ Falha: ' + data.detail;
      setTimeout(() => { msg.className = 'msg'; }, 5000);
    }

    // ── Leituras ──────────────────────────────────────────────────────────────
    async function loadReadings() {
      const r = await fetch('/readings');
      const container = document.getElementById('readings-container');
      if (r.status === 401) {
        window.location.href = '/login';
        return;
      }
      if (!r.ok) {
        container.innerHTML = '<div class="empty">Sem leituras disponíveis.</div>';
        return;
      }
      const data = await r.json();
      if (data.length > 0) {
        document.getElementById('stat-count').textContent = data.length;
        document.getElementById('stat-kg').textContent = data.reduce((s, r) => s + r.kg_amount, 0).toFixed(1) + ' kg';
        document.getElementById('stat-conf').textContent = (data.reduce((s, r) => s + r.confidence, 0) / data.length * 100).toFixed(0) + '%';
      }
      if (data.length === 0) { container.innerHTML = '<div class="empty">Nenhuma detecção registrada ainda.</div>'; return; }
      const cat = { arroz:'Arroz', feijao:'Feijão', macarrao:'Macarrão', acucar:'Açúcar', cafe:'Café', outros:'Outros' };
      let html = '<table><thead><tr><th>Data/Hora</th><th>Equipe</th><th>Categoria</th><th>Kg</th><th>Confiança</th></tr></thead><tbody>';
      for (const r of data) {
        const pct = Math.round(r.confidence * 100);
        html += `<tr>
          <td>${new Date(r.created_at).toLocaleString('pt-BR')}</td>
          <td>${r.team_name || '—'}</td>
          <td><span class="badge">${cat[r.category] || r.category}</span></td>
          <td>${r.kg_amount.toFixed(2)} kg</td>
          <td>${pct}%<div class="conf-bar"><span style="width:${pct}%"></span></div></td>
        </tr>`;
      }
      html += '</tbody></table>';
      container.innerHTML = html;
    }

    // ── Logout ────────────────────────────────────────────────────────────────
    async function doLogout() {
      await fetch('/logout', { method: 'POST' });
      window.location.href = '/login';
    }

    // ── Init ──────────────────────────────────────────────────────────────────
    loadConfig();
    loadReadings();
    checkCameraStatus();
    setInterval(loadReadings, 15000);
    setInterval(checkCameraStatus, 5000);
  </script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
def login_page():
    return LOGIN_HTML


@app.post("/login")
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
            token = r.json().get("access_token", "")
            cfg["admin_token"] = token
            cfg["admin_email"] = body.get("email", "")
            save_config(cfg)
            return {"ok": True}
        return JSONResponse(status_code=401, content={"ok": False, "detail": "Credenciais inválidas"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "detail": str(e)})


@app.post("/logout")
def do_logout():
    cfg = load_config()
    cfg["admin_token"] = ""
    cfg["admin_email"] = ""
    save_config(cfg)
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def dashboard():
    cfg = load_config()
    if not cfg.get("admin_token"):
        return RedirectResponse(url="/login")
    return DASHBOARD_HTML


@app.get("/config")
def get_config():
    cfg = load_config()
    # nunca expõe campos sensíveis
    return {
        "server_url": cfg.get("server_url", ""),
        "team_id": cfg.get("team_id", 1),
        "admin_email": cfg.get("admin_email", ""),
    }


@app.post("/config")
async def set_config(request: Request):
    body = await request.json()
    cfg = load_config()
    if "server_url" in body:
        cfg["server_url"] = body["server_url"]
    if "team_id" in body:
        cfg["team_id"] = body["team_id"]
    save_config(cfg)
    return {"ok": True}


@app.get("/camera/status")
def camera_status():
    global _camera_process
    return {"running": _camera_process is not None and _camera_process.poll() is None}


@app.post("/camera/start")
def camera_start():
    global _camera_process
    if _camera_process is not None and _camera_process.poll() is None:
        return {"ok": False, "detail": "Câmera já está rodando"}
    cfg = load_config()
    env = os.environ.copy()
    env["SERVER_URL"] = cfg.get("server_url", "")
    env["CAMERA_API_KEY"] = cfg.get("camera_api_key", "")
    env["TEAM_ID"] = str(cfg.get("team_id", 1))
    _camera_process = subprocess.Popen(
        [sys.executable, str(BASE_DIR / "detector.py")],
        env=env, cwd=str(BASE_DIR),
    )
    return {"ok": True, "detail": "Câmera iniciada"}


@app.post("/camera/stop")
def camera_stop():
    global _camera_process
    if _camera_process is None or _camera_process.poll() is not None:
        _camera_process = None
        return {"ok": False, "detail": "Câmera não está rodando"}
    STOP_FILE.write_text("stop")
    _camera_process.wait(timeout=20)
    _camera_process = None
    STOP_FILE.unlink(missing_ok=True)
    return {"ok": True, "detail": "Câmera encerrada"}


@app.post("/camera/finish")
def camera_finish():
    """Para a câmera graciosamente e aguarda todos os envios ao servidor."""
    global _camera_process
    if _camera_process is None or _camera_process.poll() is not None:
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


@app.get("/teams")
def get_teams():
    cfg = load_config()
    try:
        r = requests.get(cfg["server_url"] + "/api/teams", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


@app.get("/test-connection")
def test_connection():
    cfg = load_config()
    try:
        r = requests.get(cfg["server_url"] + "/", timeout=4)
        return {"ok": True, "detail": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "detail": str(e)}


@app.get("/readings")
def get_readings(limit: int = 100):
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
        return r.json() if r.status_code == 200 else JSONResponse(status_code=r.status_code, content={"detail": r.text})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    try:
        model = get_model()
    except FileNotFoundError as e:
        return JSONResponse(status_code=503, content={"detail": str(e)})

    suffix = Path(image.filename or "frame.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(image.file, tmp)
        temp_path = Path(tmp.name)
    try:
        results = model(str(temp_path), conf=CONFIDENCE_THRESHOLD, verbose=False)
        if not results or results[0].boxes is None or len(results[0].boxes) == 0:
            return {"category": "outros", "confidence": 0.0}
        best_box = max(results[0].boxes, key=lambda b: float(b.conf[0].item()))
        cls_id = int(best_box.cls[0].item())
        conf = float(best_box.conf[0].item())
        return {"category": model.names[cls_id], "confidence": round(conf, 4)}
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
