
from fastapi import FastAPI
from backend.database.database import client

app = FastAPI(
    title="DocCrop API",
    description="AI-powered Crop Disease and Pest Management System",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "DocCrop API is running!"
    }


@app.get("/health")
def health_check():
    try:
        client.admin.command("ping")

        return {
            "status": "success",
            "mongodb": "connected"
        }

    except Exception as e:
        return {
            "status": "error",
            "mongodb": "disconnected",
            "error": str(e)
        }