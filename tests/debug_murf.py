import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing Murf AI API with detailed logging...")
print("-" * 50)

api_key = os.getenv("MURF_API_KEY")
print(f"✅ API Key: {api_key[:20]}...")

# Test different payload formats
test_text = "Hello, this is a test from Murf AI"

# Try format 1 - basic
print("\n📝 Test 1: Basic payload")
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

payload = {
    "voiceId": "en-US-ken",
    "text": test_text,
    "format": "MP3",
    "sampleRate": 24000,
    "modelVersion": "GEN2"
}

print("Request:")
print(f"URL: https://api.murf.ai/v1/speech/generate")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        "https://api.murf.ai/v1/speech/generate",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text[:500]}")
    
    if response.status_code == 200:
        print(f"\n✅ Success! Audio size: {len(response.content)} bytes")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Full response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {str(e)}")
    import traceback
    traceback.print_exc()
