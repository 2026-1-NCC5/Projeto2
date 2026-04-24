import os
import csv
import time
import threading
import cv2
import requests
from datetime import datetime
from ultralytics import YOLO

MODEL_PATH = "runs/detect/treino/treino_alimentos/weights/best.pt"
STOP_FILE = ".camera_stop"
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.60
REQUIRED_FRAMES = 5
COOLDOWN_SECONDS = 3.0

EVIDENCE_DIR = "outputs/evidencias"
LOG_DIR = "outputs/logs"
LOG_FILE = os.path.join(LOG_DIR, "readings.csv")

WINDOW_NAME = "Leitura Automatica - YOLOv8 + OpenCV"

SERVER_URL = os.getenv("SERVER_URL", "http://3.80.36.248:8000")
CAMERA_API_KEY = os.getenv("CAMERA_API_KEY", "camera-secret-key")
TEAM_ID = int(os.getenv("TEAM_ID", "1"))

PRODUCTS = {
    "arroz":    {"peso_kg": 5.0},
    "feijao":   {"peso_kg": 1.0},
    "macarrao": {"peso_kg": 0.5},
    "acucar":   {"peso_kg": 1.0},
    "cafe":     {"peso_kg": 0.5},
    "outros":   {"peso_kg": 1.0},
}

os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["timestamp", "category", "confidence", "peso_kg", "evidence_path", "status"])

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modelo não encontrado em: {MODEL_PATH}")

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

# threads pendentes — NÃO são daemon para garantir envio completo ao fechar
_pending_threads: list[threading.Thread] = []


def _send_to_server(label: str, conf: float, peso: float, evidence_path: str, log_row_idx: int):
    status = "erro"
    try:
        resp = requests.post(
            f"{SERVER_URL}/api/camera-readings",
            json={
                "team_id": TEAM_ID,
                "category": label,
                "confidence": round(conf, 4),
                "kg_amount": peso,
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

    # atualiza coluna status no CSV
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

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Falha ao capturar frame.")
        break

    results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
    annotated_frame = results[0].plot().copy()

    current_label = None
    current_conf = 0.0

    if results[0].boxes is not None and len(results[0].boxes) > 0:
        best = max(results[0].boxes, key=lambda b: float(b.conf[0].item()))
        current_label = model.names[int(best.cls[0].item())]
        current_conf = float(best.conf[0].item())

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

                peso = PRODUCTS.get(current_label, {"peso_kg": 1.0})["peso_kg"]
                total_peso += peso
                total_itens += 1

                # log local — guarda índice da linha para atualizar status depois
                with open(LOG_FILE, mode="r", encoding="utf-8") as f:
                    row_idx = sum(1 for _ in f)  # próxima linha = índice atual
                with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow([
                        datetime.now().isoformat(), current_label,
                        f"{current_conf:.4f}", f"{peso:.2f}", evidence_path, "pendente",
                    ])

                print(f"[→] Detectado: {current_label} | {peso:.1f}kg | conf={current_conf:.0%} — enviando...")

                # thread SEM daemon para garantir conclusão ao fechar
                t = threading.Thread(
                    target=_send_to_server,
                    args=(current_label, current_conf, peso, evidence_path, row_idx),
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
    pw, ph, r = 360, 85, 18
    px, py = (fw - pw) // 2, fh - ph - 25
    col = (230, 230, 235)
    ov = annotated_frame.copy()
    cv2.rectangle(ov, (px + r, py), (px + pw - r, py + ph), col, -1)
    cv2.rectangle(ov, (px, py + r), (px + pw, py + ph - r), col, -1)
    for cx, cy in [(px+r,py+r),(px+pw-r,py+r),(px+r,py+ph-r),(px+pw-r,py+ph-r)]:
        cv2.circle(ov, (cx, cy), r, col, -1)
    cv2.addWeighted(ov, 1, annotated_frame, 0, 0, annotated_frame)

    orange, black = (0, 107, 255), (30, 30, 30)
    cv2.putText(annotated_frame, f"Itens: {total_itens}", (px+15, py+30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, orange, 2)
    cv2.putText(annotated_frame, f"Peso: {total_peso:.1f} kg", (px+15, py+62), cv2.FONT_HERSHEY_SIMPLEX, 0.65, black, 2)
    cv2.putText(annotated_frame, f"Equipe ID: {TEAM_ID}", (px+200, py+46), cv2.FONT_HERSHEY_SIMPLEX, 0.6, black, 2)

    cv2.imshow(WINDOW_NAME, annotated_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    if key == ord("s") or os.path.exists(STOP_FILE):
        print("[→] Finalizando sessão...")
        break

cap.release()
cv2.destroyAllWindows()

# aguarda todos os envios pendentes antes de encerrar
if _pending_threads:
    pending = [t for t in _pending_threads if t.is_alive()]
    if pending:
        print(f"[...] Aguardando {len(pending)} envio(s) pendente(s)...")
        for t in pending:
            t.join(timeout=15)

print(f"Câmera encerrada. Total: {total_itens} itens | {total_peso:.1f} kg")
