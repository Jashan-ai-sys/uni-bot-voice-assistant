"""
Check which Gemini models are available with this API key
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("🔍 Listing all available Gemini models:\n")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Methods: {model.supported_generation_methods}")
        print()

print("=" * 60)
print("\n📌 Recommended models for streaming:")
print("   - For LangChain: Use display name WITHOUT 'models/' prefix") 
print("   - For direct genai: Use full name WITH 'models/' prefix")
