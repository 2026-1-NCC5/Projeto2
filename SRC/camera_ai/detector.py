import os
import csv
import json
import math
import time
import threading
from typing import Optional

import cv2
import numpy as np
import requests
from datetime import datetime
from ultralytics import YOLO

# ── Modelo ───────────────────────────────────────────────────────────────────
# Procura best.pt na raiz da pasta primeiro; cai no modelo treinado localmente
_model_candidates = [
    os.getenv("MODEL_PATH", ""),
    "best.pt",
    "runs/detect/treino/treino_alimentos/weights/best.pt",
]
MODEL_PATH = next(
    (p for p in _model_candidates if p and os.path.exists(p)),
    "runs/detect/treino/treino_alimentos/weights/best.pt",
)

STOP_FILE = ".camera_stop"
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.60
REQUIRED_FRAMES = 5
COOLDOWN_SECONDS = 3.0

EVIDENCE_DIR = "outputs/evidencias"
LOG_DIR = "outputs/logs"
LOG_FILE = os.path.join(LOG_DIR, "readings.csv")

WINDOW_NAME = "Leitura Automatica - YOLOv8 + OpenCV"

SERVER_URL = os.getenv("SERVER_URL", "http://54.90.66.229:8000")
CAMERA_API_KEY = os.getenv("CAMERA_API_KEY", "camera-secret-key")
TEAM_ID = int(os.getenv("TEAM_ID", "1"))

# ── Mapeamento de nomes do modelo para categorias do servidor ─────────────────
CATEGORY_MAP = {
    "arroz": "arroz",
    "pacote de arroz": "arroz",
    "feijao": "feijao",
    "feijão": "feijao",
    "pacote de feijao": "feijao",
    "pacote de feijão": "feijao",
    "macarrao": "macarrao",
    "macarrão": "macarrao",
    "pacote de macarrao": "macarrao",
    "pacote de macarrão": "macarrao",
    "acucar": "acucar",
    "açúcar": "acucar",
    "pacote de acucar": "acucar",
    "pacote de açúcar": "acucar",
    "fuba": "fuba",
    "fubá": "fuba",
    "pacote de fuba": "fuba",
    "pacote de fubá": "fuba",
    "oleo": "oleo",
    "óleo": "oleo",
    "garrafa de oleo": "oleo",
    "garrafa de óleo": "oleo",
    "misto": "outros",
    "cafe": "outros",
    "café": "outros",
    "pacote de cafe": "outros",
    "pacote de café": "outros",
}

# Pesos e preços padrão por categoria (usados quando calibração está ausente)
PRODUCTS = {
    "arroz":    {"peso_kg": 5.0,  "price": 28.90},
    "feijao":   {"peso_kg": 1.0,  "price": 8.50},
    "macarrao": {"peso_kg": 0.5,  "price": 4.20},
    "acucar":   {"peso_kg": 1.0,  "price": 4.90},
    "fuba":     {"peso_kg": 1.0,  "price": 3.50},
    "oleo":     {"peso_kg": 0.9,  "price": 7.50},
    "outros":   {"peso_kg": 1.0,  "price": 5.00},
}

# ── Calibração de tamanho ───────────────────────────────────────
# Carrega pontos de calibração do camera_config.json para classificação por tamanho.
# Execute calibrador.py para obter os pontos da sua câmera e adicione-os ao config.
_homography: Optional[np.ndarray] = None
try:
    _cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera_config.json")
    with open(_cfg_path, encoding="utf-8") as _f:
        _cfg_json = json.load(_f)
    if "calibracao" in _cfg_json:
        _cal = _cfg_json["calibracao"]
        _pixels = np.array(_cal["pontos_pixel"], dtype="float32")
        _real_cm = np.array(_cal["pontos_cm"], dtype="float32")
        _homography, _ = cv2.findHomography(_pixels, _real_cm)
        print("[✓] Calibração carregada — classificação por tamanho ativa")
except Exception:
    _homography = None
    print("[!] Calibração não encontrada em camera_config.json — usando pesos padrão")


