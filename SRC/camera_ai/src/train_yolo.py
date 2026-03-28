from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="data.yaml",
    epochs=80,
    imgsz=640,
    batch=8,
    patience=15,
    save=True,
    plots=True,
    project="runs/detect",
    name="treino_alimentos",
    pretrained=True
)