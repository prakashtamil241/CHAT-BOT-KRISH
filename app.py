import os
import sys
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# Locate .env based on script directory so it works from anywhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(BASE_DIR, ".env")

if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

SERVER_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]

SYSTEM_PROMPT = (
    "You are Krish AI, a helpful, friendly, and intelligent AI assistant. "
    "Answer questions accurately, clearly, and concisely."
)

chat_histories = {}

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Krish AI</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f0f1a;--surface:#1a1a2e;--panel:#16213e;
  --accent:#7c3aed;--accent2:#a855f7;--accent3:#c084fc;
  --bot-bg:#1e1e3f;--text:#e2e8f0;--muted:#94a3b8;
  --border:#2d2d4e;--input-bg:#1e1e3f;
}
html,body{height:100%;font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text)}
.app{display:flex;flex-direction:column;height:100vh;max-width:900px;margin:0 auto}

header{display:flex;align-items:center;gap:12px;padding:14px 20px;
  background:var(--surface);border-bottom:1px solid var(--border);box-shadow:0 2px 20px rgba(0,0,0,.4)}
.logo{width:40px;height:40px;border-radius:12px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  display:flex;align-items:center;justify-content:center;font-size:20px}
.title-wrap h1{font-size:1.25rem;font-weight:700;
  background:linear-gradient(90deg,var(--accent2),var(--accent3));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.title-wrap p{font-size:.75rem;color:var(--muted);margin-top:2px}
.header-actions{margin-left:auto;display:flex;align-items:center;gap:10px}
.key-btn{background:var(--panel);border:1px solid var(--border);color:var(--accent3);
  padding:6px 12px;border-radius:10px;font-size:.78rem;cursor:pointer;transition:all .2s}
.key-btn:hover{background:var(--accent);color:#fff}
.status-indicator{display:flex;align-items:center;gap:6px;font-size:.75rem;color:#22c55e}
.dot{width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e}

.chat-area{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px;
  scrollbar-width:thin;scrollbar-color:var(--border) transparent}
.chat-area::-webkit-scrollbar{width:6px}
.chat-area::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

.welcome{text-align:center;padding:36px 16px}
.welcome-icon{font-size:3.5rem;margin-bottom:14px}
.welcome h2{font-size:1.6rem;font-weight:700;margin-bottom:8px;
  background:linear-gradient(90deg,var(--accent2),var(--accent3));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.welcome p{color:var(--muted);font-size:.9rem;max-width:440px;margin:0 auto 24px;line-height:1.5}
.chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.chip{background:var(--panel);border:1px solid var(--border);border-radius:18px;
  padding:7px 14px;font-size:.8rem;color:var(--accent3);cursor:pointer;transition:all .2s}
.chip:hover{background:var(--accent);color:#fff;border-color:var(--accent)}

.msg{display:flex;gap:12px;align-items:flex-start}
.msg.user{flex-direction:row-reverse}
.avatar{width:34px;height:34px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:15px}
.avatar.bot{background:linear-gradient(135deg,var(--accent),var(--accent2))}
.avatar.user{background:linear-gradient(135deg,#06b6d4,#3b82f6)}
.bubble{max-width:76%;padding:10px 15px;border-radius:16px;font-size:.92rem;line-height:1.6;word-break:break-word}
.msg.bot .bubble{background:var(--bot-bg);border:1px solid var(--border);border-top-left-radius:4px}
.msg.user .bubble{background:var(--accent);color:#fff;border-top-right-radius:4px}
.bubble pre{background:#0d0d1f;padding:10px;border-radius:8px;overflow-x:auto;margin-top:6px;border:1px solid var(--border)}
.bubble code{background:rgba(0,0,0,.35);padding:2px 5px;border-radius:4px;font-size:.82rem;font-family:monospace}
.bubble pre code{background:none;padding:0}

.typing-dots{display:flex;gap:5px;padding:8px 0}
.typing-dots span{width:7px;height:7px;border-radius:50%;background:var(--accent3);animation:bounce .8s infinite alternate}
.typing-dots span:nth-child(2){animation-delay:.2s}
.typing-dots span:nth-child(3){animation-delay:.4s}
@keyframes bounce{from{transform:translateY(0)}to{transform:translateY(-6px)}}

.input-bar{display:flex;gap:10px;align-items:center;
  padding:14px 20px;background:var(--surface);border-top:1px solid var(--border)}
#userInput{flex:1;background:var(--input-bg);border:1px solid var(--border);border-radius:12px;
  color:var(--text);font-size:.92rem;padding:10px 14px;resize:none;max-height:140px;
  outline:none;line-height:1.4}
#userInput:focus{border-color:var(--accent)}
#sendBtn{width:44px;height:44px;border-radius:50%;border:none;cursor:pointer;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;font-size:18px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
#sendBtn:disabled{opacity:.5;cursor:not-allowed}

/* API Key Modal */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center;z-index:100;padding:20px}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:24px;max-width:440px;width:100%}
.modal h3{margin-bottom:8px;font-size:1.1rem;color:var(--accent3)}
.modal p{font-size:.84rem;color:var(--muted);margin-bottom:16px;line-height:1.4}
.modal input{width:100%;padding:10px 12px;border-radius:10px;background:var(--input-bg);border:1px solid var(--border);color:var(--text);font-size:.88rem;outline:none;margin-bottom:14px}
.modal-actions{display:flex;gap:10px;justify-content:flex-end}
.modal-actions button{padding:8px 16px;border-radius:8px;border:none;cursor:pointer;font-size:.85rem}
.btn-save{background:var(--accent);color:#fff}
.btn-cancel{background:var(--panel);color:var(--muted)}
</style>
</head>
<body>
<div class="app">

  <header>
    <div class="logo">🤖</div>
    <div class="title-wrap">
      <h1>Krish AI</h1>
      <p>Intelligent AI Assistant</p>
    </div>
    <div class="header-actions">
      <button class="key-btn" onclick="openKeyModal()" title="Configure API Key">🔑 Key</button>
      <div class="status-indicator">
        <div class="dot"></div>
        <span>Online</span>
      </div>
    </div>
  </header>

  <div class="chat-area" id="chatArea">
    <div class="welcome" id="welcome">
      <div class="welcome-icon">✨</div>
      <h2>Welcome to Krish AI</h2>
      <p>Ask me anything or choose a suggestion to start!</p>
      <div class="chips">
        <span class="chip" onclick="quickSend('Write a python function to check if a word is palindrome')">🐍 Python code</span>
        <span class="chip" onclick="quickSend('Explain gravity in simple words')">🌍 Science</span>
        <span class="chip" onclick="quickSend('Tell me a short motivational quote')">💡 Motivation</span>
        <span class="chip" onclick="quickSend('How does artificial intelligence work?')">🤖 AI basics</span>
      </div>
    </div>
  </div>

  <div class="input-bar">
    <textarea id="userInput" placeholder="Type a message and press Enter..." rows="1"></textarea>
    <button id="sendBtn" onclick="sendMessage()" title="Send">➤</button>
  </div>

</div>

<!-- Modal for setting custom API key if desired -->
<div class="modal-overlay" id="keyModal">
  <div class="modal">
    <h3>Google Gemini API Key</h3>
    <p>Optional: Paste your API key from Google AI Studio. If left blank, Krish AI uses the server's configured key.</p>
    <input type="password" id="customApiKey" placeholder="AIzaSy... or AQ..."/>
    <div class="modal-actions">
      <button class="btn-cancel" onclick="closeKeyModal()">Cancel</button>
      <button class="btn-save" onclick="saveCustomKey()">Save</button>
    </div>
  </div>
</div>

<script>
const chatArea  = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const sendBtn   = document.getElementById('sendBtn');
const keyModal  = document.getElementById('keyModal');
const customKey = document.getElementById('customApiKey');
const sessionId = 'session_' + Date.now();
let busy = false;

// Pre-fill key if saved
customKey.value = localStorage.getItem('krish_custom_key') || '';

function openKeyModal() { keyModal.style.display = 'flex'; }
function closeKeyModal() { keyModal.style.display = 'none'; }
function saveCustomKey() {
  const val = customKey.value.trim();
  if (val) {
    localStorage.setItem('krish_custom_key', val);
  } else {
    localStorage.removeItem('krish_custom_key');
  }
  closeKeyModal();
}

userInput.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 140) + 'px';
});

userInput.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

function quickSend(text) {
  userInput.value = text;
  sendMessage();
}

function addMsg(role, text) {
  const welcome = document.getElementById('welcome');
  if (welcome) welcome.remove();

  const wrap = document.createElement('div');
  wrap.className = 'msg ' + role;

  const av = document.createElement('div');
  av.className = 'avatar ' + role;
  av.textContent = role === 'bot' ? '🤖' : '👤';

  const bub = document.createElement('div');
  bub.className = 'bubble';
  bub.innerHTML = formatText(text);

  wrap.appendChild(av);
  wrap.appendChild(bub);
  chatArea.appendChild(wrap);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function formatText(raw) {
  return raw
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/```([\s\S]*?)```/g,'<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,'<em>$1</em>')
    .replace(/\n/g,'<br>');
}

function showTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'msg bot';
  wrap.id = 'typingIndicator';
  wrap.innerHTML = '<div class="avatar bot">🤖</div><div class="bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
  chatArea.appendChild(wrap);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function hideTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || busy) return;

  busy = true;
  sendBtn.disabled = true;
  userInput.value = '';
  userInput.style.height = 'auto';
  
  addMsg('user', text);
  showTyping();

  const clientApiKey = localStorage.getItem('krish_custom_key') || '';

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
        api_key: clientApiKey
      }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    const data = await res.json();
    hideTyping();
    if (data.error) {
      addMsg('bot', '⚠️ ' + data.error);
    } else {
      addMsg('bot', data.reply || 'No response.');
    }
  } catch (err) {
    hideTyping();
    if (err.name === 'AbortError') {
      addMsg('bot', '⚠️ Request timed out. Please try again.');
    } else {
      addMsg('bot', '⚠️ Could not connect to server.');
    }
  } finally {
    busy = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "Krish AI Chatbot"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    user_msg = data.get("message", "").strip()
    session_id = data.get("session_id", "default")
    client_key = data.get("api_key", "").strip()

    if not user_msg:
        return jsonify({"error": "Please enter a message."}), 400

    effective_key = client_key or SERVER_API_KEY
    if not effective_key:
        return jsonify({
            "error": "No API key configured. Click 🔑 Key in the header or set GEMINI_API_KEY."
        }), 400

    try:
        client = genai.Client(api_key=effective_key)
    except Exception as e:
        return jsonify({"error": f"Invalid client initialization: {str(e)}"}), 400

    history = chat_histories.get(session_id, [])
    # Limit conversation history to last 20 messages to avoid token bloat
    if len(history) > 20:
        history = history[-20:]

    history.append(types.Content(role="user", parts=[types.Part(text=user_msg)]))

    last_error = ""
    for model_name in MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=history,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            reply = response.text or "I processed your request, but received an empty response."
            history.append(types.Content(role="model", parts=[types.Part(text=reply)]))
            chat_histories[session_id] = history
            return jsonify({"reply": reply})
        except Exception as e:
            last_error = str(e)
            continue

    return jsonify({"error": f"Service temporarily busy ({last_error}). Please try again."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Krish AI server starting on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
