from pathlib import Path

import joblib
import pandas as pd

# Path of trained XGBoost model
MODEL_PATH = Path(__file__).resolve().parent / "risk_model.pkl"

_model = None


def _get_model():
    """Load XGBoost model only once."""
    global _model

    if _model is None:
        _model = joblib.load(MODEL_PATH)

    return _model


def predict_risk(data):
    """
    Predict plant disease risk using XGBoost.

    Input:
    {
        "crop": 4,
        "disease": 1,
        "temperature": 30,
        "humidity": 85,
        "rainfall": 70,
        "soil_moisture": 65,
        "pest_severity": 2
    }
    """

    model = _get_model()

    # Convert JSON input into DataFrame
    features = pd.DataFrame([{
        "crop": data["crop"],
        "disease": data["disease"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "rainfall": data["rainfall"],
        "soil_moisture": data["soil_moisture"],
        "pest_severity": data["pest_severity"]
    }])

    prediction = model.predict(features)[0]

    # Prediction probability
    confidence = model.predict_proba(features)[0]
    confidence_score = float(max(confidence)) * 100

    # Convert prediction number into label
    risk_map = {
        0: "High",
        1: "Low",
        2: "Medium"
    }

    return {
        "risk": risk_map[int(prediction)],
        "confidence": round(confidence_score, 2)
    }


# Temporary testing block
if __name__ == "__main__":

    sample_data = {
        "crop": 4,
        "disease": 1,
        "temperature": 30,
        "humidity": 85,
        "rainfall": 70,
        "soil_moisture": 65,
        "pest_severity": 2
    }

    result = predict_risk(sample_data)
    print(result)