import os
import csv
import time
import cv2
from datetime import datetime
from ultralytics import YOLO

MODEL_PATH = "runs/detect/treino_alimentos/weights/best.pt"
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.60
REQUIRED_FRAMES = 5
COOLDOWN_SECONDS = 3.0

EVIDENCE_DIR = "outputs/evidencias"
LOG_DIR = "outputs/logs"
LOG_FILE = os.path.join(LOG_DIR, "readings.csv")

WINDOW_NAME = "Leitura Automatica - YOLOv8 + OpenCV"

PRODUCTS = {
    "arroz": {
        "preco": 59.0,
        "peso_kg": 5.0
    },
    "feijao": {
        "preco": 16.0,
        "peso_kg": 1.0
    },
    "outros": {
        "preco": 25.0,
        "peso_kg": 1.0
    },
    "acucar": {
        "preco": 10.0,
        "peso_kg": 1.0
    },
    "cafe": {
        "preco": 45.0,
        "peso_kg": 0.5
    }
}

os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "category", "confidence", "peso_kg", "valor", "evidence_path"])

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Modelo não encontrado em: {MODEL_PATH}\n"
        "Treine o YOLO primeiro para gerar o arquivo best.pt."
    )

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    raise RuntimeError(
        f"Não foi possível abrir a câmera no índice {CAMERA_INDEX}. "
        "Tente trocar CAMERA_INDEX para 1."
    )

stable_label = None
stable_count = 0

last_saved_label = None
last_saved_time = 0.0

total_valor = 0.0
total_peso = 0.0
total_itens = 0

print("Câmera iniciada com sucesso.")
print("Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
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

                produto = PRODUCTS.get(current_detected_label)

                if produto:
                    preco = produto["preco"]
                    peso = produto["peso_kg"]

                    total_valor += preco
                    total_peso += peso
                    total_itens += 1

                    # Gravar log CSV
                    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            datetime.now().isoformat(),
                            current_detected_label,
                            f"{current_detected_conf:.4f}",
                            f"{peso:.2f}",
                            f"{preco:.2f}",
                            evidence_path
                        ])

                    print(
                        f"[OK] Leitura confirmada | "
                        f"classe={current_detected_label} | "
                        f"conf={current_detected_conf:.2f} | "
                        f"peso={peso:.2f}kg | "
                        f"valor=R$ {preco:.2f}"
                    )

                last_saved_label = current_detected_label
                last_saved_time = now
                stable_count = 0
    else:
        stable_label = None
        stable_count = 0

    cv2.rectangle(annotated_frame, (10, 10), (380, 140), (0, 0, 0), -1)

    cv2.putText(
        annotated_frame,
        f"Quantidade: {total_itens}",
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Peso total: {total_peso:.2f} kg",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated_frame,
        f"Valor total: R$ {total_valor:.2f}",
        (20, 115),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    cv2.imshow(WINDOW_NAME, annotated_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("Câmera encerrada.")