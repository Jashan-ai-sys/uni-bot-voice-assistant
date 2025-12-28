import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model_name = "models/gemini-2.0-flash-exp"
print(f"Testing {model_name}...")

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
