import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load env (just for path safety, though not strictly needed for local FAISS if preloaded)
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "faiss_index")
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"

print(f"Loading FAISS from {DB_PATH}...")
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
try:
    vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
    print("✅ Vectorstore loaded.")
except Exception as e:
    print(f"❌ Failed to load vectorstore: {e}")
    sys.exit(1)

def test_query(q):
    print(f"\n🔎 Testing Query: '{q}'")
    docs = vectorstore.similarity_search_with_score(q, k=2)
    for doc, score in docs:
        print(f"   - [{score:.4f}] {doc.page_content[:100]}...")

# Test 1: The failing query
test_query("where can i meet her in person")

# Test 2: The explicit query
test_query("where can i meet Rashmi Mittal in person")
