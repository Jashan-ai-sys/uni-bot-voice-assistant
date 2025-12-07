import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
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
        "users": "user_data"
    }
    
    return keyword_map.get(parent_dir.lower(), "general")

def get_chunk_size(doc_type):
    """
    Returns optimal chunk size for the document type.
    """
    if doc_type == "map":
        return 350, 50 
    elif doc_type == "regulation":
        return 800, 100
    elif doc_type == "hostel":
        return 600, 100
    else:
        return 500, 100

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
    
    all_files = find_files(".pdf") + find_files(".docx") + find_files(".doc") + find_files(".txt")
    
    if not all_files:
        print("⚠️ No documents found.")
        return

    print(f"📄 Found {len(all_files)} document(s). Processing...")
    
    # Store docs by recommended chunk size for batch processing
    # Key: (chunk_size, chunk_overlap) -> List[Document]
    docs_by_strategy = {}
    
    for file_path in all_files:
        try:
            # Determine loader
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith('.txt'):
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                loader = UnstructuredWordDocumentLoader(file_path)
            
            loaded_docs = loader.load()
            
            # Enrich Metadata
            doc_type = get_doc_type(file_path)
            strategy = get_chunk_size(doc_type)
            
            for doc in loaded_docs:
                doc.metadata['source'] = os.path.basename(file_path)
                doc.metadata['doc_type'] = doc_type
                # Page number is usually auto-added by PyPDFLoader as 'page'
                
            if strategy not in docs_by_strategy:
                docs_by_strategy[strategy] = []
            docs_by_strategy[strategy].extend(loaded_docs)
            
            print(f"  - Loaded: {os.path.basename(file_path)} [{doc_type}]")
            
        except Exception as e:
            print(f"  - Error loading {file_path}: {e}")

    # 2. Split Documents
    all_chunks = []
    
    print("✂️ Splitting documents with variable strategies...")
    for (chunk_size, chunk_overlap), docs in docs_by_strategy.items():
        if not docs: continue
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)
        print(f"  - Strategy ({chunk_size}/{chunk_overlap}): Created {len(chunks)} chunks from {len(docs)} pages.")

    print(f"🧩 Total chunks created: {len(all_chunks)}")

    # 3. Create Embeddings & Store in Chroma
    print("💾 Creating embeddings and storing...")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY missing.")
        return

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    if os.path.exists(DB_PATH):
        import shutil
        shutil.rmtree(DB_PATH)
        time.sleep(1) # Wait for filesystem

    vectorstore = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    # Batch process
    BATCH_SIZE = 10 
    print(f"⏳ Processing {len(all_chunks)} chunks...")
    
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i:i + BATCH_SIZE]
        ids = [str(uuid.uuid4()) for _ in batch]
        
        try:
            vectorstore.add_documents(documents=batch, ids=ids)
            print(f"  - Processed batch {i//BATCH_SIZE + 1}/{(len(all_chunks) + BATCH_SIZE - 1)//BATCH_SIZE}")
            time.sleep(1)
        except Exception as e:
            print(f"  - Error processing batch: {e}")
    
    print(f"✅ Ingestion complete! Vector DB saved to {DB_PATH}")

if __name__ == "__main__":
    ingest_docs()
