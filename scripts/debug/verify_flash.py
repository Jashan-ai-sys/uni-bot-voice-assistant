import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

# Force utf-8 for stdout just in case
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

candidates = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-001",
    "models/gemini-1.5-flash-002",
    "models/gemini-1.5-flash-8b",
    "models/gemini-1.5-flash-latest",
]

log = []
log.append("Testing candidates...")

success = False
for model_name in candidates:
    log.append(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        if response.text:
            log.append(f"[SUCCESS] {model_name} works!")
            success = True
            break
    except Exception as e:
        log.append(f"[FAILURE] {model_name}: {e}")

with open("verification.log", "w", encoding="utf-8") as f:
    f.write("\n".join(log))

print("Done.")
