import csv
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(BASE_DIR, "agriculture_knowledge.csv")
DISEASE_FILE = os.path.join(BASE_DIR, "disease.json")
PEST_FILE = os.path.join(BASE_DIR, "pest.json")


def load_disease_data():
    with open(DISEASE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_pest_data():
    with open(PEST_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_agriculture_data():
    with open(CSV_FILE, "r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def get_recommendation(crop, disease, weather=None, severity=None):
    agriculture_data = load_agriculture_data()

    disease_data = load_disease_data()
    pest_data = load_pest_data()

    # Check whether the crop exists
    if crop not in disease_data:
        return {
            "status": "error",
            "message": f"Crop '{crop}' not found in disease database."
        }

    # Check whether the disease exists for the crop
    if disease not in disease_data[crop]:
        return {
            "status": "error",
            "message": f"Disease '{disease}' not found for crop '{crop}'."
        }

    # Search agriculture knowledge
    result = None

    for row in agriculture_data:
        if (
            row["crop"].strip().lower() == crop.strip().lower()
            and row["disease"].strip().lower() == disease.strip().lower()
        ):
            result = row
            break

    if result is None:
        return {
            "status": "error",
            "message": "No agriculture recommendation found."
        }

    # Weather comparison
    weather_note = "Weather information not provided."

    if weather:
        source_weather = result["weather_condition"].lower()
        user_weather = weather.lower()

        if user_weather in source_weather:
            weather_note = (
                "Current weather condition is suitable for disease development. "
                "Follow the recommended treatment and application condition carefully."
            )
        else:
            weather_note = (
                "Current weather does not directly match the listed favourable "
                "condition. Continue monitoring the crop."
            )

    # Severity warning
    severity_warning = "Monitor the crop regularly."

    final_severity = severity if severity else result["severity"]

    if final_severity.lower() == "high":
        severity_warning = (
            "High severity detected. Take action promptly and follow the "
            "recommended agricultural advisory."
        )
    elif final_severity.lower() == "moderate":
        severity_warning = (
            "Moderate severity detected. Monitor the crop closely and follow "
            "the recommended management practices."
        )
    else:
        severity_warning = (
            "Low severity detected. Continue regular crop monitoring and "
            "good agricultural practices."
        )

    # Pest information
    related_pests = pest_data.get(crop, [])

    return {
        "status": "success",
        "crop": result["crop"],
        "disease": result["disease"],
        "severity": final_severity,
        "symptoms": result["symptoms"],
        "weather_condition": result["weather_condition"],
        "current_weather_note": weather_note,
        "treatment": result["treatment"],
        "dosage": result["dosage"],
        "application_condition": result["application_condition"],
        "crop_stage": result["crop_stage"],
        "related_pests": related_pests,
        "warning": severity_warning,
        "source": result["source"]
    }


if __name__ == "__main__":

    # Example test
    recommendation = get_recommendation(
        crop="Tomato",
        disease="Early blight",
        weather="warm and humid",
        severity="High"
)
    

    print(json.dumps(recommendation, indent=4, ensure_ascii=False))