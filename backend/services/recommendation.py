import os
import sys
import importlib.util


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

RECOMMENDATION_FILE = os.path.join(
    PROJECT_ROOT,
    "recommendation",
    "recommendation.py"
)


def load_recommendation_engine():
    spec = importlib.util.spec_from_file_location(
        "docrop_recommendation_engine",
        RECOMMENDATION_FILE
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


recommendation_engine = load_recommendation_engine()


def generate_recommendation(
    crop,
    disease,
    weather=None,
    severity=None
):
    """
    Generate agriculture recommendation
    using the Member 4 recommendation engine.
    """

    return recommendation_engine.get_recommendation(
        crop=crop,
        disease=disease,
        weather=weather,
        severity=severity
    )


if __name__ == "__main__":

    result = generate_recommendation(
        crop="Tomato",
        disease="Early blight",
        weather="warm and humid",
        severity="High"
    )

    print(result)