import os
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ No API key found in .env")
    exit(1)

try:
    client = ElevenLabs(api_key=api_key)
    print("✅ Client initialized")

    print("🎤 Attempting to generate audio...")
    audio_generator = client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM", # Rachel
        text="Hello, this is a test of the Eleven Labs API.",
        model_id="eleven_multilingual_v2"
    )
    
    audio_bytes = b"".join(audio_generator)
    print(f"✅ Success! Generated {len(audio_bytes)} bytes of audio.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
