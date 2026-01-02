import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag_pipeline import identify_intent, VECTORSTORE

def test():
    query = "give me the uni hospital emergency number"
    print(f"Testing: {query}")
    
    intent = identify_intent(query)
    print(f"Intent: {intent}")
    
    if not VECTORSTORE:
        print("VECTORSTORE IS NONE.")
        return

    docs = VECTORSTORE.similarity_search(query, k=3, filter=intent)
    found = False
    for i, d in enumerate(docs):
        print(f"\n[Doc {i+1}] {d.page_content[:200]}...")
        if "9780036450" in d.page_content: # Hospital Reception
             print("✅ SUCCESS: Found explicit hospital number!")
             found = True
             
    if not found:
        print("❌ WARNING: Did not find the new numbers.")

if __name__ == "__main__":
    test()
