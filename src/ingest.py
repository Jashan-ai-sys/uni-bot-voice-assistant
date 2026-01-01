import os
import glob
import time
import uuid
import warnings
import shutil
from dotenv import load_dotenv

# Filter warnings
warnings.filterwarnings("ignore")

# LangChain Imports
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_ollama import OllamaEmbeddings # Switched to HF
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

DATA_PATH = "./data"
DB_PATH = "./db/faiss_index"

def get_doc_type(file_path):
    """
    Determines document type based on parent directory.
    """
    abs_path = os.path.abspath(file_path)
    parent_dir = os.path.basename(os.path.dirname(abs_path))
    
    # Check if parent dir is 'data' (root files)
    if os.path.basename(os.path.abspath(DATA_PATH)) == parent_dir:
        return "general"
        
    keyword_map = {
        "maps": "map",
        "academics": "academic",
        "admissions": "admission",
        "exams": "exam",
        "hostel": "hostel",
        "hospital": "health",
        "leave": "leave_policy",
        "facilities": "facility",
        "transport": "transport",
        "users": "user_data"
    }
    
    return keyword_map.get(parent_dir.lower(), "general")

def ingest_docs():
    """
    Loads docs, splits with Universal Strategy (400/60), and stores in FAISS.
    """
    print("🚀 Starting Optimized Ingestion (FAISS + bge-small)...")
    
    # 1. Load Documents
    # documents = [] removed (unused)
    
    # Helper to find files
    def find_files(ext):
        return glob.glob(os.path.join(DATA_PATH, f"**/*{ext}"), recursive=True)
    
    all_files = find_files(".pdf") + find_files(".docx") + find_files(".doc") + find_files(".txt") + find_files(".json")
    
    if not all_files:
        print("⚠️ No documents found.")
        return

    print(f"📄 Found {len(all_files)} document(s). Processing...")
    
    loaded_docs = []
    
    for file_path in all_files:
        try:
            # Determine loader
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith('.txt'):
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_path.endswith('.json'):
                loader = JSONLoader(file_path, jq_schema='.', text_content=False)
            else:
                loader = UnstructuredWordDocumentLoader(file_path)
            
            docs = loader.load()
            
            # Enrich Metadata
            doc_type = get_doc_type(file_path)
            
            for doc in docs:
                doc.metadata['source'] = os.path.basename(file_path)
                doc.metadata['doc_type'] = doc_type
                
            loaded_docs.extend(docs)
            print(f"  - Loaded: {os.path.basename(file_path)} [{doc_type}]")
            
        except Exception as e:
            print(f"  - Error loading {file_path}: {e}")

    # 2. Split Documents (Universal Strategy)
    print("✂️ Splitting documents (Chunk: 400, Overlap: 60)...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, 
        chunk_overlap=60
    )
    
    all_chunks = splitter.split_documents(loaded_docs)
    print(f"🧩 Total chunks created: {len(all_chunks)}")

    # 3. Create Embeddings & Store in FAISS
    print("⚗️ Generating embeddings with bge-small-en-v1.5 (HuggingFace)...")
    
    # Use bge-small for speed (Runs in-process, no API latency)
    model_name = "BAAI/bge-small-en-v1.5"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    # Clean old db if exists
    if os.path.exists("./db/faiss_index"):
        shutil.rmtree("./db/faiss_index")
        time.sleep(1)
    
    if not os.path.exists("./db"):
        os.makedirs("./db")

    print(f"⏳ Indexing {len(all_chunks)} chunks into FAISS...")
    try:
        vectorstore = FAISS.from_documents(all_chunks, embeddings)
        vectorstore.save_local(DB_PATH)
        print(f"✅ Ingestion complete! FAISS index saved to {DB_PATH}")
    except Exception as e:
        print(f"❌ Error creating FAISS index: {e}")

if __name__ == "__main__":
    ingest_docs()
