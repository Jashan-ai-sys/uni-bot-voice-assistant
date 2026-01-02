import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load .env
load_dotenv()

BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, "db", "faiss_index")
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"

print(f"📂 DB Path: {DB_PATH}")

# Mock Intent Logic
def identify_intent(query: str):
    query_lower = query.lower()
    intent_map = {
        "map": "map", "where is": "map", "location": "map", "block": "map", "parking": "map",
        "fee": "regulation", "scholarship": "regulation", "refund": "regulation", "exam": "regulation", 
        "rule": "regulation", "policy": "regulation", "attendance": "regulation",
        "hostel": "hostel", "mess": "hostel", "laundry": "hostel", "room": "hostel", "warden": "hostel"
    }
    for key, doc_type in intent_map.items():
        if key in query_lower:
            return {"doc_type": doc_type}
    return None

try:
    print("⏳ Loading Embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print("⏳ Loading VectorStore...")
    vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
    
    queries = [
        "Give me the UMS navigation to apply hostel leave.",
        "How can I meet her?"
    ]
    
    for q in queries:
        print(f"\n🔍 Query: '{q}'")
        search_filter = identify_intent(q)
        print(f"   ► Inferred Filter: {search_filter}")
        
        docs_and_scores = vectorstore.similarity_search_with_score(q, k=4, filter=search_filter)
        
        if not docs_and_scores:
            print("   ❌ No documents found.")
        
        for i, (doc, score) in enumerate(docs_and_scores):
            print(f"   📄 Doc {i+1} (Score: {score:.4f}):")
            print(f"      Metadata: {doc.metadata}")
            print(f"      Content: {doc.page_content[:150]}...")

except Exception as e:
    print(f"❌ Error: {e}")
