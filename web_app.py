from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from rag_pipeline import answer_question
from elevenlabs import ElevenLabs
import uvicorn
import os
import json
import base64
from dotenv import load_dotenv
import user_storage
import timetable_extractor

load_dotenv()

app = FastAPI()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Uni Bot - AI Assistant</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #1a1a1a;
                min-height: 100vh;
                color: #fff;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .header h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                color: #888;
                font-size: 1.1em;
            }
            
            .main-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .section {
                background: #2a2a2a;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
                min-height: 600px;
                display: flex;
                flex-direction: column;
            }
            
            .section-header {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 2px solid #3a3a3a;
            }
            
            .section-icon {
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5em;
            }
            
            .section-title {
                flex: 1;
            }
            
            .section-title h2 {
                color: #fff;
                font-size: 1.5em;
                margin-bottom: 5px;
            }
            
            .section-title p {
                color: #888;
                font-size: 0.9em;
            }
            
            /* Voice Assistant Section */
            .voice-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            
            .avatar {
                width: 150px;
                height: 150px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 4em;
                margin-bottom: 30px;
                transition: all 0.3s ease;
                box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
            }
            
            .avatar.listening {
                animation: pulse 2s infinite;
            }
            
            .avatar.speaking {
                animation: wave 1s infinite;
            }
            
            @keyframes pulse {
                0% { 
                    box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
                }
                70% {
                    box-shadow: 0 0 0 30px rgba(102, 126, 234, 0);
                }
                100% {
                    box-shadow: 0 0 0 0 rgba(102, 126, 234, 0);
                }
            }
            
            @keyframes wave {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            .voice-status {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .voice-status h3 {
                color: #667eea;
                font-size: 1.3em;
                margin-bottom: 10px;
            }
            
            .voice-status p {
                color: #aaa;
            }
            
            .voice-button {
                padding: 18px 45px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 50px;
                font-size: 1.1em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .voice-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
            }
            
            .voice-button.active {
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            }
            
            /* Text Chat Section */
            .chat-content {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #1a1a1a;
                border-radius: 12px;
                margin-bottom: 20px;
                min-height: 400px;
            }
            
            .message {
                margin-bottom: 15px;
                padding: 12px 18px;
                border-radius: 12px;
                max-width: 85%;
                animation: fadeIn 0.3s;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .user-message {
                background: #667eea;
                color: #fff;
                margin-left: auto;
                text-align: right;
            }
            
            .bot-message {
                background: #3a3a3a;
                color: #fff;
                margin-right: auto;
            }
            
            .suggestions {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .suggestion-chip {
                background: #3a3a3a;
                border: 1px solid #4a4a4a;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                cursor: pointer;
                transition: all 0.2s;
                color: #ccc;
            }
            
            .suggestion-chip:hover {
                background: #667eea;
                border-color: #667eea;
                color: #fff;
                transform: translateY(-2px);
            }
            
            .chat-input-area {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            
            .chat-input {
                flex: 1;
                padding: 15px 20px;
                background: #1a1a1a;
                border: 2px solid #3a3a3a;
                border-radius: 25px;
                color: #fff;
                font-size: 1em;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .chat-input:focus {
                border-color: #667eea;
            }
            
            .chat-input::placeholder {
                color: #666;
            }
            
            .send-button {
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 50%;
                color: white;
                font-size: 1.2em;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4);
            }
            
            .send-button:hover {
                transform: scale(1.1);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.6);
            }
            
            /* Shared transcript */
            .shared-transcript {
                background: #2a2a2a;
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
                max-width: 1400px;
                margin-left: auto;
                margin-right: auto;
            }
            
            .transcript-header {
                color: #667eea;
                font-size: 1.2em;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #3a3a3a;
            }
            
            .transcript-content {
                max-height: 200px;
                overflow-y: auto;
            }
            
            .transcript-item {
                padding: 10px;
                margin-bottom: 8px;
                border-radius: 8px;
                background: #1a1a1a;
            }
            
            .transcript-item strong {
                color: #667eea;
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #1a1a1a;
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #667eea;
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #764ba2;
            }
            
            /* Responsive */
            @media (max-width: 1024px) {
                .main-container {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎓 Uni Bot</h1>
            <p>Your intelligent university assistant with voice & chat</p>
        </div>
        
        <div class="main-container">
            <!-- Voice Assistant Section -->
            <div class="section">
                <div class="section-header">
                    <div class="section-icon">🎤</div>
                    <div class="section-title">
                        <h2>Voice Assistant</h2>
                        <p>Speak naturally to get answers</p>
                    </div>
                </div>
                
                <div class="voice-content">
                    <div class="avatar" id="avatar">🎤</div>
                    <div class="voice-status">
                        <h3 id="voiceStatus">Ready to Listen</h3>
                        <p id="voiceMessage">Click the button below to start</p>
                    </div>
                    <button class="voice-button" id="voiceButton" onclick="toggleVoice()">
                        Start Voice Chat
                    </button>
                </div>
            </div>
            
            <!-- Text Chat Section -->
            <div class="section">
                <div class="section-header">
                    <div class="section-icon">💬</div>
                    <div class="section-title">
                        <h2>Text Chat</h2>
                        <p>Type your questions here</p>
                    </div>
                </div>
                
                <div class="chat-content">
                    <div class="suggestions">
                        <div class="suggestion-chip" onclick="askSuggestion('What is the placement process?')">💼 Placement</div>
                        <div class="suggestion-chip" onclick="askSuggestion('How do I apply for scholarships?')">💰 Scholarships</div>
                        <div class="suggestion-chip" onclick="askSuggestion('What are the hostel rules?')">🏠 Hostel</div>
                        <div class="suggestion-chip" onclick="askSuggestion('Library timings?')">📚 Library</div>
                    </div>
                    
                    <div class="chat-messages" id="chatMessages">
                        <div class="message bot-message">
                            <strong>Assistant:</strong> Hello! Ask me anything about admissions, fees, placements, or university life. 👋
                        </div>
                    </div>
                    
                    <div class="chat-input-area">
                        <input type="text" class="chat-input" id="chatInput" placeholder="Ask anything..." onkeypress="handleChatKeyPress(event)">
                        <button class="send-button" onclick="sendChatMessage()">➤</button>
                    </div>
                </div>
            </div>
            
            <!-- My Timetable Section -->
            <div class="section" id="timetableSection">
                <div class="section-header">
                    <div class="section-icon">📅</div>
                    <div class="section-title">
                        <h2>My Timetable</h2>
                        <p>Upload & manage your schedule</p>
                    </div>
                </div>
                
                <div class="chat-content">
                    <!-- Profile Setup (shown if no student ID) -->
                    <div id="profileSetup" style="display: none;">
                        <h3 style="color: #667eea; margin-bottom: 15px;">Setup Your Profile</h3>
                        <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
                            <input type="text" id="studentIdInput" placeholder="Student ID (e.g., 12345678)" class="chat-input" style="margin: 0;">
                            <input type="text" id="nameInput" placeholder="Your Name" class="chat-input" style="margin: 0;">
                            <input type="text" id="programInput" placeholder="Program (e.g., B.Tech CSE)" class="chat-input" style="margin: 0;">
                            <input type="number" id="semesterInput" placeholder="Semester (e.g., 6)" class="chat-input" style="margin: 0;">
                        </div>
                        <button onclick="saveProfile()" class="voice-button" style="width: 100%; margin: 0;">
                            Save Profile
                        </button>
                    </div>
                    
                    <!-- Profile Display (shown if student ID exists) -->
                    <div id="profileDisplay" style="display: none;">
                        <div style="background: #1a1a1a; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">Profile</h4>
                            <p style="margin: 5px 0; color: #ccc;"><strong>ID:</strong> <span id="displayStudentId"></span></p>
                            <p style="margin: 5px 0; color: #ccc;"><strong>Name:</strong> <span id="displayName"></span></p>
                            <p style="margin: 5px 0; color: #ccc;"><strong>Program:</strong> <span id="displayProgram"></span></p>
                        </div>
                        
                        <!-- Upload Section -->
                        <div style="margin-bottom: 15px;">
                            <label for="timetableFile" class="voice-button" style="width: 100%; margin: 0; cursor: pointer; text-align: center;">
                                📤 Choose Timetable PDF
                            </label>
                            <input type="file" id="timetableFile" accept=".pdf" style="display: none;" onchange="handleFileSelect(event)">
                        </div>
                        
                        <div id="uploadStatus" style="padding: 10px; border-radius: 8px; background: #2a2a2a; color: #ccc; text-align: center; display: none;"></div>
                        
                        <button onclick="clearProfile()" style="margin-top: 15px; padding: 10px 20px; background: #ff6b6b; color: white; border: none; border-radius: 8px; cursor: pointer; width: 100%;">
                            Clear Profile
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Shared Transcript -->
        <div class="shared-transcript">
            <div class="transcript-header">📝 Conversation History</div>
            <div class="transcript-content" id="sharedTranscript">
                <div class="transcript-item">
                    <strong>System:</strong> Ready to assist you via voice or text!
                </div>
            </div>
        </div>
        
        <script>
            let recognition = null;
            let voiceActive = false;
            let currentAudio = null;
            
            // Initialize speech recognition
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                recognition.onresult = async function(event) {
                    const transcript = event.results[event.results.length - 1][0].transcript;
                    addToTranscript('You (Voice)', transcript);
                    await getResponse(transcript, true);
                };
                
                recognition.onend = function() {
                    if (voiceActive) {
                        setTimeout(() => {
                            if (voiceActive) {
                                recognition.start();
                            }
                        }, 500);
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('Speech recognition error:', event.error);
                };
            }
            
            function toggleVoice() {
                voiceActive = !voiceActive;
                const button = document.getElementById('voiceButton');
                const avatar = document.getElementById('avatar');
                const status = document.getElementById('voiceStatus');
                const message = document.getElementById('voiceMessage');
                
                if (voiceActive) {
                    button.textContent = 'Stop Voice Chat';
                    button.classList.add('active');
                    avatar.classList.add('listening');
                    status.textContent = 'Listening...';
                    message.textContent = 'Speak your question';
                    if (recognition) recognition.start();
                } else {
                    button.textContent = 'Start Voice Chat';
                    button.classList.remove('active');
                    avatar.classList.remove('listening', 'speaking');
                    avatar.textContent = '🎤';
                    status.textContent = 'Ready to Listen';
                    message.textContent = 'Click the button below to start';
                    if (recognition) recognition.stop();
                    if (currentAudio) currentAudio.pause();
                }
            }
            
            async function getResponse(question, isVoice = false) {
                try {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question })
                    });
                    
                    const data = await response.json();
                    const answer = data.answer;
                    
                    addToTranscript('Assistant', answer);
                    
                    if (isVoice) {
                        addChatMessage('bot', answer);
                    }
                    
                    // Speak response if voice is active
                    if (isVoice && voiceActive) {
                        await speakResponse(answer);
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                    addToTranscript('Assistant', 'Sorry, I had trouble processing that.');
                }
            }
            
            async function speakResponse(text) {
                const status = document.getElementById('voiceStatus');
                const message = document.getElementById('voiceMessage');
                const avatar = document.getElementById('avatar');
                
                status.textContent = 'Speaking...';
                message.textContent = 'Playing response';
                avatar.classList.remove('listening');
                avatar.classList.add('speaking');
                avatar.textContent = '🔊';
                
                try {
                    const response = await fetch('/speak', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text })
                    });
                    
                    if (!response.ok) throw new Error('Failed to generate speech');
                    
                    const audioBlob = await response.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    
                    currentAudio = new Audio(audioUrl);
                    currentAudio.onended = () => {
                        if (voiceActive) {
                            status.textContent = 'Listening...';
                            message.textContent = 'Speak your question';
                            avatar.classList.remove('speaking');
                            avatar.classList.add('listening');
                            avatar.textContent = '🎤';
                        }
                    };
                    
                    await currentAudio.play();
                    
                } catch (error) {
                    console.error('Speech error:', error);
                    if (voiceActive) {
                        status.textContent = 'Listening...';
                        message.textContent = 'Speak your question';
                        avatar.classList.remove('speaking');
                        avatar.classList.add('listening');
                        avatar.textContent = '🎤';
                    }
                }
            }
            
            function handleChatKeyPress(event) {
                if (event.key === 'Enter') {
                    sendChatMessage();
                }
            }
            
            async function sendChatMessage() {
                const input = document.getElementById('chatInput');
                const text = input.value.trim();
                
                if (text) {
                    input.value = '';
                    addChatMessage('user', text);
                    addToTranscript('You (Text)', text);
                    
                    // Get response and display in chat
                    try {
                        const response = await fetch('/ask', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                question: text,
                                student_id: currentStudentId
                            })
                        });
                        
                        const data = await response.json();
                        const answer = data.answer;
                        
                        // Add to both chat and transcript
                        addChatMessage('bot', answer);
                        addToTranscript('Assistant', answer);
                        
                    } catch (error) {
                        console.error('Error:', error);
                        addChatMessage('bot', 'Sorry, I had trouble processing that.');
                        addToTranscript('Assistant', 'Sorry, I had trouble processing that.');
                    }
                }
            }
            
            function addChatMessage(type, text) {
                const chatMessages = document.getElementById('chatMessages');
                const message = document.createElement('div');
                message.className = `message ${type === 'user' ? 'user-message' : 'bot-message'}`;
                
                if (type === 'bot') {
                    // Format bot messages (handle bullets, bold, etc.)
                    let formattedText = text.replace(/\\n/g, '<br>');
                    formattedText = formattedText.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
                    message.innerHTML = `<strong>${type === 'user' ? 'You' : 'Assistant'}:</strong> ${formattedText}`;
                } else {
                    message.innerHTML = `<strong>You:</strong> ${text}`;
                }
                
                chatMessages.appendChild(message);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function addToTranscript(speaker, text) {
                const transcript = document.getElementById('sharedTranscript');
                const item = document.createElement('div');
                item.className = 'transcript-item';
                item.innerHTML = `<strong>${speaker}:</strong> ${text}`;
                transcript.appendChild(item);
                transcript.scrollTop = transcript.scrollHeight;
            }
            
            async function askSuggestion(question) {
                document.getElementById('chatInput').value = question;
                sendChatMessage();
            }
            
            // ===== PROFILE & TIMETABLE FUNCTIONS =====
            let currentStudentId = null;
            
            // Initialize on page load
            window.addEventListener('DOMContentLoaded', function() {
                loadProfileFromStorage();
            });
            
            function loadProfileFromStorage() {
                currentStudentId = localStorage.getItem('studentId');
                
                if (currentStudentId) {
                    // Load profile from backend
                    fetch(`/user_profile/${currentStudentId}`)
                        .then(res => res.json())
                        .then(profile => {
                            if (profile.error) {
                                showProfileSetup();
                            } else {
                                displayProfile(profile);
                            }
                        })
                        .catch(() => showProfileSetup());
                } else {
                    showProfileSetup();
                }
            }
            
            function showProfileSetup() {
                document.getElementById('profileSetup').style.display = 'block';
                document.getElementById('profileDisplay').style.display = 'none';
            }
            
            function displayProfile(profile) {
                document.getElementById('displayStudentId').textContent = profile.student_id;
                document.getElementById('displayName').textContent = profile.name;
                document.getElementById('displayProgram').textContent = profile.program;
                
                document.getElementById('profileSetup').style.display = 'none';
                document.getElementById('profileDisplay').style.display = 'block';
                
                currentStudentId = profile.student_id;
            }
            
            function saveProfile() {
                const studentId = document.getElementById('studentIdInput').value.trim();
                const name = document.getElementById('nameInput').value.trim();
                const program = document.getElementById('programInput').value.trim();
                const semester = document.getElementById('semesterInput').value;
                
                if (!studentId || !name || !program || !semester) {
                    alert('Please fill all fields');
                    return;
                }
                
                // Save to localStorage
                localStorage.setItem('studentId', studentId);
                localStorage.setItem('studentName', name);
                localStorage.setItem('studentProgram', program);
                localStorage.setItem('studentSemester', semester);
                
                // Display profile
                displayProfile({
                    student_id: studentId,
                    name: name,
                    program: program,
                    semester: semester
                });
                
                alert('Profile saved! ✅ You can now upload your timetable.');
            }
            
            function clearProfile() {
                if (confirm('Are you sure you want to clear your profile?')) {
                    localStorage.removeItem('studentId');
                    localStorage.removeItem('studentName');
                    localStorage.removeItem('studentProgram');
                    localStorage.removeItem('studentSemester');
                    currentStudentId = null;
                    showProfileSetup();
                    
                    // Clear inputs
                    document.getElementById('studentIdInput').value = '';
                    document.getElementById('nameInput').value = '';
                    document.getElementById('programInput').value = '';
                    document.getElementById('semesterInput').value = '';
                }
            }
            
            function handleFileSelect(event) {
                const file = event.target.files[0];
                if (!file) return;
                
                if (file.type !== 'application/pdf') {
                    alert('Please select a PDF file');
                    return;
                }
                
                uploadTimetable(file);
            }
            
            async function uploadTimetable(file) {
                const statusDiv = document.getElementById('uploadStatus');
                statusDiv.style.display = 'block';
                statusDiv.style.background = '#667eea';
                statusDiv.innerHTML = '⏳ Uploading and processing timetable...';
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('student_id', currentStudentId);
                formData.append('name', localStorage.getItem('studentName'));
                formData.append('program', localStorage.getItem('studentProgram'));
                formData.append('semester', localStorage.getItem('studentSemester'));
                
                try {
                    const response = await fetch('/upload_timetable', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        statusDiv.style.background = '#4caf50';
                        statusDiv.innerHTML = `✅ ${result.message}`;
                    } else {
                        statusDiv.style.background = '#ff6b6b';
                        statusDiv.innerHTML = `❌ Error: ${result.error}`;
                    }
                } catch (error) {
                    statusDiv.style.background = '#ff6b6b';
                    statusDiv.innerHTML = `❌ Upload failed: ${error.message}`;
                }
            }
            
            // Update getResponse to include student ID
            async function getResponse(question, isVoice = false) {
                try {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            question: question,
                            student_id: currentStudentId  // Include student ID in request
                        })
                    });
                    
                    const data = await response.json();
                    const answer = data.answer;
                    
                    addToTranscript('Assistant', answer);
                    
                    if (isVoice) {
                        addChatMessage('bot', answer);
                    }
                    
                    // Speak response if voice is active
                    if (isVoice && voiceActive) {
                        await speakResponse(answer);
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                    addToTranscript('Assistant', 'Sorry, I had trouble processing that.');
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question", "")
    student_id = data.get("student_id", None)  # Get student ID if provided
    answer = answer_question(question, student_id)
    return {"answer": answer}

@app.post("/speak")
async def speak(request: Request):
    data = await request.json()
    text = data.get("text", "")
    
    try:
        # Generate speech using ElevenLabs
        audio_stream = client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            text=text,
            model_id="eleven_turbo_v2_5"
        )
        
        # Collect audio chunks
        audio_chunks = []
        for chunk in audio_stream:
            audio_chunks.append(chunk)
        
        # Combine chunks
        audio_data = b''.join(audio_chunks)
        
        from fastapi.responses import Response
        return Response(
            content=audio_data,
            media_type="audio/mpeg"
        )
    except Exception as e:
        print(f"Error generating speech: {e}")
        return {"error": str(e)}

