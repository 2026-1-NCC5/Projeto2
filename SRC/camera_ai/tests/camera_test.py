import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Não foi possível abrir a câmera. Tente trocar 0 por 1.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Teste da Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()