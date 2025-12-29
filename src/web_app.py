import os
import sys
import io
# Force UTF-8 encoding for stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add Project Root to Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from dotenv import load_dotenv
import google.generativeai as genai
from src.rag_pipeline import answer_question
import src.user_storage as user_storage
import src.timetable_extractor as timetable_extractor
import traceback

load_dotenv()


app = FastAPI()

# Add CORS middleware to allow frontend requests
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static exists
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from elevenlabs import ElevenLabs

try:
    client = ElevenLabs(
      api_key=os.getenv("ELEVENLABS_API_KEY")
    )
except Exception:
    client = None
    print("Warning: ElevenLabs client failed to init")

@app.get("/", response_class=HTMLResponse)
async def home():
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LPU UMS - AI Assistant</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #f4f6f9 0%, #e0eafc 100%);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: #333;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

        /* Header */
        .ums-header { background: #fff; height: 70px; display: flex; align-items: center; padding: 0 20px; border-bottom: 5px solid #f47920; }
        .ums-logo-text { font-size: 28px; font-weight: 800; color: #000; }
        .ums-logo-text span { color: #f47920; }
        .sub-text { font-size: 11px; color: #666; font-weight: 500; }
        
        /* Layout */
        .main-container { display: flex; flex: 1; overflow: hidden; padding: 25px; gap: 20px; }
        
        .chat-card {
            flex: 2; background: rgba(255,255,255,0.9); border-radius: 16px; 
            border-top: 5px solid #f47920; display: flex; flex-direction: column;
            box-shadow: 0 8px 32px rgba(0,0,0,0.05);
        }
        
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        
        .message { padding: 12px 18px; border-radius: 12px; max-width: 85%; font-size: 14px; line-height: 1.5; }
        .user-message { background: #f47920; color: white; align-self: flex-end; }
        .bot-message { background: #fff; border: 1px solid #eee; align-self: flex-start; }
        
        .chat-input-area { padding: 15px; background: #fff; display: flex; gap: 10px; border-top: 1px solid #eee; }
        .input-group { flex: 1; display: flex; background: #f5f5f5; border-radius: 25px; padding: 8px 15px; border: 1px solid #ddd; }
        .chat-input { flex: 1; border: none; background: transparent; outline: none; }
        .send-btn { background: #f47920; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; }
        
        /* Floating Mic */
        .mic-btn-floating { position: fixed; bottom: 30px; right: 30px; width: 60px; height: 60px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(244,121,32,0.3); cursor: pointer; color: #f47920; font-size: 24px; border: 2px solid #f47920; }
        .mic-btn-floating.active { background: #f47920; color: white; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(244,121,32,0.4); } 70% { box-shadow: 0 0 0 15px rgba(244,121,32,0); } 100% { box-shadow: 0 0 0 0 rgba(244,121,32,0); } }

    </style>
</head>
<body>
    <div class="ums-header">
        <div class="ums-logo-text"><span>U</span>MS</div>
        <div style="margin-left: 10px;">
            <div style="font-weight: 800;">UNIVERSITY MANAGEMENT SYSTEM</div>
            <div class="sub-text">AI ASSISTANT PORTAL</div>
        </div>
    </div>

    <div class="main-container">
        <div class="chat-card">
            <div style="padding: 15px; border-bottom: 1px solid #eee; font-weight: bold;">LPU CHATBOT</div>
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">Hello! I am JARVIS. How can I help you?</div>
            </div>
            <div class="chat-input-area">
                <div class="input-group">
                    <input id="chatInput" class="chat-input" placeholder="Type your query..." onkeydown="if(event.key==='Enter') sendMessage()">
                </div>
                <button class="send-btn" onclick="sendMessage()">➤</button>
            </div>
        </div>
        
         <!-- Particle Sphere Container -->
        <div id="canvas-container" style="flex: 1; background: white; border-radius: 16px; border-top: 5px solid #f47920;"></div>
    </div>
    
    <div class="mic-btn-floating" id="micBtn" onclick="toggleVoice()">🎤</div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        
        function appendMsg(text, type) {
            const div = document.createElement('div');
            div.className = `message ${type}-message`;
            div.innerHTML = type === 'bot' ? marked.parse(text) : text;
            chatMessages.appendChild(div);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return div;
        }

        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const txt = input.value.trim();
            if(!txt) return;
            
            appendMsg(txt, 'user');
            input.value = '';
            
            const botDiv = appendMsg('...', 'bot');
            
            try {
                const res = await fetch('/ask_stream', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ question: txt, student_id: localStorage.getItem('studentId') || '12345' })
                });
                
                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let fullText = "";
                botDiv.innerHTML = "";
                
                while(true) {
                    const {value, done} = await reader.read();
                    if(done) break;
                    const chunk = decoder.decode(value, {stream:true});
                    const lines = chunk.split('\\n\\n');
                    for(const line of lines) {
                        if(line.startsWith('data: ')) {
                            const data = JSON.parse(line.slice(6));
                            if(data.chunk) {
                                fullText += data.chunk;
                                botDiv.innerHTML = marked.parse(fullText);
                                chatMessages.scrollTop = chatMessages.scrollHeight;
                            }
                        }
                    }
                }
            } catch(e) {
                botDiv.innerHTML = "Error: " + e.message;
            }
        }
        
        // Voice Logic
        let recognition;
        let isListening = false;
        if('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.onresult = (e) => {
                const txt = e.results[0][0].transcript;
                document.getElementById('chatInput').value = txt;
                sendMessage();
            };
            recognition.onend = () => { if(isListening) isListening = false; document.getElementById('micBtn').classList.remove('active'); };
        }
        
        function toggleVoice() {
            if(!recognition) return alert("Browser not supported");
            if(isListening) { recognition.stop(); }
            else { recognition.start(); isListening = true; document.getElementById('micBtn').classList.add('active'); }
        }

        // Three.js Sphere (Simplified)
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({alpha:true});
        document.getElementById('canvas-container').appendChild(renderer.domElement);
        
        const geometry = new THREE.SphereGeometry(1, 32, 32);
        const material = new THREE.MeshBasicMaterial({color: 0xf47920, wireframe: true});
        const sphere = new THREE.Mesh(geometry, material);
        scene.add(sphere);
        camera.position.z = 2;
        
        function animate() {
            requestAnimationFrame(animate);
            sphere.rotation.x += 0.01;
            sphere.rotation.y += 0.01;
            
            const cont = document.getElementById('canvas-container');
            renderer.setSize(cont.clientWidth, cont.clientHeight);
            camera.aspect = cont.clientWidth / cont.clientHeight;
            camera.updateProjectionMatrix();
            
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>"""

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question", "")
    student_id = data.get("student_id", None)
    answer = answer_question(question, student_id)
    return {"answer": answer}

@app.post("/ask_stream")
async def ask_stream(request: Request):
    from fastapi.responses import StreamingResponse
    import json
    from src.config import USE_MCP
    
    data = await request.json()
    question = data.get("question", "")
    student_id = data.get("student_id", None)
    
    async def generate():
        try:
            if USE_MCP:
                # Use MCP agent (local/high-memory environments)
                from src.llm_agent import UniAgent
                agent = UniAgent()
                async for chunk in agent.process_query_stream(question, student_id):
                    yield f"data: {json.dumps({'chunk': chunk})}\\n\\n"
            else:
                # Use basic RAG (production/low-memory environments like Render free tier)
                from src.rag_pipeline import answer_question_stream
                async for chunk in answer_question_stream(question, student_id):
                    yield f"data: {json.dumps({'chunk': chunk})}\\n\\n"
            
            yield f"data: {json.dumps({'done': True})}\\n\\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\\n\\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
