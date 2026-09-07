import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

# ==============================
# PATHS
# ==============================

VOC_PATH = Path(
    r"C:\Users\solom\Downloads\Detection-20260907T061426Z-1-001\Detection\VOC2007"
)

IMAGE_PATH = VOC_PATH / "JPEGImages"
ANNOTATION_PATH = VOC_PATH / "Annotations" / "Annotations"

# DocCrop project dataset location
OUTPUT_PATH = Path("datasets/pest_detection")

# ==============================
# CREATE FOLDERS
# ==============================

train_images = OUTPUT_PATH / "images" / "train"
val_images = OUTPUT_PATH / "images" / "val"

train_labels = OUTPUT_PATH / "labels" / "train"
val_labels = OUTPUT_PATH / "labels" / "val"

for folder in [
    train_images,
    val_images,
    train_labels,
    val_labels
]:
    folder.mkdir(parents=True, exist_ok=True)

# ==============================
# READ TRAIN / TEST LISTS
# ==============================

trainval_file = VOC_PATH / "ImageSets" / "Main" / "trainval.txt"
test_file = VOC_PATH / "ImageSets" / "Main" / "test.txt"

with open(trainval_file, "r") as f:
    train_ids = [line.strip() for line in f if line.strip()]

with open(test_file, "r") as f:
    val_ids = [line.strip() for line in f if line.strip()]

print("Train images:", len(train_ids))
print("Validation/Test images:", len(val_ids))

# ==============================
# CONVERT XML → YOLO
# ==============================

def convert_xml_to_yolo(xml_file, output_file):

    tree = ET.parse(xml_file)
    root = tree.getroot()

    size = root.find("size")

    image_width = int(size.find("width").text)
    image_height = int(size.find("height").text)

    yolo_lines = []

    for obj in root.findall("object"):

        class_id = int(obj.find("name").text)

        bbox = obj.find("bndbox")

        xmin = float(bbox.find("xmin").text)
        ymin = float(bbox.find("ymin").text)
        xmax = float(bbox.find("xmax").text)
        ymax = float(bbox.find("ymax").text)

        # Convert VOC → YOLO
        x_center = ((xmin + xmax) / 2) / image_width
        y_center = ((ymin + ymax) / 2) / image_height

        width = (xmax - xmin) / image_width
        height = (ymax - ymin) / image_height

        yolo_lines.append(
            f"{class_id} {x_center:.6f} {y_center:.6f} "
            f"{width:.6f} {height:.6f}"
        )

    with open(output_file, "w") as f:
        f.write("\n".join(yolo_lines))


# ==============================
# PROCESS DATASET
# ==============================

def process_images(image_ids, image_output, label_output):

    processed = 0
    skipped = 0

    for image_id in image_ids:

        image_file = IMAGE_PATH / f"{image_id}.jpg"
        xml_file = ANNOTATION_PATH / f"{image_id}.xml"

        # Skip missing pairs
        if not image_file.exists() or not xml_file.exists():
            skipped += 1
            continue

        # Copy image
        shutil.copy2(
            image_file,
            image_output / image_file.name
        )

        # Create YOLO label
        label_file = label_output / f"{image_id}.txt"

        convert_xml_to_yolo(
            xml_file,
            label_file
        )

        processed += 1

        if processed % 500 == 0:
            print("Processed:", processed)

    return processed, skipped


# ==============================
# TRAIN
# ==============================

print("\nPreparing training dataset...")

train_processed, train_skipped = process_images(
    train_ids,
    train_images,
    train_labels
)

# ==============================
# VALIDATION
# ==============================

print("\nPreparing validation dataset...")

val_processed, val_skipped = process_images(
    val_ids,
    val_images,
    val_labels
)

# ==============================
# RESULT
# ==============================

print("\n================================")
print("DATASET PREPARATION COMPLETE")
print("================================")

print("Training images :", train_processed)
print("Training skipped:", train_skipped)

print("Validation images :", val_processed)
print("Validation skipped:", val_skipped)

print("\nDataset location:")
print(OUTPUT_PATH.resolve())