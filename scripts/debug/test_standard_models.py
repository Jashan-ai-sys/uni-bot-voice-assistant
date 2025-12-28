import google.generativeai as genai
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

candidates = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-001",
    "models/gemini-1.5-flash-002",
    "models/gemini-1.5-flash-8b",
    "models/gemini-1.5-pro",
    "models/gemini-1.0-pro",
    "models/gemini-pro"
]

results = []

print("--- START TEST ---")
for m in candidates:
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("Hi")
        print(f"PASS: {m}")
        results.append(m)
    except Exception as e:
        print(f"FAIL: {m} -> {e}")
print("--- END TEST ---")

if results:
    print(f"RECOMMENDED: {results[0]}")
else:
    print("RECOMMENDED: NONE")
