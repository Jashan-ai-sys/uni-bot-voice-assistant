import google.generativeai as genai
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Comprehensive list of potential models
candidates = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-001",
    "models/gemini-1.5-flash-002",
    "models/gemini-1.5-flash-8b",
    "models/gemini-1.5-pro",
    "models/gemini-1.5-pro-001",
    "models/gemini-1.5-pro-002",
    "models/gemini-pro",
    "models/gemini-1.0-pro",
    "models/gemini-2.0-flash-exp",
    "models/gemini-exp-1206"
]

print("--- SEARCHING FOR WORKING MODEL ---")
found = None
for m in candidates:
    print(f"Testing {m}...")
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("Hello")
        if response.text:
            print(f"SUCCESS: {m}")
            found = m
            break
    except Exception as e:
        print(f"FAILED: {m} -> {e}")

if found:
    print(f"FOUND WORKING MODEL: {found}")
else:
    print("NO WORKING MODEL FOUND")
