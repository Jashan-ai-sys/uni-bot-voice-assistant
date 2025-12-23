import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama  # Local Ollama for embeddings and LLM

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_PATH = os.path.join(BASE_DIR, "db")

TIMETABLE_KEYWORDS = [
    "class", "schedule", "timetable", "lecture", "practical", "tutorial", 
    "monday", "tuesday", "wednesday", "thursday", "friday", 
    "what time", "when is"
]

# Pre-load LLM globally for faster responses (no per-request initialization)

LLM = ChatOllama(
    model="phi3.5",
    temperature=0.2,
    top_p=0.9,
    top_k=20,
    num_predict=120,      # limits response length
    num_ctx=2048,         # we only need 1200 chars of context
    repeat_penalty=1.05,
    repeat_last_n=20
)


def get_vectorstore():
    """
    Loads the persisted Chroma vector store.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Vector DB not found at {DB_PATH}. Please run ingest.py first.")
    
    # Use local embeddings - no API latency!
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
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
        "warden": "hostel", # Warden can be hostel context too
        # Hospital / Medical Context - Now separate!
        "hospital": "hospital",
        "medical": "hospital",
        "emergency": "hospital",
        "ambulance": "hospital",
        "doctor": "hospital",
        
        "bh1": "hostel", "bh2": "hostel", "bh3": "hostel", "bh4": "hostel",
        "bh5": "hostel", "bh6": "hostel", "bh7": "hostel", "bh8": "hostel",
        "gh1": "hostel", "gh2": "hostel", "gh3": "hostel", "gh4": "hostel"
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
    # Smalltalk / Greeting Bypass
    greetings = ["hi", "hello", "hey", "yo", "sup", "hola", "greetings"]
    if query.lower().strip() in greetings:
        return "Hello! How can I help you today? 😊"

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
       
        # Fast similarity search (HNSW optimized)
        k_val = 5  # Increased from 3 to 5 for better recall
        docs = vectorstore.similarity_search(
            query=query,
            k=k_val,
            filter=search_filter
        )
       
        # Construct context with citations - BALANCED (Speed + Quality)
        context_parts = []
        total_chars = 0
        MAX_CTX_CHARS = 1200  # Optimized for 2-3B models (reduced from 2000)
       
        for doc in docs:
            source = doc.metadata.get('source', 'unknown')
            # Smart truncation: limit each document to 800 chars for more detail
            page_content = doc.page_content[:800] + "..." if len(doc.page_content) > 800 else doc.page_content
            content = f"[{source}]\n{page_content}"
           
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
       
        # Use global pre-loaded LLM (no initialization overhead)
        template = """You are JARVIS, a university assistant.

You MUST answer ONLY using the information in the context.
Do NOT guess.
If the answer is not found, reply: "I don't have that information."

CONTEXT:
{context}

QUESTION:
{query}

ANSWER (short, factual, structured):
(Format UMS paths like: Step 1 → Step 2 → Step 3)"""
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | LLM | StrOutputParser()  # Use global LLM
       
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
    # Smalltalk / Greeting Bypass
    greetings = ["hi", "hello", "hey", "yo", "sup", "hola", "greetings"]
    if query.lower().strip() in greetings:
        yield "Hello! How can I help you today? 😊"
        return

    # Check for timetable queries first
    # Check for timetable queries first
    is_timetable_query = any(keyword in query.lower() for keyword in TIMETABLE_KEYWORDS)

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
       
        # Fast similarity search (HNSW optimized)
        k_val = 5  # Consistency with sync function
        docs = vectorstore.similarity_search(
            query=query,
            k=k_val,
            filter=search_filter
        )
       
        # Construct context with citations 
        context_parts = []
        total_chars = 0
        MAX_CTX_CHARS = 1200  # Optimized for 2-3B models
       
        for doc in docs:
            source = doc.metadata.get('source', 'unknown')
            page_content = doc.page_content[:350] # Consistent chunk limit
            content = f"[{source}]\n{page_content}"
           
            if total_chars + len(content) > MAX_CTX_CHARS:
                break
               
            context_parts.append(content)
            total_chars += len(content)
       
        context = "\n\n---\n\n".join(context_parts)
       
        if not context:
            yield "I couldn't find any specific documents matching your query. Please try rephrasing."
            return

        system_prompt = f"""You are JARVIS, a university assistant.

You MUST answer ONLY using the information in the context.
Do NOT guess.
If the answer is not found, reply: "I don't have that information."

CONTEXT:
{context}

QUESTION:
{query}

ANSWER (short, factual, structured):
(Format UMS paths like: Step 1 → Step 2 → Step 3)"""

        # Stream directly using global LLM
        try:
            for chunk in LLM.stream(system_prompt):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
        except Exception as e:
            print(f"Stream error: {e}")
            yield f"⚠️ Error generating response: {str(e)}"

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