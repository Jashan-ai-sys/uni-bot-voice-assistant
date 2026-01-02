import sys
import os

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag_pipeline import retrieve_context, identify_intent, VECTORSTORE

def test():
    query = "Give me the UMS navigation to apply hospital leave"
    print(f"Testing: {query}")
    
    intent = identify_intent(query)
    print(f"Intent: {intent}")
    
    if not VECTORSTORE:
        print("VECTORSTORE IS NONE")
        return

    # Test with filter
    print("Searching with filter...")
    docs = VECTORSTORE.similarity_search(query, k=3, filter=intent)
    for d in docs:
        print(f"FOUND: {d.page_content[:100]}... [Source: {d.metadata.get('source')}]")
        
    if not docs:
        print("No docs with filter. Searching without...")
        docs = VECTORSTORE.similarity_search(query, k=3)
        for d in docs:
            print(f"FOUND (No Filter): {d.page_content[:100]}... [Source: {d.metadata.get('source')}]")

if __name__ == "__main__":
    test()
