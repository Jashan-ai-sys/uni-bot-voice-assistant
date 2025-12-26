import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv()

def verify_voice():
    print("Starting ElevenLabs Verification")
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not found in .env")
        return
        
    print(f"API Key found: {api_key[:10]}...")
    
    try:
        client = ElevenLabs(api_key=api_key)
        print("Client initialized")
        
        text = "This is a test of the Eleven Labs voice API."
        print(f"Attempting to generate audio for: '{text}'")
        
        # Using the same method as web_app.py
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id="21m00Tcm4TlvDq8ikWAM", # Rachel
            model_id="eleven_multilingual_v2"
        )
        
        print("Generator created, consuming stream...")
        
        audio_data = b"".join(audio_generator)
        
        size = len(audio_data)
        print(f"Audio generated! Size: {size} bytes")
        
        if size < 1000:
            print("Warning: Audio file is very small, might be an error message.")
            print(f"Content: {audio_data[:100]}")
        
        with open("verify_elevenlabs_output.mp3", "wb") as f:
            f.write(audio_data)
        print("Saved to verify_elevenlabs_output.mp3")
        
    except Exception as e:
        print(f"Error during verification: {e}")
        with open("error.txt", "w") as f:
            f.write(str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_voice()
