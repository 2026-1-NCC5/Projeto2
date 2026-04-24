import os
import csv
import time
import threading
import cv2
import requests
from datetime import datetime
from ultralytics import YOLO

MODEL_PATH = "runs/detect/treino/treino_alimentos/weights/best.pt"
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.60
REQUIRED_FRAMES = 5
COOLDOWN_SECONDS = 3.0

EVIDENCE_DIR = "outputs/evidencias"
LOG_DIR = "outputs/logs"
LOG_FILE = os.path.join(LOG_DIR, "readings.csv")

WINDOW_NAME = "Leitura Automatica - YOLOv8 + OpenCV"

# ── Configuração do servidor ──────────────────────────────────────────────────
SERVER_URL = os.getenv("SERVER_URL", "http://3.80.36.248:8000")
CAMERA_API_KEY = os.getenv("CAMERA_API_KEY", "camera-secret-key")
TEAM_ID = int(os.getenv("TEAM_ID", "1"))
# ─────────────────────────────────────────────────────────────────────────────

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
        writer = csv.writer(f)
        writer.writerow(["timestamp", "category", "confidence", "peso_kg", "evidence_path", "enviado"])

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Modelo não encontrado em: {MODEL_PATH}\n"
        "Treine o YOLO primeiro para gerar o arquivo best.pt."
    )

model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    raise RuntimeError(
        f"Não foi possível abrir a câmera no índice {CAMERA_INDEX}. "
        "Tente trocar CAMERA_INDEX para 1."
    )

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1000, 700)

stable_label = None
stable_count = 0
last_saved_label = None
last_saved_time = 0.0

total_peso = 0.0
total_itens = 0
last_status = ""


def _send_to_server(label: str, conf: float, peso: float, evidence_path: str):
    """Envia leitura ao servidor em background (não bloqueia a câmera)."""
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
            timeout=5,
        )
        if resp.status_code == 200:
            return True
        print(f"[SERVIDOR] Erro {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        print(f"[SERVIDOR] Falha ao enviar: {e}")
        return False


print(f"Câmera iniciada | Servidor: {SERVER_URL} | Equipe ID: {TEAM_ID}")
print("Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Falha ao capturar frame da câmera.")
        break

    results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
    annotated_frame = results[0].plot()

    current_detected_label = None
    current_detected_conf = 0.0

    if len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
        best_box = max(results[0].boxes, key=lambda b: float(b.conf[0].item()))
        cls_id = int(best_box.cls[0].item())
        conf = float(best_box.conf[0].item())
        label = model.names[cls_id]

        current_detected_label = label
        current_detected_conf = conf

        if stable_label == current_detected_label:
            stable_count += 1
        else:
            stable_label = current_detected_label
            stable_count = 1

        if stable_count >= REQUIRED_FRAMES:
            now = time.time()

            if (
                current_detected_label != last_saved_label
                or (now - last_saved_time) > COOLDOWN_SECONDS
            ):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                evidence_filename = f"{current_detected_label}_{timestamp}.jpg"
                evidence_path = os.path.join(EVIDENCE_DIR, evidence_filename)
                cv2.imwrite(evidence_path, frame)

                produto = PRODUCTS.get(current_detected_label, {"peso_kg": 1.0})
                peso = produto["peso_kg"]

                total_peso += peso
                total_itens += 1

                # Envia ao servidor em thread separada
                threading.Thread(
                    target=lambda lbl=current_detected_label, c=current_detected_conf, p=peso, ep=evidence_path: (
                        _send_to_server(lbl, c, p, ep)
                    ),
                    daemon=True,
                ).start()

                # Log local
                with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.now().isoformat(),
                        current_detected_label,
                        f"{current_detected_conf:.4f}",
                        f"{peso:.2f}",
                        evidence_path,
                        "enviando",
                    ])

                last_status = (
                    f"[OK] {current_detected_label} | "
                    f"conf={current_detected_conf:.0%} | "
                    f"{peso:.1f}kg"
                )
                print(last_status)

                last_saved_label = current_detected_label
                last_saved_time = now
                stable_count = 0
    else:
        stable_label = None
        stable_count = 0

    # ── Painel inferior ───────────────────────────────────────────────────────
    panel_width = 360
    panel_height = 85
    frame_height, frame_width = annotated_frame.shape[:2]
    panel_x = int((frame_width - panel_width) / 2)
    panel_y = frame_height - panel_height - 25
    radius = 18
    color = (230, 230, 235)

    overlay = annotated_frame.copy()
    cv2.rectangle(overlay, (panel_x + radius, panel_y), (panel_x + panel_width - radius, panel_y + panel_height), color, -1)
    cv2.rectangle(overlay, (panel_x, panel_y + radius), (panel_x + panel_width, panel_y + panel_height - radius), color, -1)
    for cx, cy in [
        (panel_x + radius, panel_y + radius),
        (panel_x + panel_width - radius, panel_y + radius),
        (panel_x + radius, panel_y + panel_height - radius),
        (panel_x + panel_width - radius, panel_y + panel_height - radius),
    ]:
        cv2.circle(overlay, (cx, cy), radius, color, -1)
    cv2.addWeighted(overlay, 1, annotated_frame, 0, 0, annotated_frame)

    orange = (0, 107, 255)  # BGR para FF6B00
    black = (30, 30, 30)

    cv2.putText(annotated_frame, f"Itens: {total_itens}", (panel_x + 15, panel_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, orange, 2)
    cv2.putText(annotated_frame, f"Peso: {total_peso:.1f} kg", (panel_x + 15, panel_y + 62), cv2.FONT_HERSHEY_SIMPLEX, 0.65, black, 2)
    cv2.putText(annotated_frame, f"Equipe ID: {TEAM_ID}", (panel_x + 200, panel_y + 46), cv2.FONT_HERSHEY_SIMPLEX, 0.6, black, 2)

    cv2.imshow(WINDOW_NAME, annotated_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("Câmera encerrada.")
