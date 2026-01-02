import os
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv()
api_key = os.getenv("DEEPGRAM_API_KEY")
dg = DeepgramClient(api_key=api_key)

print("Attributes of dg.speak.v1.audio (if valid):")
try:
    print(dir(dg.speak.v1.audio))
except Exception as e:
    print(e)