def _largura_cm(x1: float, y1: float, x2: float, y2: float) -> Optional[float]:
    """Converte largura da bounding box para centímetros via homografia."""
    if _homography is None:
        return None
    base_esq = cv2.perspectiveTransform(
        np.array([[[x1, y2]]], dtype="float32"), _homography
    )[0][0]
    base_dir = cv2.perspectiveTransform(
        np.array([[[x2, y2]]], dtype="float32"), _homography
    )[0][0]
    return math.sqrt(
        (base_dir[0] - base_esq[0]) ** 2 + (base_dir[1] - base_esq[1]) ** 2
    )


def _produto_por_tamanho(label: str, largura: Optional[float]) -> dict:
    """Retorna peso/preço com base no tamanho medido; usa padrão se sem calibração."""
    if largura is None:
        return PRODUCTS.get(label, {"peso_kg": 1.0, "price": 5.00})
    if label == "arroz":
        if largura < 22:  return {"peso_kg": 1.0, "price": 4.50}
        if largura < 27:  return {"peso_kg": 2.0, "price": 9.00}
        return                   {"peso_kg": 5.0, "price": 28.90}
    if label == "feijao":
        if largura < 22:  return {"peso_kg": 1.0, "price": 8.50}
        return                   {"peso_kg": 2.0, "price": 17.00}
    if label == "acucar":
        if largura < 25:  return {"peso_kg": 1.0, "price": 4.90}
        return                   {"peso_kg": 5.0, "price": 24.50}
    if label == "fuba":
        if largura < 22:  return {"peso_kg": 0.5, "price": 2.00}
        return                   {"peso_kg": 1.0, "price": 3.50}
    if label == "oleo":
        if largura < 8:   return {"peso_kg": 0.9, "price": 6.50}
        return                   {"peso_kg": 1.0, "price": 7.50}
    if label == "macarrao":
        return                   {"peso_kg": 0.5, "price": 4.20}
    return PRODUCTS.get(label, {"peso_kg": 1.0, "price": 5.00})


# ── Inicialização ─────────────────────────────────────────────────────────────
os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            ["timestamp", "category", "confidence", "peso_kg", "price", "evidence_path", "status"]
        )

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modelo não encontrado em: {MODEL_PATH}\nExecute: python training/train.py")

model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    raise RuntimeError(f"Não foi possível abrir a câmera no índice {CAMERA_INDEX}.")

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1000, 700)

stable_label = None
stable_count = 0
last_saved_label = None
last_saved_time = 0.0
total_peso = 0.0
total_itens = 0
total_valor = 0.0

_pending_threads: list[threading.Thread] = []


