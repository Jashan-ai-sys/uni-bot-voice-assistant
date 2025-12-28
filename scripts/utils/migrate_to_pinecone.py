
import os
import sys
import time

# Add root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from src.config import (
    DB_PATH, EMBED_MODEL_NAME, PINECONE_API_KEY, PINECONE_INDEX_NAME
)

def migrate():
    print("🚀 Starting Migration: FAISS -> Pinecone")
    
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found in env.")
        return

    # 1. Load Embeddings (CPU)
    print(f"⏳ Loading Embeddings Model ({EMBED_MODEL_NAME})...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # 2. Load FAISS (Source)
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: FAISS index not found at {DB_PATH}")
        return
        
    print(f"⏳ Loading Source FAISS Index from {DB_PATH}...")
    try:
        faiss_db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
        # Extract docs - FAISS doesn't have a direct 'get_all_docs' easily, 
        # but we can rely on the docstore if it's in memory.
        # Hack: Access the docstore directly
        docs = list(faiss_db.docstore._dict.values())
        print(f"✅ Loaded {len(docs)} documents from FAISS.")
    except Exception as e:
        print(f"❌ Fail to load FAISS: {e}")
        return

    # 3. Init Pinecone (Destination)
    print(f"⏳ Connecting to Pinecone Index '{PINECONE_INDEX_NAME}'...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Check if index exists, create if not (Serverless)
    existing_indexes = [i.name for i in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        print(f"⚠️ Index '{PINECONE_INDEX_NAME}' not found. Creating it...")
        try:
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=384, # BGE-Small dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print("✅ Index created. Waiting for initialization...")
            time.sleep(10)
        except Exception as e:
            print(f"❌ Failed to create index: {e}")
            return

    # 4. Upsert
    print("⏳ Upserting documents to Pinecone (this may take a while)...")
    try:
        PineconeVectorStore.from_documents(
            docs, 
            embeddings, 
            index_name=PINECONE_INDEX_NAME
        )
        print("✅ Migration Complete! Documents are now in the cloud. ☁️")
    except Exception as e:
        print(f"❌ Upload Failed: {e}")

if __name__ == "__main__":
    migrate()
