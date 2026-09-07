from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from backend.database.database import client, db, farmers_collection
from passlib.context import CryptContext
import os
import shutil
from fastapi import HTTPException
from datetime import datetime
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


app = FastAPI(
    title="DocCrop API",
    description="AI-powered Crop Disease and Pest Management System",
    version="1.0.0"
)

# Upload folder
UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve uploaded images
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")


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

        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, JPEG, and PNG images are allowed."
            )

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

        db["crop_analyses"].insert_one(analysis_data)

        return {
            "status": "success",
            "message": "Crop image analyzed successfully",
            "result": result
        }

    except HTTPException:
        raise

    except Exception as e:
        print("ANALYZE ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the crop image."
        )
@app.get("/history")
def get_history():
    analyses = list(
        db["crop_analyses"]
        .find({}, {"_id": 0})
        .sort("uploaded_at", -1)
    )

    for analysis in analyses:
        filename = os.path.basename(analysis["image"])
        analysis["image"] = f"/uploads/{filename}"

    return {
        "status": "success",
        "count": len(analyses),
        "history": analyses
    }
@app.post("/register")
def register_user(username: str, password: str):

    print("1. REGISTER API CALLED")
    print("2. Username:", username)

    # Check whether username already exists
    existing_user = farmers_collection.find_one({"username": username})
    print("3. Database check completed")

    if existing_user:
        return {
            "status": "error",
            "message": "Username already exists"
        }

    print("4. Starting password hashing")

    try:
        hashed_password = pwd_context.hash(password)
        print("5. Password hashing completed")
    except Exception as e:
        print("PASSWORD HASH ERROR:", repr(e))
        return {
            "status": "error",
            "message": str(e)
        }

    user_data = {
        "username": username,
        "password": hashed_password,
        "created_at": datetime.now()
    }

    print("6. Inserting user into MongoDB")

    try:
        farmers_collection.insert_one(user_data)
        print("7. User inserted successfully")
    except Exception as e:
        print("MONGODB INSERT ERROR:", repr(e))
        return {
            "status": "error",
            "message": str(e)
        }

    return {
        "status": "success",
        "message": "User registered successfully"
    }
@app.post("/login")
def login_user(username: str, password: str):

    # Find user by username
    user = farmers_collection.find_one({"username": username})

    if not user:
        return {
            "status": "error",
            "message": "Invalid username or password"
        }

    # Verify password
    if not pwd_context.verify(password, user["password"]):
        return {
            "status": "error",
            "message": "Invalid username or password"
        }

    return {
        "status": "success",
        "message": "Login successful",
        "username": username
    }