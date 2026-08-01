import os
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from detector import PPEDetector
from database import create_database, get_all_alerts


app = FastAPI(
    title="PPE Compliance Monitoring API"
)

# ------------------------------------
# CORS Configuration
# ------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------
# Initialize
# ------------------------------------

create_database()

os.makedirs("uploads", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)

detector = PPEDetector("../model/best.pt")


# ------------------------------------
# Home
# ------------------------------------

@app.get("/")
def home():

    return {
        "message": "PPE Compliance Monitoring API Running"
    }


# ------------------------------------
# Upload Video
# ------------------------------------

@app.post("/upload")
def upload_video(file: UploadFile = File(...)):

    file_path = os.path.join(
        "uploads",
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {

        "message": "Upload Successful",

        "file_name": file.filename

    }


# ------------------------------------
# Process Video
# ------------------------------------

@app.post("/process")
def process_video(file_name: str):

    video_path = os.path.join(
        "uploads",
        file_name
    )

    result = detector.process_video(
        video_path
    )

    return result


# ------------------------------------
# Get Alerts
# ------------------------------------

@app.get("/alerts")
def alerts():

    return {

        "alerts": get_all_alerts()

    }


# ------------------------------------
# Mount Static Files (must be at the end)
# ------------------------------------

# Serve screenshots directory
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")
