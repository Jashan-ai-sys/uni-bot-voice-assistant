import os
import sys
import io
# Force UTF-8 encoding for stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append('src')

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

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from deepgram import DeepgramClient

deepgram = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))

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

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

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

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* HEADER */
        .ums-header {
            background: #ffffff;
            height: 70px;
            display: flex;
            align-items: center;
            padding: 0 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            z-index: 100;
            border-bottom: 5px solid #f47920;
        }

        .logo-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .ums-logo-text {
            font-size: 28px;
            font-weight: 800;
            color: #000;
            letter-spacing: -1px;
        }
        
        .ums-logo-text span {
            color: #f47920;
        }

        .sub-text {
            font-size: 11px;
            color: #666;
            margin-top: -3px;
            font-weight: 500;
        }

        .nav-links {
            margin-left: auto;
            display: flex;
            gap: 25px;
            font-size: 14px;
            color: #555;
            font-weight: 500;
        }

        .nav-item {
            cursor: pointer;
            transition: color 0.2s;
        }

        .nav-item:hover {
            color: #f47920;
        }

        .search-icon {
            font-size: 16px;
            color: #555;
            cursor: pointer;
        }

        .profile-section {
            margin-left: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .profile-img {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            background: #ddd;
            object-fit: cover;
            border: 2px solid #fff;
            box-shadow: 0 0 0 1px #eee;
        }

        /* MAIN LAYOUT */
        .main-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        /* SIDEBAR */
        .sidebar {
            width: 90px;
            background: #f47920;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 0;
            color: white;
            flex-shrink: 0;
            overflow-y: auto;
        }

        .sidebar-item {
            width: 100%;
            height: 90px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background 0.2s;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .sidebar-item:hover, .sidebar-item.active {
            background: rgba(0,0,0,0.1);
        }

        .sidebar-icon {
            font-size: 28px;
            margin-bottom: 8px;
        }

        .sidebar-label {
            font-size: 11px;
            text-align: center;
            line-height: 1.2;
            padding: 0 5px;
        }

        /* CONTENT AREA */
        .content-area {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            display: flex;
            gap: 25px;
        }

        /* Left Card (Chat) */
        .chat-card {
            flex: 2;
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            display: flex;
            flex-direction: column;
            border-top: 4px solid #f47920;
            height: 100%;
            max-width: 900px; /* Prevent too wide on large screens */
            border: 1px solid rgba(255, 255, 255, 0.4);
        }

        .card-header {
            padding: 15px 20px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            border-top: 5px solid #f47920;
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            background: transparent;
        }

        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .card-title span {
            color: #f47920;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #fafafa;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            padding: 12px 18px;
            border-radius: 12px;
            max-width: 85%;
            font-size: 14px;
            line-height: 1.5;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            position: relative;
            animation: slideIn 0.3s ease-out forwards;
        }

        .user-message {
            background: #f47920;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }

        .bot-message {
            background: #ffffff;
            color: #333;
            align-self: flex-start;
            border: 1px solid #eee;
            border-bottom-left-radius: 2px;
        }
        
        .bot-message strong {
            color: #d35400;
        }
        
        .bot-message h3 {
            font-size: 16px;
            margin: 10px 0 5px 0;
            color: #333;
        }
        
        .bot-message ul {
            margin-left: 20px;
            margin-bottom: 10px;
        }

        .chat-input-area {
            padding: 15px 20px;
            background: #fff;
            border-top: 1px solid #f0f0f0;
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .input-group {
            flex: 1;
            display: flex;
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 25px;
            padding: 8px 15px;
            align-items: center;
            transition: all 0.2s;
        }

        .input-group:focus-within {
            border-color: #f47920;
            background: #fff;
            box-shadow: 0 0 0 3px rgba(244, 121, 32, 0.1);
        }

        .chat-input {
            flex: 1;
            border: none;
            background: transparent;
            outline: none;
            font-size: 14px;
            color: #333;
            margin-left: 8px;
        }
        
        .chat-input::placeholder {
            color: #999;
        }

        .send-btn {
            background: #f47920;
            color: white;
            border: none;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.2s, background 0.2s;
            font-size: 18px;
        }

        .send-btn:hover {
            transform: scale(1.05);
            background: #e67e22;
        }

        /* Right Card (Info/Notices) */
        .info-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
            max-width: 400px;
        }
        
        .notice-box {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            padding: 0;
            border-top: 4px solid #f47920;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .box-header {
            padding: 15px 20px;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .box-title {
            font-size: 15px;
            font-weight: 700;
            color: #333;
        }
        
        .box-content {
            padding: 15px 20px;
        }

        .quick-actions-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .action-chip {
            background: #fff;
            padding: 12px 5px;
            border-radius: 6px;
            text-align: center;
            font-size: 12px;
            font-weight: 500;
            color: #555;
            border: 1px solid #eee;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }
        
        .action-chip:hover {
            border-color: #f47920;
            color: #f47920;
            background: #fffbf8;
        }
        
        .action-icon {
            font-size: 18px;
        }

        .notice-list {
            display: flex;
            flex-direction: column;
        }
        
        .notice-item {
            padding: 12px 0;
            border-bottom: 1px dashed #eee;
            font-size: 13px;
            color: #444;
        }
        
        .notice-item:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }
        
        .notice-item strong {
            color: #f47920;
            display: block;
            margin-bottom: 3px;
        }

        /* MIC BUTTON */
        .mic-btn-floating {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: #fff; 
            border: 2px solid #f47920;
            box-shadow: 0 4px 15px rgba(244, 121, 32, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: #f47920;
            z-index: 200;
            transition: all 0.2s;
        }
        
        .mic-btn-floating:hover {
            transform: scale(1.1);
            background: #f47920;
            color: white;
        }
        
        .mic-btn-floating.active {
            background: #e74c3c;
            border-color: #e74c3c;
            color: white;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.4); }
            70% { box-shadow: 0 0 0 15px rgba(231, 76, 60, 0); }
            100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
        }

        /* Timetable Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.6);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(2px);
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 8px;
            width: 90%;
            max-width: 450px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            border-top: 5px solid #f47920;
            animation: modalSlide 0.3s;
        }
        
        @keyframes modalSlide {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .form-input {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-family: inherit;
            font-size: 14px;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #f47920;
        }
        
        .btn-upload {
            flex: 1;
            padding: 12px;
            background: #f47920;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .btn-upload:hover {
            background: #e67e22;
        }
        
        .btn-cancel {
            background: #f5f5f5;
            color: #666;
            margin-left: 10px;
        }
        
        .btn-cancel:hover {
            background: #e0e0e0;
        }

    </style>
</head>
<body>

    <!-- Header -->
    <div class="ums-header">
        <div class="logo-section">
            <img src="/static/lpu_logo.png" alt="LPU Logo" style="height: 50px; width: 50px; object-fit: contain; margin-right: 2px;">
            <div class="ums-logo-text"><span>U</span>MS</div>
            <div style="display:flex; flex-direction:column; margin-left:5px;">
                <span style="font-weight:800; font-size:15px; color:#222;">UNIVERSITY MANAGEMENT SYSTEM</span>
                <span class="sub-text">AI ASSISTANT PORTAL</span>
            </div>
        </div>
    </div>

    <!-- Main Container -->
    <div class="main-container">
        
        <!-- Content Area -->
        <div class="content-area" style="display: flex; gap: 20px; padding: 25px;">
            
            <!-- CHAT AREA -->
            <div class="chat-card" style="flex: 2; height: 100%;">
                <div class="card-header">
                    <div class="card-title">
                        LPU CHATBOT
                    </div>
                </div>

                <div class="chat-messages" id="chatMessages">
                    <div class="message bot-message">
                        <strong>JARVIS:</strong> Hello! I am your University AI Assistant. Ask me about your timetable, syllabus, fees, or campus regulations.
                    </div>
                </div>

                <div class="chat-input-area">
                    <button onclick="openTimetableModal()" style="border:none; background:none; cursor:pointer; color:#777; padding: 5px;" title="Upload Timetable">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" fill="#ff6b6b" stroke="#d63031"></rect>
                            <line x1="16" y1="2" x2="16" y2="6" stroke="#555" stroke-width="3"></line>
                            <line x1="8" y1="2" x2="8" y2="6" stroke="#555" stroke-width="3"></line>
                            <line x1="3" y1="9" x2="21" y2="9" stroke="#d63031" stroke-width="2"></line>
                            <rect x="7" y="13" width="3" height="3" fill="white"></rect>
                            <rect x="14" y="13" width="3" height="3" fill="white"></rect>
                            <rect x="7" y="17" width="3" height="3" fill="white"></rect>
                        </svg>
                    </button>
                    
                    <div class="input-group">
                        <span style="color:#aaa; font-size:16px;">🔍</span>
                        <input type="text" 
                               class="chat-input" 
                               id="chatInput" 
                               placeholder="Type your query..."
                               onkeydown="handleKeyPress(event)">
                    </div>
                    
                    <button class="send-btn" onclick="sendMessage()">➤</button>
                </div>
            </div>

            <!-- RIGHT PANEL - PARTICLE SPHERE -->
            <div class="particle-panel" style="flex: 1; background: #ffffff; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); position: relative; overflow: hidden; border-top: 5px solid #f47920; border-top-left-radius: 8px; border-top-right-radius: 8px; display: flex; align-items: center; justify-content: center; min-width: 300px;">
                <div id="canvas-container" style="width: 100%; height: 100%; position: absolute; top:0; left:0;"></div>
            </div>

        </div>
    </div>

    <!-- Floating Mic Button -->
    <div class="mic-btn-floating" id="micBtn" onclick="toggleVoice()" title="Voice Command">
        <svg style="width:24px; height:24px; fill:none; stroke:currentColor; stroke-width:2;" viewBox="0 0 24 24">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
    </div>

    <!-- Timetable Upload Modal -->
    <div id="timetableModal" class="modal">
        <div class="modal-content">
            <h2 style="color:#f47920; margin-bottom:20px; font-size:20px; text-align:center;">📅 Upload Timetable PDF</h2>
            <form id="timetableForm" onsubmit="uploadTimetable(event)">
                <input type="text" id="studentId" class="form-input" placeholder="Student ID (e.g. 12345)" required>
                <input type="text" id="studentName" class="form-input" placeholder="Your Name" required>
                <input type="text" id="program" class="form-input" placeholder="Program (e.g. B.Tech CSE)" required>
                <input type="number" id="semester" class="form-input" placeholder="Semester" required>
                <input type="file" id="timetableFile" class="form-input" accept=".pdf" required>
                <div style="display:flex;">
                    <button type="submit" class="btn-upload">Upload Timetable</button>
                    <button type="button" onclick="closeTimetableModal()" class="btn-upload btn-cancel">Cancel</button>
                </div>
            </form>
            <div id="uploadStatus" style="margin-top:15px; text-align:center; font-size:13px; font-weight:500;"></div>
        </div>
    </div>

    <script>
        // --- JS LOGIC ---

        // Three.js Particle Sphere
        let scene, camera, renderer, particles, geometry, material, analyser, dataArray, source, audioContext;
        let animationId;

        function initThreeJS() {
            const container = document.getElementById('canvas-container');
            if (!container) return;

            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.z = 2.5;

            renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            const particleCount = 2000;
            geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);

            const color1 = new THREE.Color(0xd67419); // Dark Orange Golden
            const color2 = new THREE.Color(0xd67419); // Dark Orange Golden

            for (let i = 0; i < particleCount; i++) {
                const phi = Math.acos(-1 + (2 * i) / particleCount);
                const theta = Math.sqrt(particleCount * Math.PI) * phi;
                const r = 1.0;
                
                positions[i * 3] = r * Math.cos(theta) * Math.sin(phi);
                positions[i * 3 + 1] = r * Math.sin(theta) * Math.sin(phi);
                positions[i * 3 + 2] = r * Math.cos(phi);

                colors[i * 3] = color1.r;
                colors[i * 3 + 1] = color1.g;
                colors[i * 3 + 2] = color1.b;
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            material = new THREE.PointsMaterial({
                size: 0.015,
                vertexColors: true,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending
            });

            particles = new THREE.Points(geometry, material);
            scene.add(particles);

            window.addEventListener('resize', onWindowResize, false);
            animate();
        }

        function onWindowResize() {
            const container = document.getElementById('canvas-container');
            if (!container || !camera || !renderer) return;
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }

        function animate() {
            requestAnimationFrame(animate);
            if(particles) {
                particles.rotation.y += 0.003;
                particles.rotation.x += 0.001;
                
                if (isListening && analyser) {
                   analyser.getByteFrequencyData(dataArray);
                   let sum = 0;
                   for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
                   const average = sum / dataArray.length;
                   const scale = 1.0 + (average / 256) * 0.5;
                   particles.scale.lerp(new THREE.Vector3(scale, scale, scale), 0.2);
                } else {
                   particles.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1);
                }
            }
            if(renderer && scene && camera) {
                renderer.render(scene, camera);
            }
        }

        // Initialize Audio Context for Reactivity
        async function initAudio() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                source = audioContext.createMediaStreamSource(stream);
                source.connect(analyser);
                analyser.fftSize = 256;
                const bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);
                return true;
            } catch (err) {
                console.error('Mic Error:', err);
                return false;
            }
        }

        window.addEventListener('load', initThreeJS);

        let isListening = false;
        let recognition = null;
        
        // Voice Setup
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            recognition.onresult = async function (event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                await getResponse(transcript, true);
            };
            recognition.onend = function () {
                if (isListening) recognition.start();
            };
        }

        let mediaRecorder;
        let deepgramSocket;

        async function toggleVoice() {
            const btn = document.getElementById('micBtn');
            const input = document.getElementById('chatInput');

            if (isListening) {
                // STOP Logic
                if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
                if (deepgramSocket) deepgramSocket.close();
                isListening = false;
                btn.classList.remove('active');
                return;
            }

            // START Logic
            try {
                // 1. Get Token
                const res = await fetch('/deepgram_token');
                const { key } = await res.json();

                // 2. Open Mic
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

                // 3. Connect Socket
                deepgramSocket = new WebSocket('wss://api.deepgram.com/v1/listen?model=nova-2&smart_format=true', ['token', key]);

                deepgramSocket.onopen = () => {
                    isListening = true;
                    btn.classList.add('active');
                    
                    mediaRecorder.addEventListener('dataavailable', event => {
                        if (event.data.size > 0 && deepgramSocket.readyState === 1) {
                            deepgramSocket.send(event.data);
                        }
                    });
                    mediaRecorder.start(250); // Send every 250ms
                };

                deepgramSocket.onmessage = (message) => {
                    const received = JSON.parse(message.data);
                    const transcript = received.channel.alternatives[0].transcript;
                    if (transcript && received.is_final) {
                        input.value = transcript;
                        sendMessage(true); // Auto-send with VOICE=TRUE
                        // Toggle OFF to prevent echo for now
                        toggleVoice(); 
                    }
                };
                
                deepgramSocket.onclose = () => {
                     if (isListening) {
                         isListening = false;
                         btn.classList.remove('active');
                     }
                };

            } catch (e) {
                console.error("Deepgram Error:", e);
                alert("Microphone Access Denied or Deepgram Error");
                isListening = false;
                btn.classList.remove('active');
            }
        }

        // Chat Logic
        function handleKeyPress(event) {
            if (event.key === 'Enter') sendMessage(false);
        }

        async function sendMessage(isVoice = false) {
            const input = document.getElementById('chatInput');
            const question = input.value.trim();
            if (!question) return;

            addMessage(question, 'user');
            input.value = '';
            
            await getResponse(question, isVoice);
        }

        function addMessage(text, type) {
            const container = document.getElementById('chatMessages');
            const div = document.createElement('div');
            div.className = `message ${type}-message`;
            if (type === 'bot') {
                div.innerHTML = marked.parse(text);
            } else {
                div.textContent = text;
            }
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        async function getResponse(question, isVoice) {
            // Create container for new message
            const container = document.getElementById('chatMessages');
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'message bot-message';
            container.appendChild(botMessageDiv);
            
            // Loader
            const loadingSpan = document.createElement('span');
            loadingSpan.innerHTML = '<em>Thinking...</em>';
            botMessageDiv.appendChild(loadingSpan);
            container.scrollTop = container.scrollHeight;

            try {
                const studentId = localStorage.getItem('studentId');
                const response = await fetch('/ask_stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question, student_id: studentId, session_id: sessionId })
                });

                if (!response.ok) throw new Error('Network error');

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                // Remove loader when first chunk arrives
                let isFirstChunk = true;
                
                let fullText = '';
                let displayedText = '';
                let isTyping = false;
                
                // Typing Loop
                const typeNextChar = async () => {
                    if (displayedText.length < fullText.length) {
                        isTyping = true;
                        const char = fullText.charAt(displayedText.length);
                        displayedText += char;
                        botMessageDiv.innerHTML = marked.parse(displayedText);
                        container.scrollTop = container.scrollHeight;
                        
                        // Dynamic speed: faster if behind
                        const delay = (fullText.length - displayedText.length) > 50 ? 5 : 20;
                        setTimeout(typeNextChar, delay);
                    } else {
                        isTyping = false;
                    }
                };

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    if (isFirstChunk) {
                        botMessageDiv.innerHTML = ''; // Clear "Thinking..."
                        isFirstChunk = false;
                    }
                    
                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\\n\\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.chunk) {
                                    fullText += data.chunk;
                                    if (!isTyping) typeNextChar();
                                }
                            } catch (e) {}
                        }
                    }
                }
                
                // Voice Prefetch (Parallel)
                let voicePromise = null;
                if (isVoice) {
                     voicePromise = fetch('/speak', {
                         method: 'POST',
                         headers: { 'Content-Type': 'application/json' },
                         body: JSON.stringify({ text: fullText })
                     }).then(res => res.blob());
                }

                // Ensure finish typing
                while (displayedText.length < fullText.length) {
                    await new Promise(r => setTimeout(r, 100));
                }

                // Voice Playback (Play when ready)
                if (isVoice && voicePromise) {
                    try {
                         const blob = await voicePromise;
                         const audioMsg = new Audio(URL.createObjectURL(blob));
                         audioMsg.play();
                         
                         // Visualizer
                         if (audioContext && analyser) {
                             const source = audioContext.createMediaElementSource(audioMsg);
                             source.connect(analyser);
                             analyser.connect(audioContext.destination);
                         }
                    } catch (e) {
                        console.error("TTS Error:", e);
                    }
                }

            } catch (error) {
                botMessageDiv.innerHTML = '❌ Error: ' + error.message;
            }
        }

        // Timetable Modal
        function openTimetableModal() {
            document.getElementById('timetableModal').style.display = 'flex';
        }

        function closeTimetableModal() {
            document.getElementById('timetableModal').style.display = 'none';
        }

        async function uploadTimetable(event) {
            event.preventDefault();
            const formData = new FormData();
            formData.append('student_id', document.getElementById('studentId').value);
            formData.append('name', document.getElementById('studentName').value);
            formData.append('program', document.getElementById('program').value);
            formData.append('semester', document.getElementById('semester').value);
            formData.append('file', document.getElementById('timetableFile').files[0]);

            const status = document.getElementById('uploadStatus');
            status.textContent = 'Uploading...';
            status.style.color = 'black';

            try {
                const res = await fetch('/upload_timetable', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.success) {
                    localStorage.setItem('studentId', document.getElementById('studentId').value);
                    status.textContent = '✅ Timetable Uploaded Successfully!';
                    status.style.color = 'green';
                    setTimeout(closeTimetableModal, 1500);
                } else {
                    status.textContent = '❌ ' + (data.error || 'Upload failed');
                    status.style.color = 'red';
                }
            } catch (e) {
                status.textContent = '❌ Network connection failed';
                status.style.color = 'red';
            }
        }
        
         // Load saved student ID
        let currentStudentId = localStorage.getItem('studentId');
        
        // Generate or retrieve Session ID for memory
        let sessionId = localStorage.getItem('chatSessionId');
        if (!sessionId) {
            sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('chatSessionId', sessionId);
        }
        console.log("Session ID:", sessionId);

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
    """Streaming endpoint for real-time response generation"""
    from fastapi.responses import StreamingResponse
    import json
    
    data = await request.json()
    question = data.get("question", "")
    student_id = data.get("student_id", None)
    session_id = data.get("session_id", "default_session") # Use provided ID or default
    
    print(f"\n[DEBUG] WEB: Received stream request: {question} (Session: {session_id})")
    
    async def generate():
        # Import here to access streaming API
        from src.rag_pipeline import answer_question_stream
        try:
            print("[DEBUG] WEB: Starting generator loop...")
            async for chunk in answer_question_stream(question, student_id, session_id):
                print(f"[DEBUG] WEB: Chunk: {chunk[:20]}...")
                yield f"data: {json.dumps({'chunk': chunk})}\\n\\n"
            print("[DEBUG] WEB: Generator finished.")
            yield f"data: {json.dumps({'done': True})}\\n\\n"
        except Exception as e:
            print(f"[DEBUG] WEB: Generator ERROR: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\\n\\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/deepgram_token")
async def get_deepgram_token():
    """Return Deepgram API Key for frontend streaming"""
    # In production, use a temporary scope key. For local, we pass the env key.
    key = os.getenv("DEEPGRAM_API_KEY")
    return JSONResponse({"key": key})

@app.post("/speak")
async def speak(request: Request):
    """Generate speech from text using ElevenLabs"""
    try:
        data = await request.json()
        text = data.get("text", "")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)

        print(f"🎤 Generating audio for: {text[:50]}...")
        
        # Deepgram TTS Config
        options = {
            "model": "aura-asteria-en",
            "encoding": "linear16",
            "container": "wav"
        }
        
        # Define output buffer (In-Memory)
        import io
        audio_buffer = io.BytesIO()
        
        # Generate Audio (Streaming Generator)
        response_generator = deepgram.speak.v1.audio.generate(text=text, **options)
        
        # Write to buffer
        for chunk in response_generator:
            if chunk:
                audio_buffer.write(chunk)
                
        audio_bytes = audio_buffer.getvalue()

        
        # Return audio as response
        from fastapi.responses import Response
        return Response(content=audio_bytes, media_type="audio/wav")
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Deepgram Error: {e}")
        print(error_trace)
        return JSONResponse({"error": str(e), "trace": error_trace}, status_code=500)

@app.post("/upload_timetable")
async def upload_timetable_endpoint(
    student_id: str = Form(...),
    name: str = Form(...),
    program: str = Form(...),
    semester: int = Form(...),
    file: UploadFile = File(...)
):
    """Handle timetable PDF upload"""
    try:
        # Save profile
        user_storage.save_user_profile(student_id, name, program, semester)
        
        # Save PDF
        pdf_content = await file.read()
        pdf_path = user_storage.save_user_timetable_pdf(student_id, pdf_content)
        
        # Extract timetable
        timetable_data = timetable_extractor.extract_timetable_from_pdf(pdf_path)
        
        # Save extracted data
        user_storage.save_user_timetable(student_id, timetable_data, pdf_path)
        
        return JSONResponse({"success": True, "message": "Timetable uploaded successfully!"})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/user_profile/{student_id}")
async def get_user_profile_endpoint(student_id: str):
    """Get user profile"""
    profile = user_storage.get_user_profile(student_id)
    if profile:
        return JSONResponse({"success": True, "profile": profile})
    return JSONResponse({"success": False, "message": "Profile not found"}, status_code=404)

if __name__ == "__main__":
    print("Starting Uni Bot AI Assistant...")
    print("Open your browser and go to: http://localhost:8000")
    print("Use voice or type your questions!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
