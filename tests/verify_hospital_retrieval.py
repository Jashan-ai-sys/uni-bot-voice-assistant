import sys
import os
import time

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_pipeline import retrieve_context, identify_intent, VECTORSTORE

def test_hospital_retrieval():
    query = "Give me the UMS navigation to apply hospital leave"
    print(f"Testing retrieval for query: '{query}'")
    
    # Check Intent
    intent = identify_intent(query)
    print(f"Identified Intent: {intent}")
    
    # Check VectorStore
    if not VECTORSTORE:
        print("❌ VECTORSTORE not loaded.")
        return

    try:
        # Search specifically for the added path
        results = VECTORSTORE.similarity_search(query, k=3, filter=intent)
        
        if results:
            print(f"✅ Found {len(results)} docs.")
            for i, doc in enumerate(results):
                print(f"\n-- Doc {i+1} --")
                print(f"Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"Type: {doc.metadata.get('doc_type', 'Unknown')}")
                print(f"Content: {doc.page_content[:300]}...")
                
                if "UMS Navigation" in doc.page_content and "Residential Services" in doc.page_content:
                     print("✅ SUCCESS: Found Navigation Path!")
        else:
            print("❌ No results found with filter.")
            
            # Try without filter
            print("\nRetrying without filter...")
            results_nofilter = VECTORSTORE.similarity_search(query, k=3)
            for i, doc in enumerate(results_nofilter):
                print(f"\n-- Doc {i+1} (No Filter) --")
                print(f"Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"Content: {doc.page_content[:100]}...")

    except Exception as e:
        print(f"❌ Error during search: {e}")

if __name__ == "__main__":
    test_hospital_retrieval()
