from ultralytics import YOLO
import cv2
import os
from datetime import datetime

MODEL_PATH = "runs/detect/treino_alimentos/weights/best.pt"
EVIDENCE_DIR = "outputs/evidencias"

os.makedirs(EVIDENCE_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Não foi possível abrir a câmera.")

last_saved_label = None
last_saved_time = 0

stable_label = None
stable_count = 0
required_frames = 5

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    annotated_frame = results[0].plot()

    detected_now = False

    for box in results[0].boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        label = model.names[cls_id]

        if conf >= 0.80:
            detected_now = True
            current_time = cv2.getTickCount() / cv2.getTickFrequency()

            # evita salvar várias vezes seguidas o mesmo item
            if label != last_saved_label or (current_time - last_saved_time) > 2.0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(EVIDENCE_DIR, f"{label}_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Leitura válida: {label} | conf={conf:.2f} | salvo em {filename}")
                last_saved_label = label
                last_saved_time = current_time

    cv2.imshow("Leitura Automatica - YOLOv8 + OpenCV", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()