@app.post("/upload_timetable")
async def upload_timetable(
    file: UploadFile = File(...),
    student_id: str = Form(...),
    name: str = Form(...),
    program: str = Form(...),
    semester: int = Form(...)
):
    """Upload and process student timetable"""
    try:
        # Save user profile
        user_storage.save_user_profile(student_id, name, program, semester)
        
        # Read PDF content
        pdf_content = await file.read()
        
        # Save PDF
        pdf_path = user_storage.save_timetable_pdf(student_id, pdf_content)
        
        # Extract timetable data using Gemini
        timetable_data = timetable_extractor.extract_timetable_from_pdf(pdf_path)
        
        # Save extracted data
        user_storage.save_timetable_data(student_id, timetable_data)
        
        return JSONResponse({
            "success": True,
            "message": f"Timetable uploaded and processed! Found {len(timetable_data.get('schedule', []))} classes.",
            "classes_count": len(timetable_data.get('schedule', []))
        })
    except Exception as e:
        print(f"Error uploading timetable: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/user_profile/{student_id}")
async def get_profile(student_id: str):
    """Get user profile"""
    profile = user_storage.get_user_profile(student_id)
    if profile:
        return JSONResponse(profile)
    else:
        return JSONResponse({"error": "Profile not found"}, status_code=404)

if __name__ == "__main__":
    print("🚀 Starting Uni Bot AI Assistant...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("🎤 Use voice or 💬 type your questions!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
