import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv()

print("🔍 Testing ElevenLabs API Connection...")
print("-" * 50)

api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    print("❌ ERROR: ELEVENLABS_API_KEY not found in .env file")
    exit(1)

print(f"✅ API Key found: {api_key[:20]}...")

try:
    client = ElevenLabs(api_key=api_key)
    print("✅ ElevenLabs client initialized successfully")
    
    # Try to get available models or voices to verify connection
    print("\n🎤 Testing API connection by fetching voices...")
    voices = client.voices.get_all()
    
    if voices:
        print(f"✅ Successfully connected! Found {len(voices.voices)} voices available")
        print("\n📋 Available voices:")
        for i, voice in enumerate(voices.voices[:5], 1):  # Show first 5 voices
            print(f"  {i}. {voice.name} ({voice.voice_id})")
        if len(voices.voices) > 5:
            print(f"  ... and {len(voices.voices) - 5} more voices")
    else:
        print("⚠️ Connected but no voices found")
    
    print("\n" + "=" * 50)
    print("✅ ElevenLabs API is working correctly!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ ERROR: Failed to connect to ElevenLabs API")
    print(f"Error details: {str(e)}")
    print("\nPossible issues:")
    print("  1. Invalid API key")
    print("  2. No internet connection")
    print("  3. ElevenLabs service is down")
    exit(1)
