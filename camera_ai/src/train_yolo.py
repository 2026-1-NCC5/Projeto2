from ultralytics import YOLO

model = YOLO("yolov8s.pt")

model.train(
    data="data.yaml",
    epochs=100,
    imgsz=640,
    batch=8,
    patience=20,
    name="treino_alimentos"
)

