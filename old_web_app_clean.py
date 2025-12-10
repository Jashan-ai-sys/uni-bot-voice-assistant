from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from rag_pipeline import answer_question
from elevenlabs import ElevenLabs
import uvicorn
import os
import json
import base64
from dotenv import load_dotenv

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
        <title>Uni Bot - Live Voice Assistant</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                width: 100%;
                padding: 40px;
                text-align: center;
            }
            
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            
            .conversation-area {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 20px;
                min-height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            
            .avatar {
                width: 120px;
                height: 120px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 3em;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }
            
            .avatar.listening {
                animation: pulse 1.5s infinite;
                box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
            }
            
            .avatar.speaking {
                animation: wave 1s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            @keyframes wave {
                0%, 100% { transform: scale(1) rotate(0deg); }
                25% { transform: scale(1.05) rotate(-5deg); }
                75% { transform: scale(1.05) rotate(5deg); }
            }
            
            .status {
                font-size: 1.2em;
                color: #667eea;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            .transcript {
                background: white;
                border-radius: 10px;
                padding: 15px;
                margin-top: 20px;
                max-height: 200px;
                overflow-y: auto;
                text-align: left;
            }
            
            .transcript-line {
                margin-bottom: 10px;
                padding: 8px;
                border-radius: 5px;
            }
            
            .user-line {
                background: #e3f2fd;
                margin-left: 20px;
            }
            
            .bot-line {
                background: #f3e5f5;
                margin-right: 20px;
            }
            
            button {
                padding: 20px 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 50px;
                font-size: 1.2em;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            button.active {
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            }

            .input-area {
                display: flex;
                gap: 10px;
                margin-top: 20px;
                width: 100%;
            }

            #textInput {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #eee;
                border-radius: 30px;
                font-size: 1em;
                outline: none;
                transition: border-color 0.3s;
            }

            #textInput:focus {
                border-color: #667eea;
            }

            #sendButton {
                padding: 15px 25px;
                border-radius: 50%;
                font-size: 1.2em;
                width: 54px;
                height: 54px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Uni Bot</h1>
            <p class="subtitle">Live Voice Assistant</p>
            
            <div class="conversation-area">
                <div class="avatar" id="avatar">🎤</div>
                <div class="status" id="status">Ready to talk</div>
                <p id="statusMessage">Click "Start Conversation" to begin</p>
                
                <div class="suggestions" id="suggestions">
                    <div class="suggestion-chip" onclick="askSuggestion('What is the placement process?')">💼 Placement Process</div>
                    <div class="suggestion-chip" onclick="askSuggestion('How do I apply for scholarships?')">💰 Scholarships</div>
                    <div class="suggestion-chip" onclick="askSuggestion('What are the hostel rules?')">🏠 Hostel Rules</div>
                    <div class="suggestion-chip" onclick="askSuggestion('Library timings?')">📚 Library</div>
                </div>

                <div class="transcript" id="transcript" style="display: none;">
                    <div class="transcript-line bot-line">
                        <strong>Assistant:</strong> Hello! Ask me anything about admissions, fees, or university life.
                    </div>
                </div>
            </div>
            
            <style>
                .suggestions {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    justify-content: center;
                    margin-top: 20px;
                    margin-bottom: 10px;
                }
                
                .suggestion-chip {
                    background: #f0f2f5;
                    border: 1px solid #ddd;
                    padding: 8px 15px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    cursor: pointer;
                    transition: all 0.2s;
                    color: #555;
                }
                
                .suggestion-chip:hover {
                    background: #e3f2fd;
                    border-color: #667eea;
                    color: #667eea;
                    transform: translateY(-2px);
                }
            </style>
            
            <button id="conversationButton" onclick="toggleConversation()">
                Start Conversation
            </button>
            <div class="input-area">
                <input type="text" id="textInput" placeholder="Type your question here..." onkeypress="handleKeyPress(event)">
                <button id="sendButton" onclick="sendText()">➤</button>
            </div>
        </div>
        
        <script>
            let recognition = null;
            let isListening = false;
            let currentAudio = null;
            let conversationActive = false;
            
            // Initialize speech recognition
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                recognition.onresult = async function(event) {
                    const transcript = event.results[event.results.length - 1][0].transcript;
                    addToTranscript('You: ' + transcript, 'user');
                    await getResponse(transcript);
                };
                
                recognition.onend = function() {
                    if (conversationActive) {
                        // Restart listening if conversation is still active
                        setTimeout(() => {
                            if (conversationActive) {
                                recognition.start();
                            }
                        }, 500);
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('Speech recognition error:', event.error);
                    if (event.error !== 'no-speech') {
                        updateStatus('Error: ' + event.error, 'Click "Stop" to end');
                    }
                };
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendText();
                }
            }

            async function sendText() {
                const input = document.getElementById('textInput');
                const text = input.value.trim();
                
                if (text) {
                    input.value = '';
                    // Ensure conversation is "active" so audio plays
                    if (!conversationActive) {
                        toggleConversation(); 
                    }
                    addToTranscript('You: ' + text, 'user');
                    await getResponse(text);
                }
            }
            
            function toggleConversation() {
                if (!recognition) {
                    alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
                    return;
                }
                
                conversationActive = !conversationActive;
                const button = document.getElementById('conversationButton');
                const avatar = document.getElementById('avatar');
                const transcript = document.getElementById('transcript');
                
                if (conversationActive) {
                    button.textContent = 'Stop Conversation';
                    button.classList.add('active');
                    avatar.classList.add('listening');
                    transcript.style.display = 'block';
                    updateStatus('Listening...', 'I\\'m ready to help! Speak your question.');
                    recognition.start();
                } else {
                    button.textContent = 'Start Conversation';
                    button.classList.remove('active');
                    avatar.classList.remove('listening', 'speaking');
                    avatar.textContent = '🎤';
                    updateStatus('Ready to talk', 'Click "Start Conversation" to begin');
                    recognition.stop();
                    if (currentAudio) {
                        currentAudio.pause();
                    }
                }
            }
            
            async function getResponse(question) {
                if (!conversationActive) return;
                
                updateStatus('Thinking...', 'Processing your question...');
                document.getElementById('avatar').classList.remove('listening');
                
                try {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question })
                    });
                    
                    const data = await response.json();
                    addToTranscript('Assistant: ' + data.answer, 'bot');
                    
                    // Speak the response
                    await speakResponse(data.answer);
                    
                } catch (error) {
                    console.error('Error:', error);
                    addToTranscript('Assistant: Sorry, I had trouble processing that.', 'bot');
                    if (conversationActive) {
                        updateStatus('Listening...', 'Ask me anything!');
                        document.getElementById('avatar').classList.add('listening');
                    }
                }
            }
            
            async function speakResponse(text) {
                if (!conversationActive) return;
                
                updateStatus('Speaking...', 'Generating response...');
                const avatar = document.getElementById('avatar');
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
                        if (conversationActive) {
                            updateStatus('Listening...', 'I\\'m ready for your next question!');
                            avatar.classList.remove('speaking');
                            avatar.classList.add('listening');
                            avatar.textContent = '🎤';
                        }
                    };
                    
                    await currentAudio.play();
                    
                } catch (error) {
                    console.error('Speech error:', error);
                    if (conversationActive) {
                        updateStatus('Listening...', 'Ask me anything!');
                        avatar.classList.remove('speaking');
                        avatar.classList.add('listening');
                        avatar.textContent = '🎤';
                    }
                }
            }
            
            function updateStatus(status, message) {
                document.getElementById('status').textContent = status;
                document.getElementById('statusMessage').textContent = message;
            }
            
            function addToTranscript(text, type) {
                const transcript = document.getElementById('transcript');
                const line = document.createElement('div');
                line.className = 'transcript-line ' + (type === 'user' ? 'user-line' : 'bot-line');
                // Allow HTML for bot responses to render bullets/bold
                if (type === 'bot') {
                    // Convert newlines to <br> for proper formatting
                    let formattedText = text.replace(/\n/g, '<br>');
                    // Convert **text** to <strong>text</strong>
                    formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    
                    line.innerHTML = '<strong>Assistant:</strong> ' + formattedText;
                } else {
                    line.innerHTML = '<strong>You:</strong> ' + text.replace('You: ', '');
                }
                transcript.appendChild(line);
                transcript.scrollTop = transcript.scrollHeight;
            }

            async function askSuggestion(question) {
                // If conversation not active, start it
                if (!conversationActive) {
                    toggleConversation();
                }
                
                // Add to transcript
                addToTranscript('You: ' + question, 'user');
                
                // Get response
                await getResponse(question);
            }
        </script>
    </body>
    </html>
    """

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question", "")
    answer = answer_question(question)
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

if __name__ == "__main__":
    print("🚀 Starting Uni Bot Live Voice Assistant...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("🎤 Click 'Start Conversation' and speak naturally!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
