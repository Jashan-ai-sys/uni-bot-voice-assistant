import os
import sys
import time
from functools import lru_cache

# Imports moved to lazy loader to prevent timeout
from src.config import (
    DB_PATH, EMBED_MODEL_NAME, RERANK_MODEL_NAME, 
    MAX_CONTEXT_CHARS, RERANK_THRESHOLD, RETRIEVAL_K, CACHE_DIR,
    PINECONE_API_KEY, PINECONE_INDEX_NAME
)
from src.llm_router import get_llm
from src import cache_manager, user_storage, timetable_extractor

# --- EMBEDDINGS WRAPPER ---
class CachedEmbeddingsWrapper:
    def __init__(self, embeddings):
        self.embeddings = embeddings

    @lru_cache(maxsize=1024)
    def embed_query(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)
        
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embeddings.embed_documents(texts)

    def __call__(self, text: str) -> list[float]:
        return self.embed_query(text)

# --- LAZY RESOURCES ---
RERANKER = None
EMBEDDINGS = None
VECTORSTORE = None
_RESOURCES_LOADED = False

def _lazy_load_resources():
    """Lazy load heavy ML models only when needed"""
    global RERANKER, EMBEDDINGS, VECTORSTORE, _RESOURCES_LOADED
    if _RESOURCES_LOADED:
        return
        
    print("⏳ RAG Pipeline: Loading resources...", file=sys.stderr)
    start_load = time.time()

    # Import config and dependencies here to avoid loading at module import time
    from src.config import SKIP_RERANKER, RERANK_MODEL_NAME, CACHE_DIR
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone
    
    # 1. Reranker (Optional - can be disabled to save memory)

    if not SKIP_RERANKER:
        try:
            from flashrank import Ranker
            RERANKER = Ranker(model_name=RERANK_MODEL_NAME, cache_dir=CACHE_DIR)
            print("✅ Reranker loaded", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ Reranker failed to load: {e}", file=sys.stderr)
            RERANKER = None
    else:
        RERANKER = None
        print("⚠️ Reranker disabled (SKIP_RERANKER=true)", file=sys.stderr)

    # 2. Embeddings
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        _raw_embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        EMBEDDINGS = CachedEmbeddingsWrapper(_raw_embeddings)
    except Exception as e:
        print(f"⚠️ Embeddings failed to load: {e}", file=sys.stderr)
        EMBEDDINGS = None

    # 3. Vector Store (Pinecone)
    global VECTORSTORE
    if EMBEDDINGS and PINECONE_API_KEY:
        try:
            from langchain_pinecone import PineconeVectorStore
            from pinecone import Pinecone
            
            # Init Client to check connection (optional but good for debugging)
            pc = Pinecone(api_key=PINECONE_API_KEY)
            
            VECTORSTORE = PineconeVectorStore(
                index_name=PINECONE_INDEX_NAME, 
                embedding=EMBEDDINGS
            )
            print(f"✅ Pinecone Index '{PINECONE_INDEX_NAME}' Connected ({time.time() - start_load:.2f}s)", file=sys.stderr)
        except Exception as e:
             print(f"⚠️ Pinecone Connection Error: {e}", file=sys.stderr)
             VECTORSTORE = None
    else:
        print("⚠️ Pinecone Config Missing (API Key or Embeddings).", file=sys.stderr)
        VECTORSTORE = None
    
    _RESOURCES_LOADED = True


# --- HELPER: INTENT ---
def identify_intent(query: str) -> dict:
    query_lower = query.lower()
    intent_map = {
        "map": "map", "location": "map", "block": "map",
        "fee": "regulation", "exam": "regulation", "rule": "regulation",
        "hostel": "hostel", "mess": "hostel", "warden": "hostel",
        "emergency": "hospital", "doctor": "hospital",
        "login": "navigation", "portal": "navigation"
    }
    
    for key, doc_type in intent_map.items():
        if key in query_lower:
            return {"doc_type": doc_type}
    return None


# --- CORE: RETRIEVAL ---
def retrieve_context(query: str) -> str:
    """
    Core Retrieval Function used by MCP Server.
    """
    search_filter = identify_intent(query)
    
    # Init Resources if needed
    _lazy_load_resources()
    
    if not VECTORSTORE:
        return ""

    # Dense Search
    scores_and_docs = VECTORSTORE.similarity_search_with_score(
        query,
        k=RETRIEVAL_K, 
        filter=search_filter
    )
    
    if not scores_and_docs:
        return ""

    # Conditional Rerank
    best_score = scores_and_docs[0][1]
    
    if best_score < RERANK_THRESHOLD or not RERANKER:
        # High confidence or no reranker -> Take top
        final_docs_content = [doc.page_content for doc, score in scores_and_docs[:2]]
    else:
        # Rerank
        passages = [
            {"id": str(i), "text": doc.page_content, "meta": doc.metadata} 
            for i, (doc, score) in enumerate(scores_and_docs)
        ]
        from flashrank import RerankRequest
        rerank_request = RerankRequest(query=query, passages=passages)
        results = RERANKER.rerank(rerank_request)
        final_docs_content = [res['text'] for res in results[:2]]

    # Truncate
    context = "\n\n".join(final_docs_content)
    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS] + "..."
    
    return context


# --- CORE: ORCHESTRATION (The "Answer" Service) ---
def answer_question(query: str, student_id: str = None) -> str:
    # 1. Cache
    cached = cache_manager.get_from_cache(query)
    if cached: return cached

    # 2. Timetable Check (User Data)
    if student_id and any(k in query.lower() for k in ["class", "schedule", "timetable", "when is"]):
        tt = user_storage.get_user_timetable(student_id)
        if tt:
            res = timetable_extractor.search_timetable(tt, query)
            if res: return res

    # 3. Retrieve
    context = retrieve_context(query)
    if not context:
        return "Information not available in university records."

    # 4. Generate (Router decides LLM)
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    response = get_llm().invoke(prompt).content
    
    # 5. Cache & Return
    cache_manager.set_to_cache(query, response)
    return response


# --- STREAMING ---
async def answer_question_stream(query: str, student_id: str = None):
    # 1. Cache
    cached = cache_manager.get_from_cache(query)
    if cached: 
        yield cached
        return

    # 2. Retrieve
    context = retrieve_context(query)
    if not context:
        yield "Information not available."
        return

    # 3. Generate Stream
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    full_response = ""
    for chunk in get_llm().stream(prompt):
        if hasattr(chunk, 'content') and chunk.content:
            text = chunk.content
            full_response += text
            yield text
            
    # 4. Cache
    if full_response:
         cache_manager.set_to_cache(query, full_response)