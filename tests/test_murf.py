import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing Murf AI API Connection...")
print("-" * 50)

api_key = os.getenv("MURF_API_KEY")

if not api_key:
    print("❌ ERROR: MURF_API_KEY not found in .env file")
    exit(1)

print(f"✅ API Key found: {api_key[:20]}...")

try:
    # Test Murf AI API with a simple text
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    payload = {
        "voiceId": "en-US-ken",
        "text": "Hello, this is a test from Murf AI",
        "format": "MP3",
        "sampleRate": 24000,
        "modelVersion": "GEN2"
    }
    
    print("\n🎤 Testing Murf AI voice generation...")
    print(f"Voice: en-US-ken")
    print(f"Model: GEN2")
    
    response = requests.post(
        "https://api.murf.ai/v1/speech/generate",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        audio_size = len(response.content)
        print(f"\n✅ Successfully generated speech!")
        print(f"Audio size: {audio_size} bytes")
        
        # Save test audio
        with open("test_murf_audio.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Test audio saved as 'test_murf_audio.mp3'")
        
        print("\n" + "=" * 50)
        print("✅ Murf AI API is working correctly!")
        print("=" * 50)
    else:
        print(f"\n❌ ERROR: Murf AI API returned status {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR: Failed to connect to Murf AI API")
    print(f"Error details: {str(e)}")
    print("\nPossible issues:")
    print("  1. Invalid API key")
    print("  2. No internet connection")
    print("  3. Murf AI service is down")
    print("  4. Incorrect API endpoint")
    exit(1)
