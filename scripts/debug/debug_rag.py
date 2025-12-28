import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from rag_pipeline import get_vectorstore, answer_question_stream, answer_question

# Force utf-8 for console
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

async def test_stream():
    print("\n--- Starting Deep Debug Stream Test ---")
    query = "Where is block 34?"
    print(f"Query: {query}")
    
    # 1. Test Retrieval Speed
    t0 = time.time()
    try:
        print("Loading vectorstore...")
        vs = get_vectorstore()
        print(f"Vectorstore loaded in {time.time()-t0:.2f}s")
        
        print("Searching docs...")
        docs = vs.similarity_search(query, k=3)
        print(f"Found {len(docs)} docs in {time.time()-t0:.2f}s")
        for d in docs:
            print(f" - Doc source: {d.metadata.get('source')}")
    except Exception as e:
        print(f"Retrieval Error: {e}")
        return

    # 2. Test Stream
    print("\n--- Testing answer_question_stream ---")
    t1 = time.time()
    try:
        async for chunk in answer_question_stream(query):
            print(f"{time.time()-t1:.2f}s CHUNK: {chunk}", end=" | ", flush=True)
            t1 = time.time() # reset tick
        print("\n--- Stream Finished ---")
    except Exception as e:
        print(f"\nStream Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_stream())
