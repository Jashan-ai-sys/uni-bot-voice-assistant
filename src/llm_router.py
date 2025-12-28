import sys
from langchain_ollama import ChatOllama
from src.config import LOCAL_LLM_MODEL, CLOUD_LLM_MODEL, GROQ_API_KEY

# Singleton LLM instance
_LLM_INSTANCE = None

def get_llm():
    """
    Returns the appropriate LLM instance based on configuration (Router).
    """
    global _LLM_INSTANCE
    
    if _LLM_INSTANCE is not None:
        return _LLM_INSTANCE

    # Routing Logic
    if GROQ_API_KEY:
        try:
            from langchain_groq import ChatGroq
            print(f"☁️ Router: Switching to Cloud (Groq: {CLOUD_LLM_MODEL})", file=sys.stderr)
            _LLM_INSTANCE = ChatGroq(
                model=CLOUD_LLM_MODEL,
                temperature=0.1,
                api_key=GROQ_API_KEY
            )
            return _LLM_INSTANCE
        except ImportError:
            print("⚠️ Router: langchain-groq not found. Falling back to Local.", file=sys.stderr)
    
    # Fallback / Default to Local
    print(f"💻 Router: Using Local (Ollama: {LOCAL_LLM_MODEL})", file=sys.stderr)
    _LLM_INSTANCE = ChatOllama(
        model=LOCAL_LLM_MODEL,
        temperature=0.1,
        top_p=0.9,
        num_ctx=1024,
        keep_alive="1h"
    )
    
    return _LLM_INSTANCE
