import os
import time
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from flashrank import Ranker, RerankRequest
from langchain_core.documents import Document

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_PATH = os.path.join(BASE_DIR, "db", "faiss_index")

# --- FAST PIPELINE CONFIG ---
LLM_MODEL = "phi3.5"
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "ms-marco-MiniLM-L-12-v2"
MAX_CONTEXT_CHARS = 1200 # Hard cap for velocity

# Global Cache (Simple in-memory)
CACHE = {}

def clear_cache_if_full():
    if len(CACHE) > 1000:
        CACHE.clear()
        print("🧹 Cache cleared (LRU safety)")

# Global LLM (Preloaded)
LLM = ChatOllama(
    model=LLM_MODEL,
    temperature=0.1, # Precise
    top_p=0.9,
    num_ctx=1024, # Reduced for speed
    keep_alive="1h"
)

# Global Reranker (Preloaded)
RERANKER = Ranker(model_name=RERANK_MODEL, cache_dir=os.path.join(BASE_DIR, "models"))

# Global Embeddings & VectorStore (Preloaded)
print("⏳ Loading Embeddings & Vector Store into Memory...")
start_load = time.time()
EMBEDDINGS = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL_NAME,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

if os.path.exists(DB_PATH):
    VECTORSTORE = FAISS.load_local(
        DB_PATH, 
        EMBEDDINGS, 
        allow_dangerous_deserialization=True
    )
    print(f"✅ FAISS Index Loaded ({time.time() - start_load:.2f}s)")
else:
    print("⚠️ FAISS Index not found. Please run ingest.py.")
    VECTORSTORE = None

# Startup Warmup
def warmup():
    print("🔥 Warming up pipeline...")
    try:
        if VECTORSTORE:
            VECTORSTORE.similarity_search("warmup", k=1)
        LLM.invoke("Hi")
        print("✅ Pipeline Warmed Up")
    except Exception as e:
        print(f"⚠️ Warmup failed: {e}")

# Run warmup on import
if VECTORSTORE:
    warmup()

def identify_intent(query: str) -> dict:
    """
    Analyzes query to determine if strict metadata filtering should be applied.
    """
    query_lower = query.lower()
   
    # Map keywords to doc_type
    intent_map = {
        "map": "map",
        "where is": "map",
        "location": "map",
        "block": "map",
        "parking": "map",
        "fee": "regulation",
        "scholarship": "regulation",
        "refund": "regulation",
        "exam": "regulation",
        "rule": "regulation",
        "policy": "regulation",
        "attendance": "regulation",
        "hostel": "hostel",
        "mess": "hostel",
        "laundry": "hostel",
        "room": "hostel",
        "warden": "hostel"
    }
   
    for key, doc_type in intent_map.items():
        if key in query_lower:
            return {"doc_type": doc_type}
           
    return None

def answer_question(query: str, student_id: str = None) -> str:
    """
    Answers a question using Optimized RAG (FAISS + Conditional Rerank + Cache).
    """
    # 0. Cache Check
    if query in CACHE:
        return CACHE[query]

    # Check for timetable queries first
    timetable_keywords = ["class", "schedule", "timetable", "subject", "room", "lecture", "practical", "tutorial", "when", "where", "time", "monday", "tuesday", "wednesday", "thursday", "friday", "teacher", "what time", "when is"]
    is_timetable_query = any(keyword in query.lower() for keyword in timetable_keywords)

    if student_id:
        try:
            import user_storage
            import timetable_extractor
           
            if is_timetable_query:
                timetable_data = user_storage.get_user_timetable(student_id)
                if timetable_data and timetable_data.get("schedule"):
                    result = timetable_extractor.search_timetable(timetable_data, query)
                    return result
        except Exception as e:
            print(f"Timetable check error: {e}")
   
    # Optimized Pipeline
    try:
        # Step 1: Intent / Routing (Zero Latency)
        search_filter = identify_intent(query)
        
        if not VECTORSTORE:
            return "System is initializing or index missing."

        # Step 2: Dense Retrieval (FAISS - Fast)
        # using search_with_score_by_vector (or sim_search_with_score)
        # FAISS returns L2 distance here if space is l2, or cosine dist/sim depending on init.
        # Check ingestion: ingest.py uses standard FAISS.from_documents.
        # Defaults to L2 usually unless normalized.
        # We used HuggingFaceEmbeddings with normalize_embeddings=True -> Cosine Similarity effectively (Inner Product).
        # So higher score is better if Inner Product, but FAISS default is L2 (lower is better). 
        # Actually LangChain FAISS wrapper implementation details matter. 
        # Let's perform standard search first.
        
        docs = VECTORSTORE.similarity_search(
            query,
            k=4, 
            filter=search_filter
        )
        
        # Step 3: Conditional Reranking
        # Simplistic check: if we have docs, we might rerank.
        # Elite Optimization: Check score if possible, but langchain wrapper abstracts it.
        # We will stick to the user's suggestion: "skip rerank if first doc is clearly dominant" 
        # But we need scores for that.
        
        docs_and_scores = VECTORSTORE.similarity_search_with_score(query, k=4, filter=search_filter)
        
        # In FAISS (LangChain default L2), Lower score = Better match.
        # If score < 0.3 (arbitrary threshold for "very close"), skip rerank.
        # NOTE: user said "similarity_search_with_score", assumes cosine distance? 
        # The ingestion used normalize_embeddings=True. 
        # If FAISS.from_documents was used, it uses IndexFlatL2 by default.
        # With normalized vectors, L2 distance is related to cosine similarity.
        # L2 = 2 * (1 - cosine_similarity). 
        # So cosine_sim = 1 -> L2 = 0.
        # cosine_sim = 0.9 -> L2 = 0.2. 
        # So score < 0.2 is a very good match.
        
        should_rerank = True
        if docs_and_scores:
            best_score = docs_and_scores[0][1]
            # L2 distance on normalized vectors:
            # L2 ≈ 2 * (1 - cosine_similarity)
            # score < 0.25 ≈ cosine_sim > 0.875
            if best_score < 0.25: # High confidence
                should_rerank = False
                # Just take the top doc or top 2
                final_docs_content = [doc.page_content for doc, score in docs_and_scores[:2]]
            else:
                # Prepare for rerank
                passages = [
                    {"id": str(i), "text": doc.page_content, "meta": doc.metadata} 
                    for i, (doc, score) in enumerate(docs_and_scores)
                ]
                rerank_request = RerankRequest(query=query, passages=passages)
                results = RERANKER.rerank(rerank_request)
                top_results = results[:3] # Keep top 3 after rerank
                final_docs_content = [res['text'] for res in top_results]
        else:
             final_docs_content = []

        # Step 4: Context Construction (Truncated)
        context = "\n\n".join(final_docs_content)
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS] + "..." # Hard truncation
            
        if not context:
            return "Information not available in university records."

        # Step 5: Final Answer (Phi-3.5) with Strict Prompt
        system_prompt = f"""You are JARVIS. Answer ONLY from the content below.
        If the answer is not present, say "Information not available in university records."
        
        Content:
        {context}
        
        Question: {query}
        
        Answer:"""
        
        response = LLM.invoke(system_prompt)
        content = response.content
        
        # Cache result
        clear_cache_if_full()
        CACHE[query] = content
        return content

    except Exception as e:
        print(f"Pipeline Error: {e}")
        return "I encountered an error. Please try again."

