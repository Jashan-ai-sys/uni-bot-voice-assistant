
import sys
import os
sys.path.append('src')

try:
    from src.rag_pipeline import answer_question
    print("Attempting to query...")
    response = answer_question("tell me about lpu")
    print(f"Response: {response}")
except Exception as e:
    import traceback
    traceback.print_exc()
