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
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from elevenlabs import ElevenLabs

client = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY")
)

@app.get("/", response_class=HTMLResponse)
async def home():
    return r"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS AI Assistant</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: #0a0a0a;
            color: #fff;
            overflow: hidden;
            height: 100vh;
        }

        .main-container {
            display: flex;
            height: 100vh;
        }

        /* Sidebar */
        .sidebar {
            width: 60px;
            background: #0f0f0f;
            border-right: 1px solid #1a1a1a;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px 0;
            gap: 20px;
        }

        .sidebar-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #1a1a1a;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 20px;
        }

        .sidebar-icon:hover {
            background: #252525;
        }

        .sidebar-icon.active {
            background: linear-gradient(135deg, #00ffff, #00aaaa);
            color: #000;
        }

        /* Chat Panel */
        .chat-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #0a0a0a;
            max-width: 720px;
            border-right: 1px solid #1a1a1a;
        }

        .chat-header {
            padding: 15px 20px;
            border-bottom: 1px solid #1a1a1a;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ffff;
            box-shadow: 0 0 10px #00ffff;
        }

        .header-text {
            font-size: 13px;
            color: #00ffff;
            font-weight: 500;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .message {
            margin-bottom: 20px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
            animation: messageSlide 0.3s;
        }

        @keyframes messageSlide {
            from {
                opacity: 0;
                transform: translateY(10px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .user-message {
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid rgba(0, 255, 255, 0.3);
            margin-left: auto;
            color: #00ffff;
        }

        .bot-message {
            background: #1a1a1a;
            border: 1px solid #252525;
            margin-right: auto;
            color: #e0e0e0;
        }

        .chat-input-container {
            padding: 20px;
            border-top: 1px solid #1a1a1a;
        }

        .input-wrapper {
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.3s;
        }

        .input-wrapper:focus-within {
            border-color: #00ffff;
            box-shadow: 0 0 0 1px #00ffff;
        }

        .chat-input {
            flex: 1;
            background: transparent;
            border: none;
            color: #fff;
            font-size: 14px;
            outline: none;
        }

        .chat-input::placeholder {
            color: #666;
        }

        .input-icon {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
            color: #666;
        }

        .input-icon:hover {
            background: #252525;
            color: #00ffff;
        }

        .bottom-actions {
            display: flex;
            gap: 15px;
            margin-top: 15px;
            padding: 0 5px;
        }

        .action-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: transparent;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            color: #888;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .action-btn:hover {
            border-color: #00ffff;
            color: #00ffff;
        }

        /* Right Panel - Particle Sphere */
        .particle-panel {
            flex: 1;
            background: #0f0f0f;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        #canvas-container {
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
        }

        .sphere-controls {
            position: absolute;
            bottom: 40px;
            display: flex;
            gap: 30px;
            z-index: 10;
            align-items: center;
        }

        /* Standard round button for close */
        .close-btn {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(26, 26, 26, 0.8);
            border: 1px solid #2a2a2a;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
            color: #fff;
            font-size: 20px;
        }

        .close-btn:hover {
            background: rgba(37, 37, 37, 0.9);
            border-color: #ff4444;
            color: #ff4444;
        }

        /* New Waveform Button */
        .wave-btn {
            width: 60px;
            height: 60px;
            border-radius: 18px;
            /* Rounded square */
            background: #26c6da;
            /* Cyan color from image */
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(38, 198, 218, 0.3);
        }

        .wave-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(38, 198, 218, 0.5);
        }

        .wave-btn.active {
            background: #00e5ff;
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.6);
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% {
                transform: scale(1);
            }

            50% {
                transform: scale(1.1);
            }

            100% {
                transform: scale(1);
            }
        }

        .wave-icon {
            width: 24px;
            height: 24px;
            fill: none;
            stroke: #000;
            stroke-width: 2.5;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: #0a0a0a;
        }

        ::-webkit-scrollbar-thumb {
            background: #2a2a2a;
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #3a3a3a;
        }
    </style>
</head>

<body>
    <div class="main-container">
        <!-- Sidebar -->
        <div class="sidebar">
            

            <div class="sidebar-icon" onclick="openTimetableModal()" title="Upload Timetable">📅</div>
            
        </div>

        <!-- Chat Panel -->
        <div class="chat-panel">
            <div class="chat-header">
                <div class="status-indicator"></div>
                <span class="header-text">JARVIS AI Assistant - Ready</span>
            </div>

            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    Hello! I'm JARVIS, your AI assistant. How can I help you today?
                </div>
            </div>

            <div class="chat-input-container">
                <div class="input-wrapper">
                    <div class="input-icon">🔍</div>
                    <input type="text" class="chat-input" id="chatInput"
                        placeholder="Ask anything. Type @ for mentions and / for shortcuts."
                        onkeydown="handleKeyPress(event)"
                        />

                    <div class="input-icon" onclick="sendMessage()">➤</div>
                </div>


            </div>
        </div>

        <!-- Particle Sphere Panel -->
        <div class="particle-panel">
            <div id="canvas-container"></div>
            <div class="sphere-controls">
                <div class="close-btn" onclick="closeApp()">✕</div>
                <div class="wave-btn" id="micBtn" onclick="toggleVoice()">
                    <svg class="wave-icon" viewBox="0 0 24 24">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="8" y1="9" x2="8" y2="15"></line>
                        <line x1="16" y1="9" x2="16" y2="15"></line>
                        <line x1="4" y1="11" x2="4" y2="13"></line>
                        <line x1="20" y1="11" x2="20" y2="13"></line>
                    </svg>
                </div>
            </div>
        </div>
    </div>

    <!-- Timetable Upload Modal -->
    <div id="timetableModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; align-items: center; justify-content: center;">
        <div style="background: #1a1a1a; padding: 30px; border-radius: 15px; max-width: 500px; width: 90%; border: 1px solid #00ffff;">
            <h2 style="color: #00ffff; margin-bottom: 20px;">📅 Upload Your Timetable</h2>
            <form id="timetableForm" onsubmit="uploadTimetable(event)">
                <input type="text" id="studentId" placeholder="Student ID" required style="width: 100%; padding: 12px; margin-bottom: 15px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 8px; color: #fff;">
                <input type="text" id="studentName" placeholder="Your Name" required style="width: 100%; padding: 12px; margin-bottom: 15px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 8px; color: #fff;">
                <input type="text" id="program" placeholder="Program (e.g., B.Tech CSE)" required style="width: 100%; padding: 12px; margin-bottom: 15px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 8px; color: #fff;">
                <input type="number" id="semester" placeholder="Semester" required style="width: 100%; padding: 12px; margin-bottom: 15px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 8px; color: #fff;">
                <input type="file" id="timetableFile" accept=".pdf" required style="width: 100%; padding: 12px; margin-bottom: 20px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 8px; color: #fff;">
                <div style="display: flex; gap: 10px;">
                    <button type="submit" style="flex: 1; padding: 12px; background: linear-gradient(135deg, #00ffff, #00aaaa); border: none; border-radius: 8px; color: #000; font-weight: bold; cursor: pointer;">Upload</button>
                    <button type="button" onclick="closeTimetableModal()" style="flex: 1; padding: 12px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 8px; color: #fff; cursor: pointer;">Cancel</button>
                </div>
            </form>
            <div id="uploadStatus" style="margin-top: 15px; color: #00ffff; text-align: center;"></div>
        </div>
    </div>

    <script>
        // Three.js Particle Sphere with Audio Reactivity

        let isListening = false;
        let animationId;
        let scene, camera, renderer, particles, geometry, material, analyser, dataArray, source, audioContext;

        function getElements() {
             return {
                 container: document.getElementById('canvas-container'),
                 micBtn: document.getElementById('micBtn'),
                 statusText: document.querySelector('.header-text')
             };
        }

        function initThreeJS() {
            try {
                if (typeof THREE === 'undefined') {
                    const { statusText } = getElements();
                    if(statusText) statusText.textContent = 'Error: Three.js failed to load';
                    console.error('Three.js not loaded');
                    return;
                }
                const { container } = getElements();
                if (!container) {
                    const { statusText } = getElements();
                    if(statusText) statusText.textContent = 'Error: Canvas container missing';
                    return;
                }

                // Scene setup
            scene = new THREE.Scene();

            // Camera setup
            camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.z = 2.5;

            // Renderer setup
            renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            // Particles setup
            const particleCount = 2000;
            geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);

            const color1 = new THREE.Color(0xe6d5ac); // Beige/Gold
            const color2 = new THREE.Color(0xffffff); // White

            for (let i = 0; i < particleCount; i++) {
                // Create points on a sphere surface (perfect circle look)
                const phi = Math.acos(-1 + (2 * i) / particleCount);
                const theta = Math.sqrt(particleCount * Math.PI) * phi;

                const r = 1.0; // Radius

                // Convert spherical to cartesian
                positions[i * 3] = r * Math.cos(theta) * Math.sin(phi);
                positions[i * 3 + 1] = r * Math.sin(theta) * Math.sin(phi);
                positions[i * 3 + 2] = r * Math.cos(phi);

                // Random colors between gold and white
                const mixedColor = color1.clone().lerp(color2, Math.random());
                colors[i * 3] = mixedColor.r;
                colors[i * 3 + 1] = mixedColor.g;
                colors[i * 3 + 2] = mixedColor.b;
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            // Material
            material = new THREE.PointsMaterial({
                size: 0.015,
                vertexColors: true,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending
            });

            particles = new THREE.Points(geometry, material);
            scene.add(particles);

            // Resize handler
            window.addEventListener('resize', onWindowResize, false);

            animate();
            } catch (e) {
                console.error("ThreeJS Init Error:", e);
            }
        }

        function onWindowResize() {
            const { container } = getElements();
            if (!container || !camera || !renderer) return;
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }

        function animate() {
            animationId = requestAnimationFrame(animate);

            // Base rotation
            particles.rotation.y += 0.002;
            particles.rotation.x += 0.001;

            // Audio reactivity
            if (isListening && analyser) {
                analyser.getByteFrequencyData(dataArray);

                // Calculate average volume
                let sum = 0;
                for (let i = 0; i < dataArray.length; i++) {
                    sum += dataArray[i];
                }
                const average = sum / dataArray.length;

                // Scale sphere based on volume (pitch/loudness effect)
                // Base scale is 1.0, adds up to 0.5 based on volume
                const scale = 1.0 + (average / 256) * 0.8;

                // Smooth transition
                particles.scale.lerp(new THREE.Vector3(scale, scale, scale), 0.2);

                // Change rotation speed based on activity
                particles.rotation.y += (average / 256) * 0.02;
            } else {
                // Return to normal size
                particles.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1);
            }

            renderer.render(scene, camera);
        }

        // Initialize Audio Context
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
                console.error('Error accessing microphone:', err);
                alert('Microphone access denied or not available.');
                return false;
            }
        }

        // Voice Control Logic
        let recognition = null;

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

        async function toggleVoice() {
            if (!isListening) {
                // Start listening
                const audioInitialized = await initAudio();
                if (audioInitialized) {
                    isListening = true;
                    const { micBtn } = getElements();
                    if(micBtn) micBtn.classList.add('active');
                    updateStatus('Listening...');
                    if (recognition) recognition.start();
                }
            } else {
                // Stop listening
                isListening = false;
                const { micBtn } = getElements();
                if(micBtn) micBtn.classList.remove('active');
                updateStatus('Ready');
                if (recognition) recognition.stop();

                // Close audio context to stop processing
                if (audioContext) {
                    audioContext.close();
                    audioContext = null;
                }
            }
        }

        // Chat Logic
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const question = input.value.trim();

            if (!question) return;

            addMessage(question, 'user');
            input.value = '';

            await getResponse(question, false);
        }

        function addMessage(text, type) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            
            if (type === 'bot') {
                // Parse markdown for bot messages
                messageDiv.innerHTML = marked.parse(text);
            } else {
                messageDiv.textContent = text;
            }
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        async function getResponse(question, isVoice) {
            updateStatus('Thinking...');
            
            // Create container for new message
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'message bot-message';
            const messagesDiv = document.getElementById('chatMessages');
            messagesDiv.appendChild(botMessageDiv);
            
            // Loader
            const botLoader = document.createElement('div');
            botLoader.className = 'loader';
            botMessageDiv.appendChild(botLoader);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            try {
                const studentId = localStorage.getItem('studentId');
                
                const response = await fetch('/ask_stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        question: question,
                        student_id: studentId 
                    })
                });

                if (!response.ok) throw new Error('Network error');

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let isFirstChunk = true;
                
                // Typewriter state
                let buffer = '';
                let displayedText = '';
                let isTyping = false;
                
                // Process buffer loop function
                const processBuffer = async () => {
                    if (isTyping) return;
                    isTyping = true;
                    
                    while (buffer.length > 0) {
                        const char = buffer.charAt(0);
                        buffer = buffer.slice(1);
                        displayedText += char;
                        
                        if (typeof marked !== 'undefined') {
                            botMessageDiv.innerHTML = marked.parse(displayedText);
                        } else {
                            botMessageDiv.textContent = displayedText;
                        }
                        
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        
                        // Faster typing if buffer gets too large
                        const delay = buffer.length > 50 ? 5 : 20;
                        await new Promise(r => setTimeout(r, delay));
                    }
                    isTyping = false;
                };

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    if (isFirstChunk && botMessageDiv.contains(botLoader)) {
                        botMessageDiv.removeChild(botLoader);
                        isFirstChunk = false;
                    }

                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.error) {
                                    buffer += "\n\n[Error: " + data.error + "]";
                                } else if (data.chunk) {
                                    buffer += data.chunk;
                                    // Trigger typing if not already running
                                    if (!isTyping) processBuffer();
                                }
                            } catch (e) {
                                console.error('JSON parse error:', e);
                            }
                        }
                    }
                }
                
                // Wait for any remaining buffer to be typed out
                while (buffer.length > 0 || isTyping) {
                    await new Promise(r => setTimeout(r, 100));
                }

                if (isVoice && isListening) {
                    updateStatus('Speaking...');
                    await speakResponse(displayedText);
                    updateStatus('Listening...');
                } else {
                    updateStatus('Ready');
                }
            } catch (error) {
                console.error('Error:', error);
                if (botMessageDiv.contains(botLoader)) botMessageDiv.removeChild(botLoader);
                botMessageDiv.textContent = 'Sorry, I encountered an error.';
                updateStatus('Ready');
            }
        }

        async function speakResponse(text) {
            try {
                const response = await fetch('/speak', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });

                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);

                await audio.play();

                return new Promise(resolve => {
                    audio.onended = () => resolve();
                });
            } catch (error) {
                console.error('Speech error:', error);
            }
        }

        function updateStatus(status) {
            const { statusText } = getElements();
            if (statusText) statusText.textContent = `JARVIS AI Assistant - ${status}`;
        }

        function closeApp() {
            if (confirm('Close JARVIS?')) {
                window.close();
            }
        }

        function tryAssistant() {
            const sampleQuestions = [
                "Tell me about LPU",
                "What courses are available?",
                "How do I apply for admission?"
            ];
            const randomQ = sampleQuestions[Math.floor(Math.random() * sampleQuestions.length)];
            document.getElementById('chatInput').value = randomQ;
        }

        // Initialize Three.js on load
        window.addEventListener('load', initThreeJS);

        // ===== TIMETABLE UPLOAD FUNCTIONS =====
        let currentStudentId = null;

        function openTimetableModal() {
            document.getElementById('timetableModal').style.display = 'flex';
        }

        function closeTimetableModal() {
            document.getElementById('timetableModal').style.display = 'none';
            document.getElementById('timetableForm').reset();
            document.getElementById('uploadStatus').textContent = '';
        }

        async function uploadTimetable(event) {
            event.preventDefault();
            
            const studentId = document.getElementById('studentId').value;
            const name = document.getElementById('studentName').value;
            const program = document.getElementById('program').value;
            const semester = document.getElementById('semester').value;
            const file = document.getElementById('timetableFile').files[0];
            
            const statusDiv = document.getElementById('uploadStatus');
            statusDiv.textContent = '⏳ Uploading and processing...';
            
            const formData = new FormData();
            formData.append('student_id', studentId);
            formData.append('name', name);
            formData.append('program', program);
            formData.append('semester', semester);
            formData.append('file', file);
            
            try {
                const response = await fetch('/upload_timetable', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentStudentId = studentId;
                    localStorage.setItem('studentId', studentId);
                    statusDiv.style.color = '#00ff00';
                    statusDiv.textContent = '✅ Timetable uploaded successfully!';
                    setTimeout(closeTimetableModal, 2000);
                } else {
                    statusDiv.style.color = '#ff4444';
                    statusDiv.textContent = '❌ Error: ' + (data.error || 'Upload failed');
                }
            } catch (error) {
                statusDiv.style.color = '#ff4444';
                statusDiv.textContent = '❌ Network error. Please try again.';
            }
        }

        // Load saved student ID
        currentStudentId = localStorage.getItem('studentId');

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
    
    async def generate():
        # Import here to access streaming API
        from src.rag_pipeline import answer_question_stream
        try:
            async for chunk in answer_question_stream(question, student_id):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/speak")
async def speak(request: Request):
    """Generate speech from text using ElevenLabs"""
    try:
        data = await request.json()
        text = data.get("text", "")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)

        print(f"🎤 Generating audio for: {text[:50]}...")
        
        # Generate audio using the correct v1+ SDK method
        # Use a specific voice ID for 'Rachel' or let it default if allowed, 
        # but explicit ID is safer. Rachel ID: 21m00Tcm4TlvDq8ikWAM
        audio_generator = client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM", 
            text=text,
            model_id="eleven_multilingual_v2"
        )
        
        # Consume the generator to get bytes
        audio_bytes = b"".join(audio_generator)
        print(f"✅ Audio generated: {len(audio_bytes)} bytes")
        
        # Return audio as response
        from fastapi.responses import Response
        return Response(content=audio_bytes, media_type="audio/mpeg")
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ ElevenLabs Error: {e}")
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
