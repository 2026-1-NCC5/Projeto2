import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from ultralytics import YOLO

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "runs" / "detect" / "treino_alimentos" / "weights" / "best.pt"
CONFIG_FILE = BASE_DIR / "camera_config.json"
CONFIDENCE_THRESHOLD = 0.60

DEFAULT_CONFIG = {
    "server_url": "http://3.80.36.248:8000",
    "camera_api_key": "camera-secret-key",
    "team_id": 1,
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


# ── YOLO ──────────────────────────────────────────────────────────────────────
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Modelo não encontrado em: {MODEL_PATH}")

model = YOLO(str(MODEL_PATH))

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Camera AI — Lideranças Empáticas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── HTML ──────────────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Camera AI — Lideranças Empáticas</title>
  <style>
    :root { --primary: #FF6B00; --primary-light: #fff3e8; --green: #2E7D32; --red: #c62828; --gray: #f5f5f5; --border: #e0e0e0; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #f0f0f0; color: #222; }
    header { background: var(--primary); color: #fff; padding: 16px 24px; display: flex; align-items: center; gap: 14px; box-shadow: 0 2px 8px rgba(0,0,0,.2); }
    header h1 { font-size: 20px; font-weight: 700; }
    header span { font-size: 12px; opacity: .8; }
    .dot { width: 10px; height: 10px; border-radius: 50%; background: #4caf50; flex-shrink: 0; }
    main { max-width: 1100px; margin: 24px auto; padding: 0 16px; display: grid; gap: 20px; }
    .card { background: #fff; border-radius: 14px; padding: 20px 24px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    .card h2 { font-size: 15px; font-weight: 700; color: var(--primary); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
    .card h2 svg { flex-shrink: 0; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
    .stat-box { background: var(--primary-light); border-radius: 10px; padding: 14px 16px; }
    .stat-box .val { font-size: 26px; font-weight: 800; color: var(--primary); }
    .stat-box .lbl { font-size: 12px; color: #888; margin-top: 2px; }
    form { display: grid; gap: 10px; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    label { font-size: 13px; font-weight: 600; color: #555; }
    input, select { width: 100%; border: 1px solid var(--border); border-radius: 8px; padding: 9px 12px; font-size: 14px; margin-top: 4px; }
    input:focus, select:focus { outline: 2px solid var(--primary); border-color: transparent; }
    button { background: var(--primary); color: #fff; border: none; border-radius: 8px; padding: 11px 20px; font-size: 14px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
    button:hover { opacity: .88; }
    button.secondary { background: #fff; color: var(--primary); border: 2px solid var(--primary); }
    .msg { border-radius: 8px; padding: 10px 14px; font-size: 13px; margin-top: 8px; display: none; }
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
    .btn-row { display: flex; gap: 10px; margin-top: 4px; }
    @media (max-width: 600px) { .row { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <div class="dot" id="dot"></div>
    <div>
      <h1>📷 Camera AI — Lideranças Empáticas</h1>
      <span id="header-team">Carregando configuração...</span>
    </div>
  </header>

  <main>
    <!-- Stats -->
    <div class="card">
      <h2>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
        Resumo da Sessão
      </h2>
      <div class="stats-grid" id="stats">
        <div class="stat-box"><div class="val" id="stat-count">—</div><div class="lbl">Detecções</div></div>
        <div class="stat-box"><div class="val" id="stat-kg">—</div><div class="lbl">Total kg</div></div>
        <div class="stat-box"><div class="val" id="stat-conf">—</div><div class="lbl">Confiança média</div></div>
        <div class="stat-box"><div class="val" id="stat-team">—</div><div class="lbl">Equipe</div></div>
      </div>
    </div>

    <!-- Config -->
    <div class="card">
      <h2>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93A10 10 0 0 0 4.93 19.07M4.93 4.93A10 10 0 0 0 19.07 19.07"/></svg>
        Configuração
      </h2>
      <form id="config-form">
        <div class="row">
          <div>
            <label>URL do Servidor</label>
            <input type="text" id="cfg-server" placeholder="http://3.80.36.248:8000"/>
          </div>
          <div>
            <label>Camera API Key</label>
            <input type="text" id="cfg-key" placeholder="camera-secret-key"/>
          </div>
        </div>
        <div>
          <label>ID da Equipe</label>
          <input type="number" id="cfg-team" placeholder="1" min="1"/>
        </div>
        <div class="btn-row">
          <button type="submit">Salvar configuração</button>
          <button type="button" class="secondary" onclick="testConnection()">Testar conexão</button>
        </div>
        <div class="msg" id="cfg-msg"></div>
      </form>
    </div>

    <!-- Leituras recentes -->
    <div class="card">
      <h2>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        Últimas Detecções
      </h2>
      <div class="btn-row" style="margin-bottom:12px">
        <button onclick="loadReadings()" class="secondary">↻ Atualizar</button>
      </div>
      <div id="readings-container">
        <div class="empty">Carregando...</div>
      </div>
    </div>
  </main>

  <script>
    const API = '';

    async function loadConfig() {
      const r = await fetch(API + '/config');
      const cfg = await r.json();
      document.getElementById('cfg-server').value = cfg.server_url || '';
      document.getElementById('cfg-key').value = cfg.camera_api_key || '';
      document.getElementById('cfg-team').value = cfg.team_id || 1;
      document.getElementById('header-team').textContent = 'Equipe ID: ' + (cfg.team_id || '—') + ' · ' + (cfg.server_url || '');
      document.getElementById('stat-team').textContent = cfg.team_id || '—';
    }

    document.getElementById('config-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const cfg = {
        server_url: document.getElementById('cfg-server').value.trim(),
        camera_api_key: document.getElementById('cfg-key').value.trim(),
        team_id: parseInt(document.getElementById('cfg-team').value),
      };
      const r = await fetch(API + '/config', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(cfg) });
      const msg = document.getElementById('cfg-msg');
      if (r.ok) {
        msg.className = 'msg ok'; msg.textContent = 'Configuração salva com sucesso!';
        loadConfig(); loadReadings();
      } else {
        msg.className = 'msg err'; msg.textContent = 'Erro ao salvar.';
      }
      setTimeout(() => { msg.className = 'msg'; }, 4000);
    });

    async function testConnection() {
      const msg = document.getElementById('cfg-msg');
      msg.className = 'msg'; msg.textContent = 'Testando...'; msg.style.display = 'block';
      const r = await fetch(API + '/test-connection');
      const data = await r.json();
      if (data.ok) {
        msg.className = 'msg ok'; msg.textContent = '✓ Servidor acessível: ' + data.detail;
      } else {
        msg.className = 'msg err'; msg.textContent = '✗ Falha: ' + data.detail;
      }
      setTimeout(() => { msg.className = 'msg'; }, 5000);
    }

    async function loadReadings() {
      const r = await fetch(API + '/readings');
      if (!r.ok) {
        document.getElementById('readings-container').innerHTML = '<div class="empty">Erro ao carregar (verifique servidor e token admin)</div>';
        return;
      }
      const data = await r.json();

      // stats
      if (data.length > 0) {
        const totalKg = data.reduce((s, r) => s + r.kg_amount, 0);
        const avgConf = data.reduce((s, r) => s + r.confidence, 0) / data.length;
        document.getElementById('stat-count').textContent = data.length;
        document.getElementById('stat-kg').textContent = totalKg.toFixed(1) + ' kg';
        document.getElementById('stat-conf').textContent = (avgConf * 100).toFixed(0) + '%';
      }

      if (data.length === 0) {
        document.getElementById('readings-container').innerHTML = '<div class="empty">Nenhuma detecção registrada ainda.</div>';
        return;
      }

      const catLabel = { arroz:'Arroz', feijao:'Feijão', macarrao:'Macarrão', acucar:'Açúcar', cafe:'Café', outros:'Outros' };
      let html = '<table><thead><tr><th>Data/Hora</th><th>Equipe</th><th>Categoria</th><th>Kg</th><th>Confiança</th></tr></thead><tbody>';
      for (const r of data) {
        const d = new Date(r.created_at);
        const dt = d.toLocaleString('pt-BR');
        const pct = Math.round(r.confidence * 100);
        html += `<tr>
          <td>${dt}</td>
          <td>${r.team_name || '—'}</td>
          <td><span class="badge">${catLabel[r.category] || r.category}</span></td>
          <td>${r.kg_amount.toFixed(2)} kg</td>
          <td>
            ${pct}%
            <div class="conf-bar"><span style="width:${pct}%"></span></div>
          </td>
        </tr>`;
      }
      html += '</tbody></table>';
      document.getElementById('readings-container').innerHTML = html;
    }

    loadConfig();
    loadReadings();
    setInterval(loadReadings, 15000);
  </script>
</body>
</html>"""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTML


@app.get("/config")
def get_config():
    return load_config()


@app.post("/config")
async def set_config(request: Request):
    body = await request.json()
    cfg = load_config()
    cfg.update({k: v for k, v in body.items() if k in DEFAULT_CONFIG})
    save_config(cfg)
    return {"ok": True}


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
    """Busca as últimas leituras da câmera no servidor principal."""
    cfg = load_config()
    admin_token = cfg.get("admin_token", "")
    if not admin_token:
        return JSONResponse(
            status_code=400,
            content={"detail": "Configure o admin_token na configuração para visualizar leituras."},
        )
    try:
        r = requests.get(
            cfg["server_url"] + f"/api/camera-readings?limit={limit}",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=6,
        )
        if r.status_code == 200:
            return r.json()
        return JSONResponse(status_code=r.status_code, content={"detail": r.text})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    """Inferência YOLO em uma imagem enviada."""
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
        label = model.names[cls_id]

        return {"category": str(label), "confidence": round(conf, 4)}

    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
