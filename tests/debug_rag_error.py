from rag_pipeline import get_vectorstore
import traceback

try:
    print("Initializing vector store...")
    vectorstore = get_vectorstore()
    
    print("Running search...", flush=True)
    docs = vectorstore.max_marginal_relevance_search(
        "test query", 
        k=1,
        fetch_k=5,
        lambda_mult=0.7
    )
    print(f"Found {len(docs)} docs", flush=True)
    for doc in docs:
        print(doc.page_content[:50], flush=True)

except Exception:
    traceback.print_exc()
