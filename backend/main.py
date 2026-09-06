from fastapi import FastAPI, UploadFile, File
from backend.database.database import client
import os
import shutil
from datetime import datetime

app = FastAPI(
    title="DocCrop API",
    description="AI-powered Crop Disease and Pest Management System",
    version="1.0.0"
)

# Upload folder
UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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


@app.post("/analyze")
async def analyze_crop(file: UploadFile = File(...)):

    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Save uploaded image
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Temporary demo result
    result = {
        "disease": "Leaf Blight",
        "confidence": 94,
        "pest": "No Major Pest Detected",
        "severity": "Moderate",
        "risk": "High",
        "recommendation": "Follow Integrated Pest Management (IPM) practices."
    }

    # Save analysis in MongoDB
    analysis_data = {
        "image": file_path,
        "filename": file.filename,
        "uploaded_at": datetime.now(),
        **result
    }

    db = client["docrop_db"]
    db["crop_analyses"].insert_one(analysis_data)

    return {
        "status": "success",
        "message": "Crop image analyzed successfully",
        "result": result
    }