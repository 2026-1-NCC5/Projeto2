import os

BASE_IMAGE_DIR = "dataset/images"
BASE_LABEL_DIR = "dataset/labels"

class_map = {
    "arroz": 0,
    "feijao": 1,
    "outros": 2
}

for split in ["train", "val"]:

    image_split_dir = os.path.join(BASE_IMAGE_DIR, split)
    label_split_dir = os.path.join(BASE_LABEL_DIR, split)

    os.makedirs(label_split_dir, exist_ok=True)

    for category in os.listdir(image_split_dir):

        img_folder = os.path.join(image_split_dir, category)
        label_folder = os.path.join(label_split_dir, category)

        os.makedirs(label_folder, exist_ok=True)

        class_id = class_map[category]

        for img in os.listdir(img_folder):

            if not img.lower().endswith((".jpg", ".png", ".jpeg")):
                continue

            name = os.path.splitext(img)[0]

            label_path = os.path.join(label_folder, name + ".txt")

            with open(label_path, "w") as f:
                f.write(f"{class_id} 0.5 0.5 0.8 0.8")
                
print("Labels gerados para train e val.")