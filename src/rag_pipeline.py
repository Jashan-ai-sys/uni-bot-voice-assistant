import os
import time
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from flashrank import Ranker, RerankRequest
from langchain_core.documents import Document

# Import smart cache and API key rotator
try:
    from smart_cache import get_cached_response, cache_response, get_cache_stats
    SMART_CACHE_ENABLED = True
    print("✅ Smart Cache enabled")
except ImportError:
    SMART_CACHE_ENABLED = False
    print("⚠️ Smart Cache not available")

try:
    from api_key_rotator import get_api_key, rotate_key, mark_key_failed
    API_ROTATION_ENABLED = True
    print("✅ API Key Rotation enabled")
except ImportError:
    API_ROTATION_ENABLED = False
    print("⚠️ API Key Rotation not available")

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_PATH = os.path.join(BASE_DIR, "db", "faiss_index")

# --- FAST PIPELINE CONFIG ---
LLM_MODEL = "gemini-2.0-flash"  # Updated to available model
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "ms-marco-MiniLM-L-12-v2"
MAX_CONTEXT_CHARS = 1200 # Hard cap for velocity

# Global Cache (Simple in-memory)
CACHE = {}
CACHE_KEYWORDS = {}  # Keyword mapping for smart matching

# Load FAQ cache on startup
def load_faq_cache():
    try:
        faq_path = os.path.join(BASE_DIR, "faq_cache.json")
        if os.path.exists(faq_path):
            with open(faq_path, 'r', encoding='utf-8') as f:
                faq_data = json.load(f)
                CACHE.update(faq_data)
                # Build keyword index for smart matching
                build_keyword_index(faq_data)
                print(f"✅ Loaded {len(faq_data)} FAQ entries into cache")
    except Exception as e:
        print(f"⚠️ Could not load FAQ cache: {e}")

def build_keyword_index(faq_data):
    """Build keyword index for fuzzy cache matching"""
    for question, answer in faq_data.items():
        # Extract keywords from question
        keywords = extract_keywords(question.lower())
        for keyword in keywords:
            if keyword not in CACHE_KEYWORDS:
                CACHE_KEYWORDS[keyword] = []
            CACHE_KEYWORDS[keyword].append((question, answer))

def extract_keywords(text):
    """Extract important keywords from text"""
    # Remove common words
    stop_words = {'kya', 'hai', 'kaise', 'karein', 'ka', 'ki', 'ke', 'se', 'mein', 'me', 
                  'is', 'the', 'a', 'an', 'how', 'what', 'where', 'when', 'who', '?'}
    words = text.replace('?', '').split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords

def smart_cache_lookup(query):
    """Smart cache lookup with fuzzy matching"""
    # 1. Exact match
    if query in CACHE:
        return CACHE[query]
    
    # 2. Case-insensitive match
    for cached_q in CACHE.keys():
        if query.lower() == cached_q.lower():
            return CACHE[cached_q]
    
    # 3. Keyword-based fuzzy match
    query_keywords = set(extract_keywords(query.lower()))
    if not query_keywords:
        return None
    
    best_match = None
    best_score = 0
    
    for keyword in query_keywords:
        if keyword in CACHE_KEYWORDS:
            for cached_q, cached_a in CACHE_KEYWORDS[keyword]:
                cached_keywords = set(extract_keywords(cached_q.lower()))
                # Calculate overlap score
                overlap = len(query_keywords & cached_keywords)
                score = overlap / max(len(query_keywords), len(cached_keywords))
                
                if score > best_score and score > 0.5:  # 50% match threshold
                    best_score = score
                    best_match = cached_a
    
    return best_match

def clear_cache_if_full():
    if len(CACHE) > 5000:  # Increased from 1000 to 5000
        # Keep FAQ entries, clear only dynamic ones
        faq_path = os.path.join(BASE_DIR, "faq_cache.json")
        try:
            with open(faq_path, 'r', encoding='utf-8') as f:
                faq_keys = set(json.load(f).keys())
            # Remove non-FAQ entries
            keys_to_remove = [k for k in CACHE.keys() if k not in faq_keys]
            for key in keys_to_remove:
                del CACHE[key]
            print(f"🧹 Cache cleared (kept {len(faq_keys)} FAQ entries)")
        except:
            CACHE.clear()
            print("🧹 Cache cleared (LRU safety)")

# Global LLM (Preloaded)
# Use API key rotation if enabled
if API_ROTATION_ENABLED:
    api_key = get_api_key()
    print(f"🔑 Using API key rotation")
else:
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"🔑 Using default API key")

LLM = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    temperature=0.1,
    google_api_key=api_key,
    convert_system_message_to_human=True
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
    # Load FAQ cache after FAISS is ready
    load_faq_cache()
else:
    print("⚠️ FAISS Index not found. Please run ingest.py.")
    VECTORSTORE = None

# Startup Warmup
def warmup():
    print("🔥 Warming up pipeline...")
    try:
        if VECTORSTORE:
            VECTORSTORE.similarity_search("warmup", k=1)
        # LLM.invoke("Hi")  # DISABLED to save API quota
        print("✅ Pipeline Warmed Up (LLM warmup skipped)")
    except Exception as e:
        print(f"⚠️ Warmup failed: {e}")

# Run warmup on import (LLM warmup disabled to save quota)
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
    # 0. Smart Cache Check (NEW - Enhanced caching)
    if SMART_CACHE_ENABLED:
        cached_answer = get_cached_response(query)
        if cached_answer:
            print("✅ Smart Cache HIT!")
            return cached_answer
    
    # 0.1. Fallback to old cache (with fuzzy matching)
    cached_answer = smart_cache_lookup(query)
    if cached_answer:
        # Also save to smart cache for future
        if SMART_CACHE_ENABLED:
            cache_response(query, cached_answer)
        return cached_answer

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
        
        # Cache result (both old and new cache)
        clear_cache_if_full()
        CACHE[query] = content
        
        # Also save to smart cache
        if SMART_CACHE_ENABLED:
            cache_response(query, content)
            print("💾 Saved to Smart Cache")
        
        return content

    except Exception as e:
        error_msg = str(e)
        print(f"Pipeline Error: {e}")
        
        # Check if quota exceeded
        if "429" in error_msg or "quota" in error_msg.lower():
            # Emergency mode: Try to rotate to next key
            if API_ROTATION_ENABLED:
                try:
                    rotate_key()
                    print("🔄 Rotated to next API key due to quota")
                except:
                    pass
            
            return """⚠️ API quota temporarily exceeded. 

Please try:
1. Asking from FAQ topics (Hospital, Hostel, Leave, Fees, etc.)
2. Waiting a few minutes and trying again
3. Contacting admin for urgent queries

Available FAQ topics:
- Hospital timings and doctors
- Hostel rules and mess timings  
- Leave application process
- Fee payment and scholarships
- Library and facilities
- Exam rules and attendance policy"""
        
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