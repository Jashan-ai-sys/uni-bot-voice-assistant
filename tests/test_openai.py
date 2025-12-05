import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

try:
    print("Initializing ChatOpenAI...")
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="google/gemini-2.0-flash-exp:free",
    )
    print("ChatOpenAI initialized.")
    
    print("Invoking...")
    response = llm.invoke("Hello, are you Claude?")
    print(f"Response: {response.content}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
