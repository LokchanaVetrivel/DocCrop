def detect_disease(image_path):
    """
    Detect plant disease from the given image.

    Args:
        image_path (str): Path of the uploaded plant image.

    Returns:
        dict: Disease name and confidence.
    """

    result = {
        "disease": "Unknown",
        "confidence": 0
    }

    return result