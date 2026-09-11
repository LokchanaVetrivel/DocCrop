import os
import shutil
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.services.pest_detection import detect_pests_with_severity
from backend.services.recommendation import generate_recommendation

# ============================================================
# APP INITIALIZATION
# ============================================================

app = FastAPI(
    title="DocCrop API",
    description="AI-based crop disease, pest detection and recommendation system",
    version="1.0.0"
)

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# MONGODB
# ============================================================

try:
    from pymongo import MongoClient

    MONGO_URL = "mongodb://localhost:27017"

    client = MongoClient(
        MONGO_URL,
        serverSelectionTimeoutMS=3000
    )

    client.admin.command("ping")

    db = client["doccrop"]

    print("MongoDB connected successfully!")

except Exception as e:
    print("MongoDB connection failed:", repr(e))
    db = None

# ============================================================
# UPLOAD FOLDER
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

# ============================================================
# BASIC ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "DocCrop API is running"
    }


# ============================================================
# ANALYZE CROP IMAGE
# ============================================================

@app.post("/analyze")
async def analyze_crop(
    file: UploadFile = File(...)
):

    try:

        # ====================================================
        # VALIDATE UPLOADED FILE
        # ====================================================

        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png"
        ]

        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

        file_extension = os.path.splitext(
            file.filename
        )[1].lower()

        if file_extension not in allowed_extensions:

            raise HTTPException(
                status_code=400,
                detail="Only JPG, JPEG and PNG files are allowed."
            )

        # ====================================================
        # VALIDATE FILE SIZE
        # ====================================================

        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:

            raise HTTPException(
                status_code=400,
                detail="File size must be less than 5 MB."
            )

        # Reset file pointer
        await file.seek(0)

        # ====================================================
        # SAVE UPLOADED IMAGE
        # ====================================================

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = f"{timestamp}_{file.filename}"

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # ====================================================
        # PEST DETECTION + SEVERITY
        # ====================================================

        pest_result = detect_pests_with_severity(
            file_path,
            confidence=0.15
        )

        detections = pest_result["detections"]

        severity_result = pest_result["severity"]

        # ====================================================
        # GET PEST NAME
        # ====================================================

        if detections:

            pest_names = list(
                dict.fromkeys(
                    detection["pest_name"]
                    for detection in detections
                )
            )

            pest = ", ".join(
                pest_names
            )

        else:

            pest = "No Major Pest Detected"

        # ====================================================
        # TEMPORARY DISEASE / RISK DATA
        # ====================================================
        #
        # These are currently placeholders from the
        # integration version.
        #
        # Disease model and risk model can be connected here
        # later.
        #

        crop = "Tomato"

        disease = "Early blight"

        confidence = 94.0

        risk = "High"

        weather = "warm and humid"

        # ====================================================
        # RECOMMENDATION
        # ====================================================

        recommendation = generate_recommendation(
            crop=crop,
            disease=disease,
            weather=weather,
            severity=severity_result["severity"]
        )

        # ====================================================
        # FINAL ANALYSIS RESULT
        # ====================================================

        result = {

            "crop": crop,

            "disease": disease,

            "confidence": confidence,

            "pest": pest,

            "severity":
                severity_result["severity"],

            "risk": risk,

            "weather": weather,

            "recommendation":
                recommendation,

            "affected_area_percentage":
                severity_result[
                    "affected_area_percentage"
                ],

            "pest_detections":
                detections
        }

        # ====================================================
        # SAVE ANALYSIS IN MONGODB
        # ====================================================

        mongodb_status = "not_saved"

        if db is not None:

            try:

                analysis_data = {

                    "image": file_path,

                    "filename": file.filename,

                    "uploaded_at":
                        datetime.now(),

                    **result
                }

                db[
                    "crop_analyses"
                ].insert_one(
                    analysis_data
                )

                mongodb_status = "saved"

            except Exception as db_error:

                print(
                    "MongoDB SAVE ERROR:",
                    repr(db_error)
                )

                mongodb_status = "not_saved"

        # ====================================================
        # RETURN RESPONSE
        # ====================================================

        return {

            "status": "success",

            "message":
                "Crop image analyzed successfully",

            "mongodb":
                mongodb_status,

            "result":
                result
        }

    # ========================================================
    # HTTP EXCEPTION
    # ========================================================

    except HTTPException:
        raise

    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception as e:

        print(
            "ANALYZE ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
async def login():

    # Temporary login response
    # Replace with actual authentication later.

    return {

        "status": "success",

        "message":
            "Login successful",

        "username":
            "user"
    }