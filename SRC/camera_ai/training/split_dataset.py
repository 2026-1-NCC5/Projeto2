import os
import shutil
import random

IMAGE_DIR = "dataset/images/train"
VAL_DIR = "dataset/images/val"

SPLIT_RATIO = 0.2

for category in os.listdir(IMAGE_DIR):

    category_path = os.path.join(IMAGE_DIR, category)
    val_category_path = os.path.join(VAL_DIR, category)

    os.makedirs(val_category_path, exist_ok=True)

    images = [f for f in os.listdir(category_path)
              if f.lower().endswith((".jpg", ".png", ".jpeg"))]

    random.shuffle(images)

    split_size = int(len(images) * SPLIT_RATIO)

    val_images = images[:split_size]

    for img in val_images:

        src = os.path.join(category_path, img)
        dst = os.path.join(val_category_path, img)

        shutil.move(src, dst)

print("Divisão train/val concluída.")