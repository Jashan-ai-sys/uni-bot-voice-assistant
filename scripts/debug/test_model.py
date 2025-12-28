import google.generativeai as genai
import os
import sys

# Set stdout to UTF-8 to safe-guard against encoding errors
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)

candidates = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-001",
    "models/gemini-2.5-flash-001",
    "models/gemini-2.0-flash-exp",
    "models/gemini-pro",
    "models/gemini-1.5-pro",
]

print(f"Testing {len(candidates)} models...")

for model_name in candidates:
    print(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        if response.text:
            print(f"[SUCCESS] {model_name} generated content.")
        else:
            print(f"[FAILURE] {model_name} returned empty response.")
    except Exception as e:
        print(f"[ERROR] {model_name} failed. Reason: {e}")
    print("-" * 30)
