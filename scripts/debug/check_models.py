
import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv

# Force utf-8 for output
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
    sys.exit(1)

genai.configure(api_key=api_key)

try:
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} ({m.display_name})")
    print("Done.")
except Exception as e:
    print(f"Error listing models: {e}")
    sys.exit(1)
