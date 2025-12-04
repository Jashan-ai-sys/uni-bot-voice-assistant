import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def test_embedding():
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        print("Attempting to embed a single string...")
        vector = embeddings.embed_query("Hello world")
        print(f"Success! Vector length: {len(vector)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_embedding()