async def answer_question_stream(query: str, student_id: str = None):
    """
    Streaming version of answer_question.
    """
    # 0. Cache Check (Not easily streamable unless we fake stream, but worth it for speed)
    if query in CACHE:
        yield CACHE[query]
        return

    # Check for timetable queries first
    timetable_keywords = ["class", "schedule", "timetable", "subject", "room", "lecture", "practical", "tutorial", "when", "where", "time", "monday", "tuesday", "wednesday", "thursday", "friday", "teacher", "what time", "when is"]
    is_timetable_query = any(keyword in query.lower() for keyword in timetable_keywords)

    if student_id:
        try:
            import user_storage
            import timetable_extractor
           
            if is_timetable_query:
                timetable_data = user_storage.get_user_timetable(student_id)
                if timetable_data and timetable_data.get("schedule"):
                    result = timetable_extractor.search_timetable(timetable_data, query)
                    words = result.split()
                    for i in range(0, len(words), 3):
                        yield " ".join(words[i:i+3]) + " "
                    return
        except Exception as e:
            print(f"Timetable check error: {e}")
   
    # Optimized Pipeline (Streaming)
    try:
        # Step 1: Intent
        search_filter = identify_intent(query)
        
        if not VECTORSTORE:
             yield "System is initializing."
             return
        
        # Step 2: Dense Retrieval (FAISS)
        docs_and_scores = VECTORSTORE.similarity_search_with_score(
            query,
            k=4,
            filter=search_filter
        )
        
        # Step 3: Conditional Reranking
        if docs_and_scores and docs_and_scores[0][1] < 0.25:
             # Fast path
             final_docs_content = [doc.page_content for doc, score in docs_and_scores[:2]]
        elif docs_and_scores:
            # Rerank path
            passages = [
                {"id": str(i), "text": doc.page_content, "meta": doc.metadata} 
                for i, (doc, score) in enumerate(docs_and_scores)
            ]
            rerank_request = RerankRequest(query=query, passages=passages)
            results = RERANKER.rerank(rerank_request)
            top_results = results[:3]
            final_docs_content = [res['text'] for res in top_results]
        else:
             final_docs_content = []

        # Step 4: Context
        context = "\n\n".join(final_docs_content)
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS] + "..."

        if not context:
            yield "Information not available in university records."
            return

        # Step 5: Stream Answer
        system_prompt = f"""You are JARVIS. Answer ONLY from the content below.
        If the answer is not present, say "Information not available in university records."
        
        Content:
        {context}
        
        Question: {query}
        
        Answer:"""

        full_response = ""
        for chunk in LLM.stream(system_prompt):
             if hasattr(chunk, 'content') and chunk.content:
                text = chunk.content
                full_response += text
                yield text
        
        # Cache the full response for next time
        if full_response:
            clear_cache_if_full()
            CACHE[query] = full_response

    except Exception as e:
        print(f"Streaming Pipeline Error: {e}")
        yield f"⚠️ Error: {str(e)}"

if __name__ == "__main__":
    print("🤖 Optimized RAG Pipeline Test")
    print("Type 'exit' to quit.")
    while True:
        q = input("\nAsk a question: ")
        if q.lower() == 'exit': break
        ans = answer_question(q)
        print(f"\nAnswer: {ans}")