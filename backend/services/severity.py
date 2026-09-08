def calculate_severity(detections, image_width, image_height):
    """
    Estimate pest infestation severity using:
    - Number of detected pests
    - Total area covered by pest bounding boxes

    Severity levels:
    None, Low, Moderate, High
    """

    if not detections:
        return {
            "severity": "None",
            "pest_count": 0,
            "affected_area_percentage": 0.0
        }

    image_area = image_width * image_height

    total_pest_area = 0

    for detection in detections:
        bbox = detection.get("bbox")

        if not bbox or len(bbox) != 4:
            continue

        x1, y1, x2, y2 = bbox

        width = max(0, x2 - x1)
        height = max(0, y2 - y1)

        total_pest_area += width * height

    affected_area_percentage = (
        total_pest_area / image_area
    ) * 100

    pest_count = len(detections)

    # Severity rules
    if pest_count == 0:
        severity = "None"

    elif pest_count <= 2 and affected_area_percentage < 5:
        severity = "Low"

    elif pest_count <= 5 and affected_area_percentage < 10:
        severity = "Moderate"

    else:
        severity = "High"

    return {
        "severity": severity,
        "pest_count": pest_count,
        "affected_area_percentage": round(
            affected_area_percentage, 2
        )
    }