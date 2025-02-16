from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import speech_recognition as sr
from pydub import AudioSegment
import random
import fitz  # PyMuPDF for PDF extraction
import docx
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Ensure upload directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load Gemini API Key
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
if not api_key:
    raise ValueError("Error: GOOGLE_GEMINI_API_KEY not found. Set it using export or set command.")
genai.configure(api_key=api_key)

# Load NLP model for resume analysis
nlp = spacy.load("en_core_web_sm")

# Mock Interview Questions
QUESTIONS = [
    "Tell me about yourself.",
    "What are your strengths and weaknesses?",
    "Describe a challenge you've faced at work.",
    "Where do you see yourself in five years?",
    "Why should we hire you?",
    "The interview is complete! Processing your feedback..."
]

# Sample varied feedback
FEEDBACK_OPTIONS = [
    "You have a strong presence and a confident tone! Try elaborating on your answers for more depth.",
    "Great response! To improve, consider adding specific examples to support your points.",
    "Your speech clarity is solid! Next time, try varying your tone to sound more engaging.",
    "You showed good enthusiasm! Consider slowing down slightly for better articulation."
]


### ======== ROUTES ======== ###

# Home Route
@app.route('/')
def home():
    return render_template("index.html")


# Mock Interview Page
@app.route('/mock-interview')
def mock_interview():
    return render_template("mock-interview.html")


# Resume Optimization Page (FIXED)
@app.route('/resume-optimizer')
def resume_optimizer():
    try:
        return render_template("resume-optimizer.html")
    except Exception as e:
        return f"Error rendering template: {e}", 500


# Serve Static Files (CSS, JS, Images)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


### ======== MOCK INTERVIEW API ======== ###

# Get Next Question
@app.route("/get_question/<int:question_index>", methods=["GET"])
def get_question(question_index):
    if question_index < len(QUESTIONS):
        return jsonify({"question": QUESTIONS[question_index], "index": question_index})
    return jsonify({"question": "Interview Complete!", "index": -1})


# Convert audio to WAV format
def convert_audio_to_wav(input_path, output_path):
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        print(f"Audio Conversion Error: {e}")
        return None


# Analyze speech clarity
def analyze_speech(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        clarity_score = min(100, len(text.split()) * 4)
        return {"text": text, "clarity_score": clarity_score}
    except sr.UnknownValueError:
        return {"text": "", "clarity_score": 0}
    except Exception as e:
        return {"text": "", "clarity_score": 0, "error": str(e)}


# Analyze Response & Generate Feedback
@app.route("/analyze_response", methods=["POST"])
def analyze_response():
    if "audio" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400

    audio_file = request.files["audio"]
    raw_audio_path = os.path.join(UPLOAD_FOLDER, "response.webm")
    wav_audio_path = os.path.join(UPLOAD_FOLDER, "response.wav")
    audio_file.save(raw_audio_path)

    converted_audio = convert_audio_to_wav(raw_audio_path, wav_audio_path)
    if not converted_audio:
        return jsonify({"error": "Audio conversion failed."}), 500

    speech_analysis = analyze_speech(wav_audio_path)
    if "error" in speech_analysis:
        return jsonify({"error": "Speech processing failed. Please try again."})

    feedback = random.choice(FEEDBACK_OPTIONS)

    return jsonify({
        "clarity_score": speech_analysis["clarity_score"],
        "final_score": round(speech_analysis["clarity_score"], 1),
        "improvements": feedback
    })


### ======== RESUME OPTIMIZATION API ======== ###

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text.strip()


# Extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()


# Parse Resume Sections
def parse_resume_sections(resume_text):
    sections = {"Education": "", "Experience": "", "Skills": ""}
    lines = resume_text.split("\n")

    for line in lines:
        lower_line = line.lower()
        if "education" in lower_line:
            sections["Education"] += line + "\n"
        elif "experience" in lower_line:
            sections["Experience"] += line + "\n"
        elif "skills" in lower_line:
            sections["Skills"] += line + "\n"

    return {key: value.strip() or "N/A" for key, value in sections.items()}


# Resume Analysis
@app.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files or "job_description" not in request.form:
        return jsonify({"error": "Resume and job description required"}), 400

    file = request.files["resume"]
    job_description = request.form["job_description"]
    file_ext = file.filename.split(".")[-1].lower()
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    if file_ext == "pdf":
        extracted_text = extract_text_from_pdf(file_path)
    elif file_ext == "docx":
        extracted_text = extract_text_from_docx(file_path)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    structured_resume = parse_resume_sections(extracted_text)

    # AI-Powered Gemini Rewrite
    def improve_resume_section(section_name, original_text):
        prompt = f"""
        You are an expert resume writer. Rewrite the '{section_name}' section of the resume
        to better align with the following job description while keeping the original details intact.

        Job Description:
        {job_description}

        Original Resume Section:
        {original_text}

        Improved Resume Section:
        """
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "Error generating improved section."

    improved_resume = {
        "Education": improve_resume_section("Education", structured_resume["Education"]),
        "Experience": improve_resume_section("Experience", structured_resume["Experience"]),
        "Skills": improve_resume_section("Skills", structured_resume["Skills"])
    }

    return jsonify({
        "filename": file.filename,
        "original_resume": structured_resume,
        "improved_resume": improved_resume,
        "analysis": {
            "similarity_score": 85,
            "missing_keywords": ["Python", "Machine Learning"]
        }
    })


### ======== RUN FLASK APP ======== ###
if __name__ == "__main__":
    app.run(debug=True, port=5000)




