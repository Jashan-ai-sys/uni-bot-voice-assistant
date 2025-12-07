import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_PATH = os.path.join(BASE_DIR, "db")

def get_vectorstore():
    """
    Loads the persisted Chroma vector store.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Vector DB not found at {DB_PATH}. Please run ingest.py first.")
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    return vectorstore

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
    Answers a question using RAG based on the ingested documents.
    Features: Metadata filtering, intent detection, and enhanced citations.
    """
    # Check for timetable queries first
    timetable_keywords = ["class", "schedule", "timetable", "subject", "room", "lecture", "practical", "tutorial", "when", "where", "time", "monday", "tuesday", "wednesday", "thursday", "friday", "teacher", "what time", "when is"]
    is_timetable_query = any(keyword in query.lower() for keyword in timetable_keywords)

    if student_id:
        try:
            import user_storage
            import timetable_extractor
            
            if is_timetable_query:
                print(f"📅 Checking timetable for student_id: {student_id}")
                timetable_data = user_storage.get_user_timetable(student_id)
                if timetable_data and timetable_data.get("schedule"):
                    print(f"📅 Calling timetable extractor for query: {query}")
                    result = timetable_extractor.search_timetable(timetable_data, query)
                    print(f"📅 Timetable extractor result length: {len(result)}")
                    return result
        except Exception as e:
            print(f"Timetable check error: {e}")
    
    # General RAG pipeline
    try:
        vectorstore = get_vectorstore()
        
        # Determine filters
        search_filter = identify_intent(query)
        
        # Search strategy
        k_val = 8 if search_filter else 10 # More specific if filtered
        
        # Use MMR for diversity
        docs = vectorstore.max_marginal_relevance_search(
            query, 
            k=k_val,
            filter=search_filter,
            fetch_k=20,
            lambda_mult=0.6 # slightly more diversity
        )
        
        # Construct context with citations
        context_parts = []
        total_chars = 0
        MAX_CTX_CHARS = 10000  # Cap context size
        
        for doc in docs:
            source = doc.metadata.get('source', 'unknown')
            page = doc.metadata.get('page', '')
            citation = f"{source}"
            if page: citation += f" (p. {page})"
            
            content = f"[Source: {citation}]\n{doc.page_content}"
            
            if total_chars + len(content) > MAX_CTX_CHARS:
                break
                
            context_parts.append(content)
            total_chars += len(content)
        
        context = "\n\n---\n\n".join(context_parts)
        
        if not context:
            return "I couldn't find any specific documents matching your query. Please try rephrasing."

        # Configure GenAI
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        system_prompt = (
            "You are JARVIS, a smart university assistant.\n"
            "Use the provided context to answer the user's question accurately.\n\n"
            "STRICT GUIDELINES:\n"
            "1. **No Hallucinations**: If the answer is not in the context, say 'I don't have that information in my documents'. Do not make up facts.\n"
            "2. **Citations**: When stating specific rules, fees, or locations, mention the source filename in brackets, e.g., [exam_rules.pdf].\n"
            "3. **Tone**: Be professional but friendly.\n"
            "4. **Formatting**: Use clear headers, bullet points, and emojis for readability.\n\n"
            "Refrain from inventing numbers, dates, or contact details.\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}"
        )
        
        # Retry logic for rate limits
        max_retries = 10
        retry_delay = 4
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(system_prompt)
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Resource exhausted" in error_str:
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
                    else:
                        return "I'm experiencing heavy traffic. Please ask again in a moment."
                raise e
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return "I encountered an issue searching my database. Please try again."

async def answer_question_stream(query: str, student_id: str = None):
    """
    Streaming version of answer_question for real-time response generation.
    Yields chunks of text as they're generated.
    """
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
                    # Stream the result in chunks
                    words = result.split()
                    for i in range(0, len(words), 3):  # Stream 3 words at a time
                        yield " ".join(words[i:i+3]) + " "
                    return
        except Exception as e:
            print(f"Timetable check error: {e}")
    
    # General RAG pipeline with streaming
    try:
        vectorstore = get_vectorstore()
        
        # Determine filters
        search_filter = identify_intent(query)
        
        # Search strategy
        k_val = 8 if search_filter else 10
        
        # Use MMR for diversity
        docs = vectorstore.max_marginal_relevance_search(
            query, 
            k=k_val,
            filter=search_filter,
            fetch_k=20,
            lambda_mult=0.6
        )
        
        # Construct context
        context_parts = []
        total_chars = 0
        MAX_CTX_CHARS = 10000
        
        for doc in docs:
            source = doc.metadata.get('source', 'unknown')
            page = doc.metadata.get('page', '')
            citation = f"{source}"
            if page: citation += f" (p. {page})"
            
            content = f"[Source: {citation}]\n{doc.page_content}"
            
            if total_chars + len(content) > MAX_CTX_CHARS:
                break
                
            context_parts.append(content)
            total_chars += len(content)
        
        context = "\n\n---\n\n".join(context_parts)
        
        if not context:
            yield "I couldn't find any specific documents matching your query. Please try rephrasing."
            return

        # Configure GenAI for streaming
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        system_prompt = (
            "You are JARVIS, a smart university assistant.\n"
            "Use the provided context to answer the user's question accurately.\n\n"
            "STRICT GUIDELINES:\n"
            "1. **No Hallucinations**: If the answer is not in the context, say 'I don't have that information in my documents'. Do not make up facts.\n"
            "2. **Citations**: When stating specific rules, fees, or locations, mention the source filename in brackets, e.g., [exam_rules.pdf].\n"
            "3. **Tone**: Be professional but friendly.\n"
            "4. **Formatting**: Use clear headers, bullet points, and emojis for readability.\n\n"
            "Refrain from inventing numbers, dates, or contact details.\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}"
        )
        
        # Retry logic for rate limits
        max_retries = 10
        retry_delay = 4
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(system_prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Resource exhausted" in error_str:
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
                    else:
                        yield "I'm experiencing heavy traffic. Please ask again in a moment."
                        return
                else:
                    raise e
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield f"I encountered an issue searching my database: {str(e)}"

if __name__ == "__main__":
    # Test the pipeline locally
    print("🤖 Optimized RAG Pipeline Test")
    print("Type 'exit' to quit.")
    while True:
        q = input("\nAsk a question: ")
        if q.lower() == 'exit': break
        ans = answer_question(q)
        print(f"\nAnswer: {ans}")
