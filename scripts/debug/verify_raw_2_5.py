import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"), transport='rest')

def test_raw_genai():
    print("--- Testing Raw genai with gemini-2.5-flash ---")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Hello, can you help me?")
        print(f"Response Text: {response.text}")
        print("--- Success ---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_raw_genai()
