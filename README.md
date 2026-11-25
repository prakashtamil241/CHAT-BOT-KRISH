# Krish AI – Intelligent Python Chatbot 🤖

A modern, responsive AI chatbot web application built with Python, Flask, and Google Gemini API.

## ✨ Features
- 🚀 **Powered by Google Gemini Flash** (`gemini-3.5-flash-lite`, `gemini-3.5-flash`)
- 💬 **Conversation Memory:** Contextual chat history per user session
- 🎨 **Sleek UI:** Dark neon aesthetic with responsive mobile/desktop layout
- 🔑 **Flexible API Key Setup:** Works with `.env` file, environment variables, or directly via the web UI key modal
- ☁️ **Cloud Ready:** Compatible with local execution, Render, Railway, Heroku, etc.

---

## 🛠️ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/prakashtamil241/CHAT-BOT-KRISH.git
cd CHAT-BOT-KRISH
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_actual_google_ai_studio_api_key_here
```
*(You can get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey))*

### 4. Run the chatbot
```bash
python app.py
```

### 5. Open in your browser
Navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**
