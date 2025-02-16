from flask import Flask, request, jsonify, render_template
import os
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS

app = Flask(__name__, static_folder="static", template_folder="templates")

# Ensure upload directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set FFmpeg path for pydub
AudioSegment.converter = "/usr/local/bin/ffmpeg"
AudioSegment.ffmpeg = "/usr/local/bin/ffmpeg"
AudioSegment.ffprobe = "/usr/local/bin/ffprobe"

# Mock interview questions
QUESTIONS = [
    "Welcome to your AI Mock Interview. Click 'Next' to begin.",
    "Tell me about yourself.",
    "What are your strengths and weaknesses?",
    "Describe a challenge you've faced at work.",
    "Where do you see yourself in five years?",
    "Why should we hire you?",
    "The interview is complete! Processing your feedback..."
]

# Generate AI interviewer voice
def generate_question_audio(question):
    tts = gTTS(text=question, lang="en")
    audio_path = os.path.join("static", "question.mp3")
    tts.save(audio_path)
    return audio_path

# Convert audio to WAV PCM (Fixes "RIFF id" error)
def convert_audio_to_wav(input_path, output_path):
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)  # Ensure correct format
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
        clarity_score = min(100, len(text.split()) * 4)  # More words = better clarity score
        return {"text": text, "clarity_score": clarity_score}
    except sr.UnknownValueError:
        return {"text": "", "clarity_score": 0}
    except Exception as e:
        return {"text": "", "clarity_score": 0, "error": str(e)}

# API: Get the next question
@app.route("/get_question/<int:question_index>", methods=["GET"])
def get_question(question_index):
    if question_index < len(QUESTIONS):
        question = QUESTIONS[question_index]
        audio_url = generate_question_audio(question)
        return jsonify({"question": question, "audio_url": audio_url, "index": question_index})
    return jsonify({"question": "Interview Complete!", "audio_url": "", "index": -1})

# API: Analyze Response
@app.route("/analyze_response", methods=["POST"])
def analyze_response():
    if "audio" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400

    audio_file = request.files["audio"]
    raw_audio_path = os.path.join(UPLOAD_FOLDER, "response.webm")
    wav_audio_path = os.path.join(UPLOAD_FOLDER, "response.wav")

    audio_file.save(raw_audio_path)

    # Convert to WAV format
    converted_audio = convert_audio_to_wav(raw_audio_path, wav_audio_path)
    if not converted_audio:
        return jsonify({"error": "Audio conversion failed."}), 500

    speech_analysis = analyze_speech(wav_audio_path)

    if "error" in speech_analysis:
        return jsonify({"error": "Speech processing failed. Please try again."})

    final_score = speech_analysis["clarity_score"]

    return jsonify({
        "clarity_score": speech_analysis["clarity_score"],
        "final_score": round(final_score, 1),
        "improvements": generate_improvements(speech_analysis)
    })

# Generate feedback based on analysis
def generate_improvements(data):
    suggestions = []
    if data["clarity_score"] < 50:
        suggestions.append("Try to speak more clearly and articulate your words.")
    if len(data["text"]) < 10:
        suggestions.append("Try to provide more detailed answers and elaborate your thoughts.")
    if not suggestions:
        return "Great job! You performed well. Continue practicing your responses."
    return " ".join(suggestions)

# Serve Frontend
@app.route("/")
def home():
    return render_template("mock.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)




