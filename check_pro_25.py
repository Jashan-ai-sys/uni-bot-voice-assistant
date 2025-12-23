import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model_name = "models/gemini-2.5-pro"
print(f"Testing {model_name}...")

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
