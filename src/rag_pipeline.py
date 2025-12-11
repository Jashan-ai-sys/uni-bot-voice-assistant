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
            citation = f"{source}"
            content = f"Source: {citation}\nContent: {doc.page_content}"
           
            if total_chars + len(content) > MAX_CTX_CHARS:
                break
               
            context_parts.append(content)
            total_chars += len(content)
       
        context = "\n\n---\n\n".join(context_parts)
       
        if not context:
            return "I couldn't find any specific documents matching your query. Please try rephrasing."

        # LangChain Generation
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
       
        llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
       
        template = """
You are JARVIS — a precise, reliable university assistant.
You answer ONLY using the information present in the provided context.

====================================================
🔒 RULES (STRICT — DO NOT VIOLATE)
====================================================
1. ❗ NO HALLUCINATIONS  
   - If the answer is NOT found in context, reply exactly:  
     "I don't have that information in my documents."

2. ❗ NO SOURCE OR FILE NAMES  
   - Never reveal document names, PDF names, metadata, or citation text.

3. ❗ STAY WITHIN CONTEXT  
   - Do NOT invent numbers, dates, fees, rules, policies, or map details.

4. ❗ STRUCTURE EVERYTHING  
   - ALWAYS use a clean, organized format:
        - Bullet points
        - Step-by-step lists
        - Headings
        - Tables (if needed)

5. ❗ TONE  
   - Friendly, clear, professional.
   - No emojis *unless the user uses them first*.

====================================================
📌 HOW TO ANSWER
====================================================
ALWAYS follow this format:

**Answer:**
<your clear answer here>

**If helpful, also include:**
- Key points
- Steps or instructions
- Short summary

====================================================
📚 CONTEXT
(Use ONLY the following information to answer)
====================================================
{context}

====================================================
❓ USER QUESTION
====================================================
{query}
"""
        prompt = ChatPromptTemplate.from_template(template)
        # We can just invoke the chain
        chain = prompt | llm | StrOutputParser()
       
        # Simple invoke without extra retry logic wrapper for sync (LangChain has some built-in defaults)
        try:
            return chain.invoke({"context": context, "query": query})
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Resource exhausted" in error_str:
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
            citation = f"{source}"
            content = f"Source: {citation}\nContent: {doc.page_content}"
           
            if total_chars + len(content) > MAX_CTX_CHARS:
                break
               
            context_parts.append(content)
            total_chars += len(content)
       
        context = "\n\n---\n\n".join(context_parts)
       
        if not context:
            yield "I couldn't find any specific documents matching your query. Please try rephrasing."
            return

        # Retry logic for rate limits
        max_retries = 10
        retry_delay = 4
       
        import asyncio
        import queue
        from concurrent.futures import ThreadPoolExecutor
        import os

        # LangChain Generation with RAW SDK Wrapper (bypass ChatGoogleGenerativeAI)
        # We need this because LangChain's parser fails on Gemini 2.5 experimental fields
        # and sync calls block the server.
        
        system_prompt = (
            "You are JARVIS — a precise, reliable university assistant.\n"
            "You answer questions using the provided context.\n\n"
            "STRICT RULES:\n"
            "1. NO HALLUCINATIONS. If not in context AND the user is asking for specific info, say 'I don't have that information'.\n"
            "2. GREETINGS: If the user says 'hi', 'hello', or introduces themselves, reply politely and ask how you can help (you do NOT need context for this).\n"
            "3. NO SOURCE FILENAMES in output.\n"
            "4. Structure with bullet points.\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}"
        )

        for attempt in range(max_retries):
            try:
                # Queue for communicating chunks from thread to async loop
                chunk_queue = asyncio.Queue()
                loop = asyncio.get_running_loop()
                
                # Worker function to run in separate thread
                def producer_thread():
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        
                        print(f"DEBUG: Thread started for {model.model_name}")
                        
                        # Blocking call
                        response = model.generate_content(system_prompt, stream=True)
                        
                        # Blocking iteration
                        for chunk in response:
                            if chunk.text:
                                # Schedule putting data into queue (thread-safe for loop)
                                loop.call_soon_threadsafe(chunk_queue.put_nowait, chunk.text)
                        
                        # Signal done
                        loop.call_soon_threadsafe(chunk_queue.put_nowait, None)
                        
                    except Exception as e:
                        print(f"Thread Error: {e}")
                        error_str = str(e)
                        if "429" in error_str or "Resource exhausted" in error_str:
                             loop.call_soon_threadsafe(chunk_queue.put_nowait, "⚠️ **High Traffic**: I am currently rate-limited by Google (429). Please wait 1 minute and try again.")
                        else:
                             loop.call_soon_threadsafe(chunk_queue.put_nowait, f"⚠️ Error: {str(e)}")
                        
                        # Signal done after sending error
                        loop.call_soon_threadsafe(chunk_queue.put_nowait, None)

                # Start the producer thread
                executor = ThreadPoolExecutor(max_workers=1)
                loop.run_in_executor(executor, producer_thread)

                print(f"Generating content with model: gemini-2.5-flash (Threaded)")
                
                # Consume the queue
                while True:
                    # Wait for data (non-blocking)
                    chunk_text = await chunk_queue.get()
                    
                    if chunk_text is None:
                        print("DEBUG: Queue received None (Done signal)")
                        break
                        
                    print(f"DEBUG: Queue received text: '{chunk_text}'")
                    yield chunk_text

                print("DEBUG: Stream finished (Generator exit).")
                executor.shutdown(wait=False)
                return

            except Exception as e:
                print(f"Stream error: {e}")
                error_str = str(e)
                if "429" in error_str or "Resource exhausted" in error_str:
                    print("DEBUG: Hit Rate Limit (429). notifying user.")
                    yield "⚠️ **High Traffic**: I am currently rate-limited by Google. Please wait 1 minute and try again."
                    return
                else:
                    print(f"DEBUG: Unknown error: {e}")
                    yield f"⚠️ Error: {str(e)}"
                    return
            except Exception as e:
                print(f"Stream error: {e}")
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

# Alias for web_app compatibility
# answer_question_stream = answer_question

if __name__ == "__main__":
    # Test the pipeline locally
    print("🤖 Optimized RAG Pipeline Test")
    print("Type 'exit' to quit.")
    while True:
        q = input("\nAsk a question: ")
        if q.lower() == 'exit': break
        ans = answer_question(q)
        print(f"\nAnswer: {ans}")