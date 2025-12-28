import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Force utf-8
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

import google.generativeai as genai

# Force REST transport globally
genai.configure(transport='rest')

def test_model():
    print("--- Testing gemini-2.0-flash DIRECTLY (REST) ---")
    try:
        # Valid init without transport arg
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash-lite-001", 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        template = "Answer looking for: {query}"
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser()
        
        print("Invoking chain...")
        res = chain.invoke({"query": "Hello"})
        print(f"Result: {res}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_model()
