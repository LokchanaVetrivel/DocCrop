from pathlib import Path
import json

import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "disease_mobilenetv2.keras"
CLASS_NAMES_PATH = BASE_DIR / "disease_class_names.json"

_model = None
_class_names = None


def _get_model():
    global _model

    if _model is None:
        _model = load_model(MODEL_PATH)

    return _model


def _get_class_names():
    global _class_names

    if _class_names is None:
        with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
            _class_names = json.load(f)

    return _class_names


def detect_disease(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = Image.open(image_path).convert("RGB")
    image = image.resize((224, 224))

    image_array = np.asarray(image, dtype=np.float32)
    image_array = np.expand_dims(image_array, axis=0)

    model = _get_model()
    class_names = _get_class_names()

    predictions = model.predict(image_array, verbose=0)[0]

    predicted_index = int(np.argmax(predictions))
    confidence = float(predictions[predicted_index]) * 100

    predicted_class = class_names[predicted_index]

    return {
        "disease": predicted_class,
        "confidence": round(confidence, 2)
    }