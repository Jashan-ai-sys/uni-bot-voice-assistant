import google.generativeai as genai
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

candidates = [
    "models/gemini-2.5-flash-001",
    "models/gemini-2.0-flash-exp"
]

print("--- MODEL CHECK ---")
for m in candidates:
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("Hi")
        print(f"WORKS: {m}")
    except Exception as e:
        print(f"FAILS: {m} -> {str(e)[:50]}...")
print("--- END ---")
