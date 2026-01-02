import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag_pipeline import identify_intent, VECTORSTORE

def test():
    query = "If I've applied for a day extended leave, what are the possibilities to convert the leaves?"
    print(f"Testing: {query}")
    
    intent = identify_intent(query)
    print(f"Intent: {intent}")
    
    if not VECTORSTORE:
        print("VECTORSTORE IS NONE.")
        return

    # Intent should be 'leave_policy' now
    docs = VECTORSTORE.similarity_search(query, k=3, filter=intent)
    found = False
    for i, d in enumerate(docs):
        print(f"\n[Doc {i+1}] {d.page_content[:200]}...")
        if "Converting Extended Leave" in d.page_content or "HOD with proof" in d.page_content:
             print("✅ SUCCESS: Found leave conversion policy!")
             found = True
             
    if not found:
        print("❌ WARNING: Did not find the new leave conversion policy.")

if __name__ == "__main__":
    test()
