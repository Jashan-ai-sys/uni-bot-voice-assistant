import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys

# Force utf-8
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_model(model_name):
    print(f"\n--- Testing {model_name} ---")
    try:
        llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))
        template = "Answer looking for: {query}"
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser()
        
        for chunk in chain.stream({"query": "Hello"}):
            print(chunk, end="", flush=True)
        print("\nSuccess!")
    except Exception as e:
        print(f"\nFailed: {e}")

test_model("models/gemini-2.5-flash")
print("\n" + "="*30 + "\n")
test_model("models/gemini-2.0-flash")
