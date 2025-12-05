import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Load environment variables
load_dotenv()

DATA_PATH = "./data"
DB_PATH = "./db"

def ingest_docs():
    """
    Loads PDFs from the data directory, splits them into chunks,
    and stores them in a Chroma vector database.
    """
    print("🚀 Starting ingestion...")
    
    # 1. Load Documents
    documents = []
    # Find all PDF files
    pdf_files = glob.glob(os.path.join(DATA_PATH, "**/*.pdf"), recursive=True)
    # Find all Word documents
    docx_files = glob.glob(os.path.join(DATA_PATH, "**/*.docx"), recursive=True)
    doc_files = glob.glob(os.path.join(DATA_PATH, "**/*.doc"), recursive=True)
    # Find all Text files
    txt_files = glob.glob(os.path.join(DATA_PATH, "**/*.txt"), recursive=True)
    
    all_files = pdf_files + docx_files + doc_files + txt_files
    
    if not all_files:
        print("⚠️ No documents found in ./data. Please add some files.")
        return

    print(f"📄 Found {len(all_files)} document(s). Loading...")
    
    for file_path in all_files:
        try:
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith('.txt'):
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(file_path, encoding='utf-8')
            else:  # .docx or .doc
                from langchain_community.document_loaders import UnstructuredWordDocumentLoader
                loader = UnstructuredWordDocumentLoader(file_path)
            
            docs = loader.load()
            documents.extend(docs)
            print(f"  - Loaded: {file_path}")
        except Exception as e:
            print(f"  - Error loading {file_path}: {e}")

    if not documents:
        print("❌ No documents loaded.")
        return

    # 2. Split Documents
    print(f"✂️ Splitting {len(documents)} documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    print(f"🧩 Created {len(chunks)} chunks.")

    # 3. Create Embeddings & Store in Chroma
    print("💾 Creating embeddings and storing in Vector DB (this may take a moment)...")
    
    # Ensure Google API Key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
        return

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # Clear existing DB to prevent duplicates
    if os.path.exists(DB_PATH):
        import shutil
        print(f"🧹 Clearing existing database at {DB_PATH}...")
        shutil.rmtree(DB_PATH)

    # Create Chroma instance
    vectorstore = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    # Batch process chunks to avoid hitting rate limits
    BATCH_SIZE = 10
    import time
    import uuid
    
    print(f"⏳ Processing {len(chunks)} chunks in batches of {BATCH_SIZE}...")
    
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        
        # Generate unique IDs for each chunk to ensure no skips
        ids = [str(uuid.uuid4()) for _ in batch]
        
        vectorstore.add_documents(documents=batch, ids=ids)
        print(f"  - Processed batch {i//BATCH_SIZE + 1}/{(len(chunks) + BATCH_SIZE - 1)//BATCH_SIZE}")
        time.sleep(1) # Sleep to respect rate limits
    
    print(f"✅ Ingestion complete! Vector DB saved to {DB_PATH}")

if __name__ == "__main__":
    ingest_docs()
