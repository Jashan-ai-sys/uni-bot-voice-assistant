import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from rag_pipeline import get_vectorstore, answer_question

# Force utf-8 for console
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_sync():
    print("\n--- Starting Deep Debug SYNC Test ---")
    query = "Where is block 34?"
    print(f"Query: {query}")
    
    # 1. Test Retrieval Speed
    t0 = time.time()
    try:
        print("answer_question() calling...")
        ans = answer_question(query)
        print(f"Result: {ans[:100]}...")
        print(f"Time taken: {time.time()-t0:.2f}s")
    except Exception as e:
        print(f"Sync Error: {e}")

if __name__ == "__main__":
    test_sync()
