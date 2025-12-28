import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content("Test")
    print("Gemini 1.5 Pro works.")
except Exception as e:
    print(f"Gemini 1.5 Pro failed: {e}")
