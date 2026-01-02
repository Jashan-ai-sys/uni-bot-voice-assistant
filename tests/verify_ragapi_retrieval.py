import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_pipeline import VECTORSTORE

def test_retrieval():
    print(f"Testing retrieval in: {os.getcwd()}")
    
    if VECTORSTORE:
        print("✅ VECTORSTORE is loaded.")
        try:
             # Search for placement policies
            query = "what are the placement policies"
            results = VECTORSTORE.similarity_search(query, k=2)
            if results:
                print(f"✅ Found {len(results)} docs.")
                for i, doc in enumerate(results):
                    print(f"\n-- Doc {i+1} --")
                    print(f"Source: {doc.metadata.get('source', 'Unknown')}")
                    print(f"Content: {doc.page_content[:200]}...")
            else:
                print("❌ VECTORSTORE returned no results.")
        except Exception as e:
            print(f"❌ Error querying VECTORSTORE: {e}")
    else:
        print("❌ VECTORSTORE is FAIL (None).")

if __name__ == "__main__":
    test_retrieval()
