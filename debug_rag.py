import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import collections

load_dotenv()

# Define the persistence directory
DB_PATH = "./db"

def debug_rag():
    print("Debugging RAG System...")
    
    # Initialize Embeddings
    if not os.getenv("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY not found in environment variables")
        return

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # Load Vector DB
    if not os.path.exists(DB_PATH):
        print(f"Database path {DB_PATH} does not exist")
        return
        
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    
    # Accessing the underlying chromadb collection
    collection = vectorstore._collection
    count = collection.count()
    print(f"Total Chunks in DB: {count}")
    
    # Get metadata to analyze sources
    result = collection.get()
    metadatas = result['metadatas']
    
    sources = [m.get('source', 'unknown') for m in metadatas]
    source_counts = collections.Counter(sources)
    
    print("\nDocument Distribution (Chunks per File):")
    sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
    for source, count in sorted_sources:
        # Clean up path for display
        filename = os.path.basename(source)
        print(f"  - {filename}: {count} chunks")
        
    print("\nTesting Retrieval for 'Placement'")
    query = "placement process"
    results = vectorstore.similarity_search_with_score(query, k=10)
    
    print(f"\nTop 10 Results for '{query}':")
    for i, (doc, score) in enumerate(results):
        filename = os.path.basename(doc.metadata.get('source', 'unknown'))
        print(f"  {i+1}. [{score:.4f}] {filename} (Content snippet: {doc.page_content[:50]}...)")

if __name__ == "__main__":
    debug_rag()
