import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv()

print("Testing ElevenLabs API...")
print(f"API Key loaded: {os.getenv('ELEVENLABS_API_KEY')[:20]}...")

try:
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    
    print("✅ Client created successfully")
    print("Generating test audio...")
    
    audio_generator = client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
        text="Hello, this is a test",
        model_id="eleven_multilingual_v2"
    )
    
    audio_bytes = b"".join(audio_generator)
    print(f"✅ Audio generated: {len(audio_bytes)} bytes")
    
    if len(audio_bytes) > 0:
        print("✅ SUCCESS: ElevenLabs API is working!")
    else:
        print("❌ ERROR: No audio data returned")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