def _send_to_server(
    label: str, conf: float, peso: float, price: float, evidence_path: str, log_row_idx: int
):
    status = "erro"
    try:
        resp = requests.post(
            f"{SERVER_URL}/api/camera-readings",
            json={
                "team_id": TEAM_ID,
                "category": label,
                "confidence": round(conf, 4),
                "kg_amount": peso,
                "price": price,
                "evidence_path": evidence_path,
            },
            headers={"X-Camera-Key": CAMERA_API_KEY},
            timeout=8,
        )
        if resp.status_code == 200:
            status = "enviado"
            print(f"[✓] Enviado ao servidor → {label} | {peso:.1f}kg | conf={conf:.0%}")
        else:
            print(f"[✗] Servidor retornou {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[✗] Falha ao enviar: {e}")

    try:
        with open(LOG_FILE, mode="r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        if log_row_idx < len(rows):
            rows[log_row_idx][-1] = status
        with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
    except Exception:
        pass


print(f"Câmera iniciada | Servidor: {SERVER_URL} | Equipe ID: {TEAM_ID}")
print("Pressione 'q' para sair.")

# ── Loop principal ────────────────────────────────────────────────────────────
while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Falha ao capturar frame.")
        break

    results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
    annotated_frame = results[0].plot().copy()

    current_label = None
    current_conf = 0.0
    _bx1 = _by1 = _bx2 = _by2 = 0.0
    _w_cm: Optional[float] = None

    if results[0].boxes is not None and len(results[0].boxes) > 0:
        best = max(results[0].boxes, key=lambda b: float(b.conf[0].item()))
        raw_label = model.names[int(best.cls[0].item())]
        current_label = CATEGORY_MAP.get(raw_label.lower(), "outros")
        current_conf = float(best.conf[0].item())

        # Medição de tamanho via homografia (Tamanho.py)
        _bx1, _by1, _bx2, _by2 = best.xyxy[0].tolist()
        _w_cm = _largura_cm(_bx1, _by1, _bx2, _by2)

        # Linha de medição na base do objeto (visual Tamanho.py)
        if _homography is not None:
            cv2.line(
                annotated_frame,
                (int(_bx1), int(_by2)), (int(_bx2), int(_by2)),
                (0, 255, 255), 3,
            )
            if _w_cm is not None:
                cv2.putText(
                    annotated_frame,
                    f"{_w_cm:.1f} cm",
                    (int(_bx1), int(_by1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2,
                )

        if stable_label == current_label:
            stable_count += 1
        else:
            stable_label = current_label
            stable_count = 1

        if stable_count >= REQUIRED_FRAMES:
            now = time.time()
            if current_label != last_saved_label or (now - last_saved_time) > COOLDOWN_SECONDS:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                evidence_path = os.path.join(EVIDENCE_DIR, f"{current_label}_{ts}.jpg")
                cv2.imwrite(evidence_path, frame)

                prod = _produto_por_tamanho(current_label, _w_cm)
                peso = prod["peso_kg"]
                price = prod["price"]
                total_peso += peso
                total_itens += 1
                total_valor += price

                with open(LOG_FILE, mode="r", encoding="utf-8") as f:
                    row_idx = sum(1 for _ in f)
                with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow([
                        datetime.now().isoformat(), current_label,
                        f"{current_conf:.4f}", f"{peso:.2f}", f"{price:.2f}",
                        evidence_path, "pendente",
                    ])

                size_info = f" | {_w_cm:.1f}cm" if _w_cm is not None else ""
                print(
                    f"[→] Detectado: {raw_label} → {current_label}"
                    f" | {peso:.1f}kg | R${price:.2f}"
                    f"{size_info} | conf={current_conf:.0%} — enviando..."
                )

                t = threading.Thread(
                    target=_send_to_server,
                    args=(current_label, current_conf, peso, price, evidence_path, row_idx),
                    daemon=False,
                )
                t.start()
                _pending_threads.append(t)

                last_saved_label = current_label
                last_saved_time = now
                stable_count = 0
    else:
        stable_label = None
        stable_count = 0

    # ── Painel inferior ───────────────────────────────────────────────────────
    fh, fw = annotated_frame.shape[:2]
    pw, ph, r = 380, 100, 18
    px, py = (fw - pw) // 2, fh - ph - 25
    col = (230, 230, 235)
    ov = annotated_frame.copy()
    cv2.rectangle(ov, (px + r, py), (px + pw - r, py + ph), col, -1)
    cv2.rectangle(ov, (px, py + r), (px + pw, py + ph - r), col, -1)
    for cx, cy in [(px+r, py+r), (px+pw-r, py+r), (px+r, py+ph-r), (px+pw-r, py+ph-r)]:
        cv2.circle(ov, (cx, cy), r, col, -1)
    cv2.addWeighted(ov, 1, annotated_frame, 0, 0, annotated_frame)

    orange, black = (0, 107, 255), (30, 30, 30)
    cv2.putText(annotated_frame, f"Itens: {total_itens}",
                (px+15, py+26), cv2.FONT_HERSHEY_SIMPLEX, 0.60, orange, 2)
    cv2.putText(annotated_frame, f"Peso: {total_peso:.1f} kg",
                (px+15, py+52), cv2.FONT_HERSHEY_SIMPLEX, 0.55, black, 2)
    cv2.putText(annotated_frame, f"Valor: R${total_valor:.2f}",
                (px+15, py+76), cv2.FONT_HERSHEY_SIMPLEX, 0.55, black, 2)
    cv2.putText(annotated_frame, f"Equipe ID: {TEAM_ID}",
                (px+200, py+52), cv2.FONT_HERSHEY_SIMPLEX, 0.55, black, 2)

    cv2.imshow(WINDOW_NAME, annotated_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    if key == ord("s") or os.path.exists(STOP_FILE):
        print("[→] Finalizando sessão...")
        break

cap.release()
cv2.destroyAllWindows()

if _pending_threads:
    pending = [t for t in _pending_threads if t.is_alive()]
    if pending:
        print(f"[...] Aguardando {len(pending)} envio(s) pendente(s)...")
        for t in pending:
            t.join(timeout=15)

print(f"Câmera encerrada. Total: {total_itens} itens | {total_peso:.1f} kg | R${total_valor:.2f}")
