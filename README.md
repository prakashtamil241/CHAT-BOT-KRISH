# Krish AI – Quick Start Guide

## 1. Get a Google AI Studio API Key
1. Go to https://aistudio.google.com/app/apikey
2. Click **Create API Key**
3. Copy the key

## 2. Set your API Key (choose one method)

### Option A – Environment variable (recommended)
```powershell
# Windows PowerShell
$env:GEMINI_API_KEY = "your_actual_key_here"
python app.py
```

### Option B – Edit app.py directly
Open `app.py` and replace line 8:
```python
API_KEY = "your_actual_key_here"
```

## 3. Install dependencies
```bash
pip install flask google-generativeai
```

## 4. Run the bot
```bash
python app.py
```

## 5. Open in browser
Navigate to: **http://127.0.0.1:5000**

---

## Features
- 🤖 Powered by Google Gemini 1.5 Flash
- 💬 Full conversation memory per session
- ⚡ Quick-start chips for common questions
- 🎨 Dark purple gradient UI
- 📱 Responsive design
- ✨ Markdown rendering (code blocks, bold, lists)
- ⌨️ Shift+Enter for newline, Enter to send
