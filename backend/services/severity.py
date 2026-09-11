def calculate_severity(detections, image_width, image_height):

    if not detections or image_width <= 0 or image_height <= 0:
        return {
            "severity": "None",
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

    # Severity based ONLY on affected area
    if affected_area_percentage == 0:

        severity = "None"

    elif affected_area_percentage < 5:

        severity = "Low"

    elif affected_area_percentage < 10:

        severity = "Moderate"

    else:

        severity = "High"

    return {
        "severity": severity,
        "affected_area_percentage":
            round(affected_area_percentage, 2)
    }