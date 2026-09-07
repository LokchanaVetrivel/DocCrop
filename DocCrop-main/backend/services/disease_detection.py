from pathlib import Path

import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model


MODEL_PATH = Path(__file__).resolve().parents[2] / "disease_mobilenetv2.keras"

CLASS_NAMES = [
    "Bacteria",
    "Fungi",
    "Healthy",
    "Nematode",
    "Pest",
    "Phytopthora",
    "Virus"
]

_model = None


def _get_model():
    global _model

    if _model is None:
        _model = load_model(MODEL_PATH)

    return _model


def detect_disease(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = Image.open(image_path).convert("RGB")
    image = image.resize((224, 224))

    image_array = np.asarray(image, dtype=np.float32)
    image_array = np.expand_dims(image_array, axis=0)

    model = _get_model()

    predictions = model.predict(image_array, verbose=0)[0]

    predicted_index = int(np.argmax(predictions))
    confidence = float(predictions[predicted_index]) * 100

    return {
        "disease": CLASS_NAMES[predicted_index],
        "confidence": round(confidence, 2)
    }