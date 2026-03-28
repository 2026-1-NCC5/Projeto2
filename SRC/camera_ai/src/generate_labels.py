import os
import cv2
import numpy as np

BASE_IMAGE_DIR = "dataset/images"
BASE_LABEL_DIR = "dataset/labels"

CLASS_MAP = {
    "arroz": 0,
    "feijao": 1,
    "outros": 2,
    "cafe": 3,
    "acucar": 4
}

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png")


def normalize_bbox(x, y, w, h, img_w, img_h):
    x_center = (x + w / 2) / img_w
    y_center = (y + h / 2) / img_h
    width = w / img_w
    height = h / img_h
    return x_center, y_center, width, height


def largest_contour_bbox(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    contour = max(contours, key=cv2.contourArea)

    if cv2.contourArea(contour) < 500:
        return None

    return cv2.boundingRect(contour)


def try_threshold_fallback(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold invertido
    _, thresh1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    bbox1 = largest_contour_bbox(thresh1)

    # Threshold normal
    _, thresh2 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bbox2 = largest_contour_bbox(thresh2)

    # Canny
    edges = cv2.Canny(blur, 50, 150)
    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=2)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    bbox3 = largest_contour_bbox(edges)

    candidates = [b for b in [bbox1, bbox2, bbox3] if b is not None]

    if not candidates:
        return None

    return max(candidates, key=lambda b: b[2] * b[3])


def pad_bbox(x, y, w, h, img_w, img_h, pad_ratio=0.03):
    pad_w = int(w * pad_ratio)
    pad_h = int(h * pad_ratio)

    x = max(0, x - pad_w)
    y = max(0, y - pad_h)
    w = min(img_w - x, w + 2 * pad_w)
    h = min(img_h - y, h + 2 * pad_h)

    return x, y, w, h


def generate_label_for_image(img_path, label_path, class_id):
    image = cv2.imread(img_path)

    if image is None:
        print(f"Erro ao ler imagem: {img_path}")
        return False

    img_h, img_w = image.shape[:2]

    bbox = try_threshold_fallback(image)

    # 🔵 CASO 1: não detectou nada → fallback
    if bbox is None:
        x_center, y_center, width, height = 0.5, 0.5, 0.8, 0.8

        with open(label_path, "w", encoding="utf-8") as f:
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        print(f"Fallback aplicado em: {img_path}")
        return True

    x, y, w, h = bbox

    area_ratio = (w * h) / (img_w * img_h)

    # 🔵 CASO 2: bbox inválida → fallback
    if area_ratio < 0.02 or area_ratio > 0.98:
        x_center, y_center, width, height = 0.5, 0.5, 0.8, 0.8

        with open(label_path, "w", encoding="utf-8") as f:
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        print(f"Fallback por bbox inválida em: {img_path} | area_ratio={area_ratio:.3f}")
        return True

    # 🔵 CASO 3: bbox válida
    x, y, w, h = pad_bbox(x, y, w, h, img_w, img_h)

    x_center, y_center, width, height = normalize_bbox(x, y, w, h, img_w, img_h)

    with open(label_path, "w", encoding="utf-8") as f:
        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    return True


def main():
    total = 0
    success = 0

    for split in ["train", "val"]:
        image_split_dir = os.path.join(BASE_IMAGE_DIR, split)
        label_split_dir = os.path.join(BASE_LABEL_DIR, split)

        if not os.path.exists(image_split_dir):
            print(f"Pasta não encontrada: {image_split_dir}")
            continue

        os.makedirs(label_split_dir, exist_ok=True)

        for category in sorted(os.listdir(image_split_dir)):
            category_path = os.path.join(image_split_dir, category)

            if not os.path.isdir(category_path):
                continue

            if category not in CLASS_MAP:
                print(f"Categoria ignorada: {category}")
                continue

            class_id = CLASS_MAP[category]

            label_category_path = os.path.join(label_split_dir, category)
            os.makedirs(label_category_path, exist_ok=True)

            for file_name in sorted(os.listdir(category_path)):
                if not file_name.lower().endswith(VALID_EXTENSIONS):
                    continue

                total += 1

                img_path = os.path.join(category_path, file_name)
                txt_name = os.path.splitext(file_name)[0] + ".txt"
                label_path = os.path.join(label_category_path, txt_name)

                if generate_label_for_image(img_path, label_path, class_id):
                    success += 1

    print(f"\nLabels gerados com sucesso: {success}/{total}")


if __name__ == "__main__":
    main()