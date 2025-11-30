import os
from flask import Flask, render_template, request, jsonify

import pytesseract
from PIL import Image
import fitz  # PyMuPDF for PDF text extraction
from joblib import load
import re

app = Flask(__name__)

# ---------------------
# TESSERACT CONFIG
# ---------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------------
# FOLDERS
# ---------------------
UPLOAD_FOLDER = "uploads"
RESULTS_FOLDER = "results"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULTS_FOLDER"] = RESULTS_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


# ---------------------
# TEXT CLEANING
# ---------------------
def clean_text(text: str) -> str:
    """Clean OCR noise and normalize characters."""
    if not text:
        return ""

    # Common OCR errors
    text = text.replace("I", "₹") if "₹" not in text else text
    text = text.replace(" .", ".")
    text = re.sub(r"[^\x00-\x7F]+", " ", text)  # remove weird Unicode
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------
# EXTENSION ALLOW CHECK
# ---------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------
# EXTRACT TEXT FROM FILE
# ---------------------
def extract_text_from_file(filepath: str) -> str:
    _, ext = os.path.splitext(filepath)
    ext = ext.lower().lstrip(".")

    text = ""

    try:
        # --------------------------
        # 📌 PDFs → USE PyMuPDF (NO OCR)
        # --------------------------
        if ext == "pdf":
            with fitz.open(filepath) as doc:
                for page in doc:
                    text += page.get_text()

        # --------------------------
        # 📌 IMAGES → Tesseract OCR
        # --------------------------
        elif ext in {"png", "jpg", "jpeg"}:
            image = Image.open(filepath)
            text = pytesseract.image_to_string(image)

    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

    return clean_text(text)


# ---------------------
# ROUTES
# ---------------------
@app.route("/")
def home():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not (file and allowed_file(file.filename)):
        return jsonify({"error": "Invalid file type"}), 400

    # SAVE FILE
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # --------------------------
    # STEP 1: OCR EXTRACTION
    # --------------------------
    extracted_text = extract_text_from_file(filepath)

    if extracted_text.strip() == "":
        return jsonify({
            "message": "No readable text found",
            "document_type": "unknown",
            "confidence": None,
            "preview_text": ""
        }), 200

    # --------------------------
    # STEP 2: ML PREDICTION
    # --------------------------
    model = load("models/classifier.pkl")
    vectorizer = load("models/vectorizer.pkl")

    features = vectorizer.transform([extracted_text])
    predicted_label = model.predict(features)[0]

    # --------------------------
    # STEP 3: CONFIDENCE SCORE
    # --------------------------
    try:
        decision_scores = model.decision_function(features)[0]
        max_score = max(decision_scores)

        # Normalize score to 0–100
        confidence = (max_score - decision_scores.min()) / (
            decision_scores.max() - decision_scores.min()
        )
        confidence = round(confidence * 100, 2)

    except:
        confidence = None

    # Low confidence fallback
    if confidence is None or confidence < 35:
        predicted_label = "unknown"

    # --------------------------
    # SEND RESPONSE
    # --------------------------
    return jsonify({
        "message": "Classification successful",
        "document_type": predicted_label,
        "confidence": confidence,
        "preview_text": extracted_text[:500]
    }), 200


# ---------------------
# MAIN
# ---------------------
if __name__ == "__main__":
    app.run(debug=True)
