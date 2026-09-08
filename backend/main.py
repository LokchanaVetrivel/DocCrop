from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from backend.database.database import client, db, farmers_collection
from backend.services.pest_detection import detect_pests_with_severity
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime
import os
import shutil


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


app = FastAPI(
    title="DocCrop API",
    description="AI-powered Crop Disease and Pest Management System",
    version="1.0.0"
)


class UserRequest(BaseModel):
    username: str
    password: str


# Upload folder
UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Serve uploaded images
app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_FOLDER),
    name="uploads"
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


@app.post("/analyze")
async def analyze_crop(file: UploadFile = File(...)):

    try:
        # Validate uploaded file
        allowed_extensions = [".jpg", ".jpeg", ".png"]
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, JPEG, and PNG images are allowed."
            )

        # Validate file size
        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File size must be less than 5 MB."
            )

        # Reset file position
        await file.seek(0)

        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        # Save uploaded image
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ==========================================
        # PEST DETECTION + SEVERITY DETECTION
        # ==========================================

        pest_result = detect_pests_with_severity(
            file_path,
            confidence=0.25
        )

        detections = pest_result["detections"]
        severity_result = pest_result["severity"]

        # ==========================================
        # FORMAT PEST RESULT
        # ==========================================

        if detections:

            pest_names = list(
                dict.fromkeys(
                    detection["pest_name"]
                    for detection in detections
                )
            )

            pest = ", ".join(pest_names)

        else:
            pest = "No Major Pest Detected"

        # ==========================================
        # FINAL RESULT
        # ==========================================

        result = {

            # Temporary disease result
            "disease": "Leaf Blight",
            "confidence": 94,

            # Actual pest detection
            "pest": pest,

            # Actual severity estimation
            "severity": severity_result["severity"],

            # Temporary risk result
            "risk": "High",

            # Temporary recommendation
            "recommendation":
                "Follow Integrated Pest Management (IPM) practices.",

            # Pest information
            "pest_count": severity_result["pest_count"],

            "affected_area_percentage":
                severity_result["affected_area_percentage"],

            "pest_detections": detections
        }

        # ==========================================
        # SAVE ANALYSIS IN MONGODB
        # ==========================================

        analysis_data = {

            "image": file_path,

            "filename": file.filename,

            "uploaded_at": datetime.now(),

            **result
        }

        db["crop_analyses"].insert_one(
            analysis_data
        )

        # ==========================================
        # API RESPONSE
        # ==========================================

        return {
            "status": "success",
            "message": "Crop image analyzed successfully",
            "result": result
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            "ANALYZE ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the crop image."
        )


@app.get("/history")
def get_history():

    try:

        analyses = list(
            db["crop_analyses"]
            .find({}, {"_id": 0})
            .sort("uploaded_at", -1)
        )

        for analysis in analyses:

            filename = os.path.basename(
                analysis["image"]
            )

            analysis["image"] = f"/uploads/{filename}"

        return {
            "status": "success",
            "count": len(analyses),
            "history": analyses
        }

    except Exception as e:

        print(
            "HISTORY ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving analysis history."
        )


@app.post("/register")
def register_user(user: UserRequest):

    # Check whether username already exists
    existing_user = farmers_collection.find_one(
        {"username": user.username}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Hash password
    hashed_password = pwd_context.hash(
        user.password
    )

    # Create user document
    user_data = {
        "username": user.username,
        "password": hashed_password,
        "created_at": datetime.now()
    }

    # Save user to MongoDB
    farmers_collection.insert_one(
        user_data
    )

    return {
        "status": "success",
        "message": "User registered successfully"
    }


@app.post("/login")
def login_user(user: UserRequest):

    # Find user by username
    existing_user = farmers_collection.find_one(
        {"username": user.username}
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Verify password
    if not pwd_context.verify(
        user.password,
        existing_user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return {
        "status": "success",
        "message": "Login successful",
        "username": user.username
    }