import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load env from .env file
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
print(f"Checking models with key: {api_key[:5]}...{api_key[-4:] if api_key else 'None'}")

if not api_key:
    print("❌ No API key found!")
    exit(1)

genai.configure(api_key=api_key)

print("\n--- Available Models ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
