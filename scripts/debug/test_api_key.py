import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

print(f"API Key (first 25 chars): {api_key[:25] if api_key else 'NONE'}")
print(f"API Key length: {len(api_key) if api_key else 0}")

# Try a simple API call
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    response = model.generate_content("Say 'API key works!'")
    print(f"\n✅ SUCCESS: {response.text}")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
