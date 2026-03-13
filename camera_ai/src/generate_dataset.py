import os
import cv2
import numpy as np
from tqdm import tqdm
import random
import shutil

INPUT_DIR = "dataset_base"
OUTPUT_IMAGE_DIR = "dataset/images"
OUTPUT_LABEL_DIR = "dataset/labels"

TRAIN_RATIO = 0.8
IMAGES_PER_INPUT = 6
TARGET_SIZE = 640

CLASS_MAP = {
    "arroz": 0,
    "feijao": 1,
    "outros": 2,
    "acucar": 3,
    "cafe": 4,
}

# bbox inicial presumida para as fotos base:
# objeto aproximadamente centralizado
# formato: [x_min, y_min, x_max, y_max] em pixels
INITIAL_BOX = [0.1, 0.1, 0.9, 0.9]  # em coordenadas relativas


def reset_output_dirs():
    if os.path.exists("dataset"):
        shutil.rmtree("dataset")

    for split in ["train", "val"]:
        os.makedirs(os.path.join(OUTPUT_IMAGE_DIR, split), exist_ok=True)
        os.makedirs(os.path.join(OUTPUT_LABEL_DIR, split), exist_ok=True)


def resize_with_padding(image, target_size=640):
    h, w = image.shape[:2]
    scale = min(target_size / w, target_size / h)

    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(image, (nw, nh))

    canvas = np.full((target_size, target_size, 3), 30, dtype=np.uint8)

    x_offset = (target_size - nw) // 2
    y_offset = (target_size - nh) // 2

    canvas[y_offset:y_offset + nh, x_offset:x_offset + nw] = resized

    return canvas, scale, x_offset, y_offset


def relative_box_to_absolute(box_rel, img_size):
    x1 = int(box_rel[0] * img_size)
    y1 = int(box_rel[1] * img_size)
    x2 = int(box_rel[2] * img_size)
    y2 = int(box_rel[3] * img_size)
    return np.array([
        [x1, y1],
        [x2, y1],
        [x2, y2],
        [x1, y2]
    ], dtype=np.float32)


def polygon_to_yolo_bbox(points, img_size):
    xs = points[:, 0]
    ys = points[:, 1]

    x_min = max(0, xs.min())
    y_min = max(0, ys.min())
    x_max = min(img_size - 1, xs.max())
    y_max = min(img_size - 1, ys.max())

    bw = x_max - x_min
    bh = y_max - y_min

    if bw < 5 or bh < 5:
        return None

    xc = (x_min + x_max) / 2 / img_size
    yc = (y_min + y_max) / 2 / img_size
    w = bw / img_size
    h = bh / img_size

    return xc, yc, w, h


def apply_affine_to_points(points, M):
    ones = np.ones((points.shape[0], 1), dtype=np.float32)
    points_h = np.hstack([points, ones])
    transformed = M @ points_h.T
    return transformed.T


def adjust_brightness_contrast(image):
    alpha = np.random.uniform(0.9, 1.1)
    beta = np.random.randint(-15, 16)
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def maybe_flip(image, points):
    if np.random.rand() < 0.3:
        flipped = cv2.flip(image, 1)
        points[:, 0] = TARGET_SIZE - points[:, 0]
        return flipped, points
    return image, points


def apply_random_transform(image, box_points):
    pts = box_points.copy()

    # rotação leve + escala leve
    angle = np.random.uniform(-8, 8)
    scale = np.random.uniform(0.95, 1.05)
    tx = np.random.randint(-20, 21)
    ty = np.random.randint(-20, 21)

    center = (TARGET_SIZE // 2, TARGET_SIZE // 2)
    M = cv2.getRotationMatrix2D(center, angle, scale)
    M[0, 2] += tx
    M[1, 2] += ty

    transformed_img = cv2.warpAffine(
        image,
        M,
        (TARGET_SIZE, TARGET_SIZE),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(30, 30, 30)
    )

    transformed_pts = apply_affine_to_points(pts, M)

    if np.random.rand() < 0.5:
        transformed_img = adjust_brightness_contrast(transformed_img)

    transformed_img, transformed_pts = maybe_flip(transformed_img, transformed_pts)

    return transformed_img, transformed_pts


def save_sample(img, points, class_id, out_img_path, out_label_path):
    bbox = polygon_to_yolo_bbox(points, TARGET_SIZE)
    if bbox is None:
        return False

    xc, yc, w, h = bbox

    cv2.imwrite(out_img_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])

    with open(out_label_path, "w", encoding="utf-8") as f:
        f.write(f"{class_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")

    return True


def process_category(category):
    class_id = CLASS_MAP[category]
    input_category = os.path.join(INPUT_DIR, category)

    files = [
        f for f in os.listdir(input_category)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]
    random.shuffle(files)

    split_index = int(len(files) * TRAIN_RATIO)
    train_files = files[:split_index]
    val_files = files[split_index:]

    for split_name, split_files in [("train", train_files), ("val", val_files)]:
        out_img_cat = os.path.join(OUTPUT_IMAGE_DIR, split_name, category)
        out_lbl_cat = os.path.join(OUTPUT_LABEL_DIR, split_name, category)
        os.makedirs(out_img_cat, exist_ok=True)
        os.makedirs(out_lbl_cat, exist_ok=True)

        for img_name in tqdm(split_files, desc=f"{category} [{split_name}]"):
            img_path = os.path.join(input_category, img_name)
            image = cv2.imread(img_path)

            if image is None:
                continue

            image, _, _, _ = resize_with_padding(image, TARGET_SIZE)

            box_points = relative_box_to_absolute(INITIAL_BOX, TARGET_SIZE)
            base_name = os.path.splitext(img_name)[0]

            # salva original
            out_img_path = os.path.join(out_img_cat, f"{base_name}_orig.jpg")
            out_lbl_path = os.path.join(out_lbl_cat, f"{base_name}_orig.txt")
            save_sample(image, box_points.copy(), class_id, out_img_path, out_lbl_path)

            # augmentações
            for i in range(IMAGES_PER_INPUT):
                aug_img, aug_pts = apply_random_transform(image.copy(), box_points.copy())

                out_img_path = os.path.join(out_img_cat, f"{base_name}_aug_{i}.jpg")
                out_lbl_path = os.path.join(out_lbl_cat, f"{base_name}_aug_{i}.txt")

                save_sample(aug_img, aug_pts, class_id, out_img_path, out_lbl_path)


def main():
    reset_output_dirs()

    for category in CLASS_MAP.keys():
        input_category = os.path.join(INPUT_DIR, category)
        if not os.path.isdir(input_category):
            print(f"[AVISO] Pasta não encontrada: {input_category}")
            continue
        process_category(category)

    print("Dataset e labels YOLO gerados com sucesso.")


if __name__ == "__main__":
    main()