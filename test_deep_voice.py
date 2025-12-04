import requests

print("Testing pyttsx3 deep voice...")

# Test the /speak endpoint
response = requests.post(
    "http://localhost:8000/speak",
    json={"text": "Good evening sir, I am Jarvis, your AI assistant ready to serve."}
)

if response.status_code == 200:
    print(f"✅ Success! Audio generated, size: {len(response.content)} bytes")
    # Save to test file
    with open("test_jarvis_voice.mp3", "wb") as f:
        f.write(response.content)
    print("✅ Audio saved to test_jarvis_voice.mp3")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
