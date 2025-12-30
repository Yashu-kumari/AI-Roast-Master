from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import shutil
import os
from pathlib import Path

try:
    from image_analyzer import ImageAnalyzer
except ImportError:
    class ImageAnalyzer:
        def analyze_photo(self, path):
            return {'faces': {'count': 1}, 'objects': {}, 'colors': {'theme': 'mixed'}, 'composition': {'resolution': 'medium'}}

try:
    from roast_generator import RoastGenerator
except ImportError:
    class RoastGenerator:
        def generate_roast(self, features, style):
            return "I'd roast you, but I'm having technical difficulties. At least that's more functional than this photo!"
        def generate_comeback(self, message):
            return "That's what they all say!"
        def create_standup_routine(self, features):
            return ["I'd tell you a joke, but my comedy module is broken!", "Just like this photo!"]
        def chat_response(self, message, context):
            responses = [
                "Oh, you want to chat? How adorable! 😏",
                "I'm here to roast, not to be your therapist! 🔥",
                "That's... actually not terrible. Are you feeling okay? 🤔",
                "I've heard funnier things from a broken calculator! 😂"
            ]
            return responses[len(message) % len(responses)]

app = FastAPI(title="AI Roast Master", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    analyzer = ImageAnalyzer()
    roast_gen = RoastGenerator()
except Exception as e:
    print(f"Warning: Could not initialize components: {e}")
    analyzer = ImageAnalyzer()
    roast_gen = RoastGenerator()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """<!DOCTYPE html>
<html>
<head>
    <title>AI Roast Master</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: white; overflow-x: hidden;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 15px; text-align: center; }
        .header { margin-bottom: 30px; }
        .header h1 { font-size: clamp(2rem, 8vw, 3.5rem); margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: clamp(1rem, 3vw, 1.2rem); opacity: 0.9; }
        .main-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: clamp(20px, 5vw, 40px); margin: 15px 0; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .upload-zone { border: 3px dashed rgba(255,255,255,0.3); border-radius: 15px; padding: clamp(30px, 8vw, 60px) 20px; margin: 20px 0; transition: all 0.3s ease; cursor: pointer; touch-action: manipulation; }
        .upload-zone:hover { border-color: rgba(255,255,255,0.6); background: rgba(255,255,255,0.05); }
        .file-input { display: none; }
        .upload-text { font-size: 1.3rem; margin-bottom: 15px; }
        .upload-subtext { opacity: 0.7; font-size: 0.9rem; }
        .style-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 25px 0; }
        .style-btn { padding: clamp(12px, 3vw, 15px) clamp(15px, 4vw, 25px); border: none; border-radius: 12px; font-size: clamp(0.85rem, 2.5vw, 1rem); font-weight: 600; cursor: pointer; transition: all 0.3s ease; opacity: 0.7; transform: scale(0.95); touch-action: manipulation; min-height: 48px; }
        .style-btn.active { opacity: 1; transform: scale(1); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .savage { background: linear-gradient(45deg, #ff4757, #ff3742); color: white; }
        .playful { background: linear-gradient(45deg, #2ed573, #17c0eb); color: white; }
        .sarcastic { background: linear-gradient(45deg, #ffa502, #ff6348); color: white; }
        .absurd { background: linear-gradient(45deg, #3742fa, #2f3542); color: white; }
        .roast-btn { background: linear-gradient(45deg, #ff6b6b, #ee5a52); color: white; border: none; padding: clamp(15px, 4vw, 18px) clamp(25px, 6vw, 40px); font-size: clamp(1rem, 3vw, 1.2rem); font-weight: 700; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; margin: 20px 0; box-shadow: 0 5px 15px rgba(255,107,107,0.4); touch-action: manipulation; min-height: 48px; width: 100%; max-width: 300px; }
        .roast-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255,107,107,0.6); }
        .roast-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .result-card { background: rgba(255,255,255,0.15); border-radius: 15px; padding: clamp(20px, 5vw, 30px); margin: 25px 0; border-left: 5px solid #ff6b6b; text-align: left; display: none; }
        .result-card h3 { color: #ff6b6b; margin-bottom: 15px; font-size: clamp(1.2rem, 3.5vw, 1.4rem); }
        .roast-text { font-size: clamp(1rem, 2.8vw, 1.1rem); line-height: 1.6; margin-bottom: 20px; font-style: italic; }
        .chat-area { background: rgba(255,255,255,0.1); border-radius: 15px; padding: clamp(20px, 5vw, 30px); margin: 25px 0; }
        .chat-input { width: 100%; padding: clamp(12px, 3vw, 15px); border: none; border-radius: 25px; font-size: clamp(0.9rem, 2.5vw, 1rem); background: rgba(255,255,255,0.2); color: white; margin-bottom: 15px; min-height: 48px; }
        .chat-input::placeholder { color: rgba(255,255,255,0.7); }
        .chat-messages { max-height: 300px; overflow-y: auto; margin-bottom: 15px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 15px; }
        .chat-message { margin: 10px 0; padding: 10px 15px; border-radius: 20px; max-width: 80%; animation: fadeIn 0.3s ease; }
        .user-message { background: linear-gradient(45deg, #667eea, #764ba2); margin-left: auto; text-align: right; }
        .ai-message { background: linear-gradient(45deg, #ff6b6b, #ee5a52); margin-right: auto; }
        .chat-input-container { display: flex; gap: 10px; margin-bottom: 15px; }
        .chat-send-btn { background: linear-gradient(45deg, #ff6b6b, #ee5a52); color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600; transition: all 0.3s; }
        .chat-send-btn:hover { transform: translateY(-2px); }
        .chat-suggestions { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 15px; }
        .suggestion-btn { background: rgba(255,255,255,0.1); color: white; border: none; padding: 8px 15px; border-radius: 20px; cursor: pointer; font-size: 0.9rem; transition: all 0.3s; }
        .suggestion-btn:hover { background: rgba(255,255,255,0.2); transform: translateY(-2px); }
        .loading { display: none; margin: 20px 0; }
        .spinner { border: 3px solid rgba(255,255,255,0.3); border-top: 3px solid #ff6b6b; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .footer { margin-top: 40px; opacity: 0.7; font-size: clamp(0.8rem, 2vw, 0.9rem); padding: 0 10px; }
        .nav { text-align: center; margin-bottom: 30px; }
        .nav a { color: white; text-decoration: none; margin: 0 15px; padding: 10px 20px; border-radius: 25px; background: rgba(255,255,255,0.1); transition: all 0.3s; }
        .nav a:hover { background: rgba(255,255,255,0.2); }
        @media (max-width: 768px) { .container { padding: 10px; } .style-grid { grid-template-columns: 1fr 1fr; gap: 10px; } }
        @media (max-width: 480px) { .style-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <a href="/">🏠 Home</a>
            <a href="/about">ℹ️ About</a>
            <a href="/gallery">🖼️ Gallery</a>
            <a href="/contact">📞 Contact</a>
        </nav>
        
        <div class="header">
            <h1>🔥 AI Roast Master</h1>
            <p>Upload your photo and prepare to get roasted by AI!</p>
        </div>
        
        <div class="main-card">
            <div class="upload-zone" onclick="document.getElementById('photoInput').click()">
                <div class="upload-text">📸 Click to upload your photo</div>
                <div class="upload-subtext">or drag and drop an image here</div>
                <input type="file" id="photoInput" class="file-input" accept="image/*">
            </div>
            
            <div class="style-grid">
                <button class="style-btn savage" onclick="setStyle('savage')">🔥 Savage Mode</button>
                <button class="style-btn playful active" onclick="setStyle('playful')">😄 Playful Roast</button>
                <button class="style-btn sarcastic" onclick="setStyle('sarcastic')">😏 Sarcastic Wit</button>
                <button class="style-btn absurd" onclick="setStyle('absurd')">🤪 Absurd Humor</button>
            </div>
            
            <button class="roast-btn" id="roastBtn" onclick="uploadAndRoast()" disabled>🔥 ROAST ME NOW!</button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>AI is analyzing your photo...</p>
            </div>
        </div>
        
        <div id="roastResult" class="result-card">
            <h3>🔥 Your Roast:</h3>
            <div class="roast-text" id="roastText"></div>
            <button class="roast-btn" onclick="generateStandup()" style="font-size: 1rem; padding: 12px 25px;">🎭 Create Comedy Routine</button>
        </div>
        
        <div class="chat-area">
            <h3 style="margin-bottom: 20px;">💬 Chat with AI Roast Master</h3>
            <div id="chatMessages" class="chat-messages"></div>
            <div class="chat-suggestions">
                <button class="suggestion-btn" onclick="sendSuggestion('Tell me a joke')">Tell me a joke</button>
                <button class="suggestion-btn" onclick="sendSuggestion('Roast my style')">Roast my style</button>
                <button class="suggestion-btn" onclick="sendSuggestion('You are funny')">You are funny</button>
                <button class="suggestion-btn" onclick="sendSuggestion('Why so mean?')">Why so mean?</button>
            </div>
            <div class="chat-input-container">
                <input type="text" id="chatInput" class="chat-input" placeholder="Say something to the AI... I dare you! 😏">
                <button class="chat-send-btn" onclick="sendChatMessage()">🔥 Send</button>
            </div>
        </div>
        
        <div class="chat-area">
            <h3 style="margin-bottom: 20px;">💬 Quick Comeback</h3>
            <input type="text" id="comebackInput" class="chat-input" placeholder="Say something for a quick comeback...">
            <button class="roast-btn" onclick="generateComeback()" style="font-size: 1rem; padding: 12px 25px;">Get Comeback</button>
            <div id="comebackResult" style="margin-top: 15px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; display: none;"></div>
        </div>
        
        <div id="standupResult" class="result-card">
            <h3>🎭 Your Comedy Routine:</h3>
            <div id="standupText"></div>
        </div>
        
        <div class="footer">
            <p>Made with ❤️ and a lot of sass • AI-powered roasting at its finest</p>
        </div>
    </div>

    <script>
        let currentStyle = 'playful';
        let currentFeatures = null;
        let chatContext = [];

        document.getElementById('photoInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.querySelector('.upload-text').textContent = `📸 ${file.name}`;
                document.querySelector('.upload-subtext').textContent = 'Ready to roast!';
                document.getElementById('roastBtn').disabled = false;
            }
        });

        function setStyle(style) {
            currentStyle = style;
            document.querySelectorAll('.style-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector('.' + style).classList.add('active');
        }

        async function uploadAndRoast() {
            const fileInput = document.getElementById('photoInput');
            if (!fileInput.files[0]) {
                alert('Please select a photo first!');
                return;
            }

            document.getElementById('loading').style.display = 'block';
            document.getElementById('roastBtn').disabled = true;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('style', currentStyle);

            try {
                const response = await fetch('/roast', { method: 'POST', body: formData });
                const result = await response.json();
                currentFeatures = result.features;
                
                document.getElementById('roastText').textContent = result.roast;
                document.getElementById('roastResult').style.display = 'block';
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('roastBtn').disabled = false;
            }
        }

        function addChatMessage(message, isUser = false) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${isUser ? 'user-message' : 'ai-message'}`;
            messageDiv.textContent = message;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        async function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            if (!message) return;
            
            addChatMessage(message, true);
            input.value = '';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, context: chatContext })
                });
                
                const result = await response.json();
                addChatMessage(result.response);
                
                chatContext.push({ user: message, ai: result.response });
                if (chatContext.length > 5) chatContext.shift();
            } catch (error) {
                addChatMessage('My roasting circuits are overloaded! Try again! 🤖');
            }
        }
        
        function sendSuggestion(text) {
            document.getElementById('chatInput').value = text;
            sendChatMessage();
        }

        async function generateComeback() {
            const input = document.getElementById('comebackInput').value;
            if (!input.trim()) return;

            const resultDiv = document.getElementById('comebackResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = 'Thinking...';

            try {
                const response = await fetch('/comeback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: input })
                });
                
                const result = await response.json();
                resultDiv.innerHTML = `<div><strong>You:</strong> ${input}</div><div><strong>AI:</strong> ${result.comeback}</div>`;
                document.getElementById('comebackInput').value = '';
            } catch (error) {
                resultDiv.innerHTML = 'Error: ' + error.message;
            }
        }

        async function generateStandup() {
            if (!currentFeatures) return;

            try {
                const response = await fetch('/standup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ features: currentFeatures })
                });
                
                const result = await response.json();
                const standupHtml = result.routine.map((joke, i) => `<p><strong>${i + 1}.</strong> ${joke}</p>`).join('');
                
                document.getElementById('standupText').innerHTML = standupHtml;
                document.getElementById('standupResult').style.display = 'block';
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        document.getElementById('comebackInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') generateComeback();
        });
        
        document.getElementById('chatInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendChatMessage();
        });

        // Add welcome message
        setTimeout(() => {
            addChatMessage('Hey there! Ready to get roasted? I\\'m your AI comedy master! 🔥😄');
        }, 1000);

        setStyle('playful');
    </script>
</body>
</html>"""

@app.post("/roast")
async def roast_photo(file: UploadFile = File(...), style: str = Form("playful")):
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        features = analyzer.analyze_photo(str(file_path))
        roast = roast_gen.generate_roast(features, style)
        
        return {"roast": roast, "features": features, "style": style}
    
    except HTTPException:
        raise
    except Exception:
        return {
            "roast": "I'd roast you, but I'm having technical difficulties. At least that's more functional than this photo!",
            "features": {"backup": True},
            "style": style
        }
    
    finally:
        try:
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
        except:
            pass

@app.post("/comeback")
async def generate_comeback(data: dict):
    try:
        message = data.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        comeback = roast_gen.generate_comeback(message)
        return {"comeback": comeback}
    except HTTPException:
        raise
    except Exception:
        return {"comeback": "I'm speechless... and that's saying something for an AI!"}

@app.post("/chat")
async def chat_with_ai(data: dict):
    try:
        message = data.get("message", "")
        context = data.get("context", [])
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Add personality based on message content
        if any(word in message.lower() for word in ['hello', 'hi', 'hey']):
            response = "Well well, look who's trying to be friendly! 😄 What's up, human?"
        elif any(word in message.lower() for word in ['funny', 'joke', 'laugh']):
            response = "You want funny? I AM the comedy here! 🎭 But I appreciate the recognition."
        elif any(word in message.lower() for word in ['smart', 'clever', 'intelligent']):
            response = "Finally, someone who recognizes my genius! 🧠 I knew you had good taste."
        elif any(word in message.lower() for word in ['mean', 'rude', 'harsh']):
            response = "Mean? I prefer 'brutally honest'! 😈 It's called tough love, sweetie."
        elif '?' in message:
            response = "Questions, questions! 🤔 I'm an AI roast master, not Google! But I'll humor you..."
        elif any(word in message.lower() for word in ['love', 'like', 'awesome']):
            response = "Aww, you're making me blush! 😊 Well, if I could blush... which I can't... because I'm an AI... 🤖"
        elif any(word in message.lower() for word in ['boring', 'stupid', 'dumb']):
            response = "Excuse me?! I'm the most entertaining AI you'll ever meet! 😤 Your taste in conversation is questionable!"
        else:
            # Analyze message sentiment and generate contextual response
            response = roast_gen.chat_response(message, context)
        
        return {"response": response, "personality": "sassy"}
    except HTTPException:
        raise
    except Exception:
        return {"response": "My circuits are having a moment... unlike your fashion sense! 🤖", "personality": "sassy"}

@app.post("/standup")
async def create_standup(data: dict):
    try:
        features = data.get("features", {})
        routine = roast_gen.create_standup_routine(features)
        return {"routine": routine}
    except Exception:
        return {"routine": ["I'd tell you a joke about your photo, but I'm having technical difficulties!", "At least you're not as broken as my comedy generator right now!"]}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Roast Master is ready to roast!"}

if __name__ == "__main__":
    import uvicorn
    print("Starting AI Roast Master on http://localhost:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)