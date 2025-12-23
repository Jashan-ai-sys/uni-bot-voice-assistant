import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings  # Local embeddings
from langchain_chroma import Chroma
import time
import uuid

# Load environment variables
load_dotenv()

DATA_PATH = "./data"
DB_PATH = "./db"

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
        "academics": "regulation",
        "admissions": "regulation",
        "exams": "regulation",
        "hostel": "hostel",
        "hospital": "hospital",
        "users": "user_data"
    }
    
    return keyword_map.get(parent_dir.lower(), "general")

def get_chunk_size(doc_type):
    """
    Returns optimal chunk size for the document type.
    Standardized to 300/40 for all types for consistent performance.
    """
    # Use unified strategy for all types including hospital
    return 300, 40

def ingest_docs():
    """
    Loads docs, enriches metadata, splits with variable strategies, and stores in Chroma.
    """
    print("🚀 Starting optimized ingestion...")
    
    # 1. Load Documents
    documents = []
    
    # Helper to find files
    def find_files(ext):
        return glob.glob(os.path.join(DATA_PATH, f"**/*{ext}"), recursive=True)
    
    all_files = find_files(".pdf") + find_files(".docx") + find_files(".doc") + find_files(".txt") + find_files(".json")
    
    if not all_files:
        print("⚠️ No documents found.")
        return

    print(f"📄 Found {len(all_files)} document(s). Processing...")
    
    # 1a. Load All Documents
    all_loaded_docs = []
    
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
            
            loaded_docs = loader.load()
            
            # Enrich Metadata
            doc_type = get_doc_type(file_path)
            
            for doc in loaded_docs:
                doc.metadata['source'] = os.path.basename(file_path)
                doc.metadata['doc_type'] = doc_type
                
            all_loaded_docs.extend(loaded_docs)
            print(f"  - Loaded: {os.path.basename(file_path)} [{doc_type}]")
            
        except Exception as e:
            print(f"  - Error loading {file_path}: {e}")
    
    # 2. Split Documents (Unified Strategy)
    print("✂️ Splitting documents (300 chars / 40 overlap)...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, 
        chunk_overlap=40
    )
    
    # Split the loaded docs
    all_chunks = splitter.split_documents(all_loaded_docs)
    print(f"🧩 Total chunks created: {len(all_chunks)}")

    # 3. Create Embeddings & Store in Chroma
    print("💾 Creating embeddings and storing...")
    
    # Use local embeddings - no API calls!
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    if os.path.exists(DB_PATH):
        import shutil
        shutil.rmtree(DB_PATH)
        time.sleep(1) # Wait for filesystem

    vectorstore = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}  # HNSW for fast search
    )

    # Batch process
    BATCH_SIZE = 100  # Increased for speed
    print(f"⏳ Processing {len(all_chunks)} chunks (Batch size: {BATCH_SIZE})...")
    
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i:i + BATCH_SIZE]
        ids = [str(uuid.uuid4()) for _ in batch]
        
        try:
            vectorstore.add_documents(documents=batch, ids=ids)
            print(f"  - Processed batch {i//BATCH_SIZE + 1}/{(len(all_chunks) + BATCH_SIZE - 1)//BATCH_SIZE}")
            # Removed sleep for performance
        except Exception as e:
            print(f"  - Error processing batch: {e}")
    
    print(f"✅ Ingestion complete! Vector DB saved to {DB_PATH}")

if __name__ == "__main__":
    ingest_docs()
