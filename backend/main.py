from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
import cv2
import os

from ai import analyze_report


# --------------------------------------------------
# TESSERACT CONFIGURATION
# --------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="Medical Report Simplifier",
    description="AI-powered medical report understanding system",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# UPLOAD DIRECTORY
# --------------------------------------------------

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Medical Report Simplifier API is running",
        "status": "online"
    }


# --------------------------------------------------
# OCR FUNCTION
# --------------------------------------------------

def extract_text(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image")

    # Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Upscale
    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # Threshold
    processed = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # OCR
    text = pytesseract.image_to_string(
        processed,
        config="--psm 6"
    )

    return text


# --------------------------------------------------
# EXTRACT REPORT
# --------------------------------------------------

@app.post("/extract")
async def extract_report(file: UploadFile = File(...)):

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/jpg"
    ]

    if file.content_type not in allowed_types:
        return {
            "success": False,
            "error": "Please upload a JPG or PNG image."
        }

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    try:

        extracted_text = extract_text(file_path)

        return {
            "success": True,
            "filename": file.filename,
            "text": extracted_text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# --------------------------------------------------
# AI ANALYSIS
# --------------------------------------------------

@app.post("/analyze")
async def analyze_medical_report(data: dict):

    report_text = data.get("text")

    if not report_text:
        return {
            "success": False,
            "error": "No report text provided."
        }

    try:

        analysis = analyze_report(report_text)

        return {
            "success": True,
            "analysis": analysis
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }