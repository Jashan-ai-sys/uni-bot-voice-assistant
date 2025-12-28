import os
from dotenv import load_dotenv

# Load env from root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- PATHS ---
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "faiss_index")
CACHE_DIR = os.path.join(BASE_DIR, "models")

# --- MODELS ---
# Local Embedding (CPU)
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Reranker
RERANK_MODEL_NAME = "ms-marco-MiniLM-L-12-v2"

# LLMs
LOCAL_LLM_MODEL = "llama3.1:8b"  # Q4 quantized, optimized for T4 GPU
CLOUD_LLM_MODEL = "llama-3.1-8b-instant" # Groq

# --- API KEYS ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "uni-bot-index")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- EMBEDDING PROVIDER ---

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "huggingface")  # or "gemini"


# --- SETTINGS ---
MAX_CONTEXT_CHARS = 1200
RETRIEVAL_K = 3
RERANK_THRESHOLD = 0.25
