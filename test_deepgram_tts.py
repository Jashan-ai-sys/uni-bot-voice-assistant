import os
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv()

api_key = os.getenv("DEEPGRAM_API_KEY")
print(f"API Key: {api_key[:5]}...")

try:
    deepgram = DeepgramClient(api_key=api_key)
    
    text = "Hello, this is a test of Deepgram Voice."
    filename = "test_audio.wav"
    
    options = {
        "model": "aura-asteria-en",
        "encoding": "linear16",
        "container": "wav"
    }
    
    print("Generating audio...")
    # Attempting the syntax used in web_app.py
    response = deepgram.speak.v1.audio.generate(text=text, **options)
    print(f"Response Type: {type(response)}")
    
    # Assuming response has a method to get bytes or is bytes?
    # SDK v3 usually returns a response object with .stream or .content
    # Let's inspect it.
    print(f"Response: {response}")
    
    if hasattr(response, 'stream'):
        # If it's a stream
        pass 
    elif isinstance(response, bytes):
        with open(filename, "wb") as f:
            f.write(response)
        print(f"Success! Saved bytes to {filename}")
    else:
        # Check standard properties
        if hasattr(response, 'to_file'):
            response.to_file(filename)
            print(f"Saved via to_file() to {filename}")
        else:
             print("Unknown response type, cannot save yet.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
