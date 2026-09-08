from pathlib import Path

from ultralytics import YOLO

from backend.services.severity import calculate_severity


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "runs"
    / "detect"
    / "runs"
    / "pest_detection"
    / "balanced_test"
    / "weights"
    / "best.pt"
)

model = YOLO(str(MODEL_PATH))


def detect_pests(image_path, confidence=0.25):
    results = model.predict(
        source=image_path,
        conf=confidence,
        imgsz=320,
        verbose=False
    )

    detections = []

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])
            conf = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            pest_name = model.names[class_id]

            detections.append({
                "pest_name": pest_name,
                "confidence": round(conf, 4),
                "bbox": [
                    round(x1, 2),
                    round(y1, 2),
                    round(x2, 2),
                    round(y2, 2)
                ]
            })

    return detections


def detect_pests_with_severity(image_path, confidence=0.25):

    results = model.predict(
        source=image_path,
        conf=confidence,
        imgsz=320,
        verbose=False
    )

    detections = []

    image_width = 0
    image_height = 0

    for result in results:

        image_height, image_width = result.orig_shape

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])
            conf = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                "pest_name": model.names[class_id],
                "confidence": round(conf, 4),
                "bbox": [
                    round(x1, 2),
                    round(y1, 2),
                    round(x2, 2),
                    round(y2, 2)
                ]
            })

    severity_result = calculate_severity(
        detections,
        image_width,
        image_height
    )

    return {
        "detections": detections,
        "severity": severity_result
    }