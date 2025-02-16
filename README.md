# Career Navigator 🚀

Career Navigator is an AI-powered mock interview platform designed to help users improve their interview skills through interactive, real-time feedback. It provides speech analysis, camera-based non-verbal assessment, and detailed reports to enhance interview performance.

## 📌 Features

### 🎙️ AI-Driven Mock Interview
- Simulates real-world interview scenarios with a dynamic AI interviewer.
- Supports **predefined structured questions** covering common interview topics.
- Generates **AI speech responses** using **gTTS (Google Text-to-Speech)**.

### 🎥 Live Camera Analysis
- Captures real-time **video feedback**.
- Provides insights into **non-verbal cues** such as facial expressions and body language.

### 🗣️ Speech and Audio Analysis
- Uses **SpeechRecognition** to transcribe and analyze spoken responses.
- Evaluates **speech clarity**, **coherence**, and **fluency**.
- Converts recorded audio into **WAV format** using **PyDub** for compatibility.

### 📊 Comprehensive Interview Feedback
- Generates **structured reports** with a **final interview score**.
- Provides **actionable suggestions** to improve performance.
- Highlights **speech clarity**, **response coherence**, and **improvement areas**.

---

## 🛠️ Technologies and Frameworks Used

The project leverages a variety of technologies for smooth functionality:

### **Frontend**
- **HTML5 & CSS3**: Provides a clean and user-friendly interface.
- **JavaScript (ES6+)**: Enables dynamic elements and user interactions.
- **Axios**: Handles API requests between frontend and backend.
- **MediaDevices API**: Manages webcam and microphone access for real-time recording.

### **Backend**
- **Python**: Core language for AI-driven functionality.
- **Flask**: A lightweight web framework for backend API development.
- **SpeechRecognition**: Converts audio responses into text for analysis.
- **gTTS (Google Text-to-Speech)**: AI-powered text-to-speech conversion.
- **PyDub**: Handles audio conversion and processing.
- **FFmpeg**: Ensures smooth audio file compatibility.

---

## 🚀 Installation and Setup

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/divakargaba/Career-Navigator.git
cd Career-Navigator
