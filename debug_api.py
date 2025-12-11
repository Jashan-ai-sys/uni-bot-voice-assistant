import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

try:
    from src.rag_pipeline import answer_question
    
    print("Running test query...")
    query = "Hello, who are you?"
    
    # Iterate because answer_question is a generator
    full_response = ""
    for chunk in answer_question(query):
        print(f"CHUNK: {chunk}")
        full_response += chunk
        
    print("\n--- FULL RESPONSE ---")
    print(full_response)
    print("--- END RESPONSE ---")
    
except Exception as e:
    import traceback
    traceback.print_exc()
