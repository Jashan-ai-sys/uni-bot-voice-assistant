import os
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv()
api_key = os.getenv("DEEPGRAM_API_KEY")
dg = DeepgramClient(api_key=api_key)

print(dg.speak.v1.audio.generate.__doc__)
