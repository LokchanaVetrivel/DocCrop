def get_recommendation(disease: str, severity: str, risk: str):
    """
    Returns recommendation based on disease,
    severity, and risk level.
    """

    recommendations = {

        "Bacteria": {
            "Low": "Remove affected leaves and maintain proper field sanitation.",
            "Moderate": "Remove infected plant parts and apply suitable bacterial disease control measures.",
            "High": "Immediately isolate severely affected plants, remove infected parts, and apply appropriate bacterial disease management."
        },

        "Fungi": {
            "Low": "Remove affected leaves and improve air circulation around the plants.",
            "Moderate": "Remove infected plant parts and apply a suitable fungicide as recommended.",
            "High": "Remove severely infected plants or parts and apply appropriate fungal disease control measures immediately."
        },

        "Healthy": {
            "Low": "Your plant is healthy. Continue regular watering and proper crop maintenance.",
            "Moderate": "The plant appears healthy. Continue monitoring for possible disease symptoms.",
            "High": "Continue regular monitoring and maintain proper crop care practices."
        },

        "Nematode": {
            "Low": "Monitor the crop regularly and maintain proper soil and field sanitation.",
            "Moderate": "Remove severely affected plants and use suitable nematode management practices.",
            "High": "Take immediate nematode control measures and consider appropriate soil treatment as recommended."
        },

        "Pest": {
            "Low": "Monitor the crop regularly for pest activity and remove affected plant parts.",
            "Moderate": "Remove heavily affected parts and apply suitable pest management measures.",
            "High": "Take immediate pest control measures and follow Integrated Pest Management practices."
        },

        "Phytopthora": {
            "Low": "Remove affected plant parts and avoid excessive watering or water stagnation.",
            "Moderate": "Improve drainage, remove infected parts, and apply a suitable treatment as recommended.",
            "High": "Immediately remove severely infected plants, improve drainage, and apply appropriate disease control measures."
        },

        "Virus": {
            "Low": "Remove visibly affected leaves and monitor the plant regularly for symptom development.",
            "Moderate": "Remove infected plants or parts and control insect vectors to reduce virus spread.",
            "High": "Immediately isolate and remove severely infected plants and control insect vectors to prevent further spread."
        }
    }

    # Disease-specific recommendation
    if disease in recommendations:
        if severity in recommendations[disease]:
            return recommendations[disease][severity]

    # General recommendation based on risk
    if risk == "High":
        return "Immediate action is recommended. Inspect the crop and apply suitable Integrated Pest Management practices."

    elif risk == "Moderate":
        return "Monitor the crop closely and take preventive measures to control disease spread."

    else:
        return "Continue regular crop monitoring and follow good agricultural practices."