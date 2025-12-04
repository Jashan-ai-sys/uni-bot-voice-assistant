import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

DB_PATH = "./db"

def get_vectorstore():
    """
    Loads the persisted Chroma vector store.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Vector DB not found at {DB_PATH}. Please run ingest.py first.")
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    return vectorstore

def answer_question(query: str, student_id: str = None) -> str:
    """
    Answers a question using RAG based on the ingested documents.
    Now also checks personal timetable if student_id is provided.
    """
    try:
        # Check if query is about timetable
        timetable_keywords = ["class", "timetable", "schedule", "teacher", "room", "lecture", "when is", "what time"]
        is_timetable_query = any(keyword in query.lower() for keyword in timetable_keywords)
        
        # If student ID provided and query is about timetable, check personal data first
        if student_id and is_timetable_query:
            from user_storage import get_timetable_data
            from timetable_extractor import search_timetable
            
            timetable_data = get_timetable_data(student_id)
            if timetable_data:
                personal_answer = search_timetable(timetable_data, query)
                if personal_answer and "No matching" not in personal_answer:
                    return personal_answer
        
        vectorstore = get_vectorstore()
        
        # Use MMR (Maximum Marginal Relevance) for diverse, relevant results
        # Increased k to 15 to ensure we capture relevant docs even if they rank lower
        docs = vectorstore.max_marginal_relevance_search(
            query, 
            k=15,             # Return 15 documents (Gemini has large context, so this is fine)
            fetch_k=50,       # Consider 50 candidates
            lambda_mult=0.7   # Balance between relevance (1.0) and diversity (0.0)
        )
        
        # Create context with source information
        context_parts = []
        for doc in docs:
            source = doc.metadata.get('source', 'unknown')
            # Extract just the filename from the path
            filename = source.split('\\')[-1] if '\\' in source else source.split('/')[-1]
            context_parts.append(f"[Document: {filename}]\n{doc.page_content}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Configure GenAI
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        system_prompt = (
            "You are a helpful university assistant. "
            "Use the retrieved context to answer the question. "
            "If you don't know, say you don't know.\n\n"
            "FORMATTING RULES:\n"
            "- Use bullet points for lists\n"
            "- Use emojis to make the answer engaging (e.g., 🎓, 📚, 📝)\n"
            "- Keep the answer concise but structured\n"
            "- Use bold text for key terms\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}"
        )
        
        # Retry logic for rate limits
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(system_prompt)
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Resource exhausted" in error_str:
                    if attempt < max_retries - 1:
                        import time
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "I'm getting too many requests right now. Please wait a moment and try again. (Gemini API rate limit)"
                else:
                    raise e
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"I'm having trouble processing that right now. Please try again in a moment."

if __name__ == "__main__":
    # Test the pipeline locally
    print("🤖 RAG Pipeline Test")
    q = input("Ask a question: ")
    if q:
        ans = answer_question(q)
        print(f"\nAnswer: {ans}")
