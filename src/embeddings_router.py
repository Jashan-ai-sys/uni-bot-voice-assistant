import os
from dotenv import load_dotenv

load_dotenv()

def get_embeddings(provider="huggingface"):
    """
    Returns embeddings model based on provider.
    
    Args:
        provider: "huggingface" (BGE) or "gemini"
    
    Returns:
        Embeddings instance
    """
    if provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        return GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=api_key
        )
    else:
        # Default: HuggingFace BGE
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from src.config import EMBED_MODEL_NAME
        
        return HuggingFaceEmbeddings(
            model_name=EMBED_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )


def compare_embeddings(query: str, provider1="huggingface", provider2="gemini"):
    """
    Compare embedding quality between two providers.
    
    Args:
        query: Test query
        provider1: First provider
        provider2: Second provider
    
    Returns:
        Dict with embedding vectors and metadata
    """
    emb1 = get_embeddings(provider1)
    emb2 = get_embeddings(provider2)
    
    vec1 = emb1.embed_query(query)
    vec2 = emb2.embed_query(query)
    
    return {
        provider1: {
            "dimensions": len(vec1),
            "vector": vec1[:5],  # First 5 dims for display
            "model": emb1
        },
        provider2: {
            "dimensions": len(vec2),
            "vector": vec2[:5],
            "model": emb2
        }
    }
