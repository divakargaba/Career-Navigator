from flask import Flask, request, jsonify, make_response
from flask_cors import CORS  # Add this import
import docx2txt
import fitz  # PyMuPDF for PDFs
import pytesseract
from PIL import Image
import os

app = Flask(__name__)

# Enable CORS for all domains (you can also restrict it to specific origins)
CORS(app)

# Function to extract text from DOCX/PDF
def extract_resume_text(file_path):
    # Extract text logic here (same as before)
    pass

# Function to simulate resume analysis (same as before)
def analyze_resume(text):
    # Analysis logic here (same as before)
    pass

# Resume Upload API
@app.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)

    # Extract text and analyze skills
    resume_text = extract_resume_text(file_path)
    if "Error" in resume_text:
        return jsonify({"error": resume_text}), 400

    skills = analyze_resume(resume_text)
    response = jsonify({
        "skills": skills,
        "resumeText": resume_text,
        "message": "Resume processed successfully"
    })

    return response

if __name__ == "__main__":
    app.run(debug=True, port=5000)



