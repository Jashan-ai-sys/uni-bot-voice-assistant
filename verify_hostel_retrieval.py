import sys
import os

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag_pipeline import identify_intent, VECTORSTORE

def test():
    query = "give me the ums navigation to apply hostel leave"
    print(f"Testing: {query}")
    
    intent = identify_intent(query)
    print(f"Intent: {intent}")
    
    if not VECTORSTORE:
        print("VECTORSTORE IS NONE. Ensure DB_PATH exists and is valid.")
        return

    print("Searching with filter...")
    # Intent might be 'navigation' or 'academic' depending on keywords.
    # We expect 'navigation' because of 'navigation' keyword.
    docs = VECTORSTORE.similarity_search(query, k=3, filter=intent)
    print(f"Docs found: {len(docs)}")
    found_target = False
    for i, d in enumerate(docs):
        # clean up newlines for cleaner log
        content_preview = d.page_content.replace("\n", " ")[:100]
        print(f"[{i+1}] {content_preview}...")
        
        if "RES.2" in d.page_content or "Apply Leave" in d.page_content:
            print(f"✅ SUCCESS: Found Target Doc! (Rank {i+1})")
            print(f"FULL CONTENT: {d.page_content}")
            found_target = True

    if not found_target:
        print("❌ WARNING: Target 'RES.2' or 'Apply Leave' NOT found in top K.")

if __name__ == "__main__":
    test()
