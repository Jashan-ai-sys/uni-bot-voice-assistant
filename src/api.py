import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

# Ensure src is in path logic (if running from root)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_pipeline import answer_question_stream

app = FastAPI(title="LPU Bot Backend (MCP Architecture)")

# CORS (Allow Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    student_id: str = None

@app.get("/")
def health_check():
    return {
        "status": "active",
        "architecture": "Hybrid MCP RAG",
        "router_mode": "Cloud" if os.getenv("GROQ_API_KEY") else "Local"
    }

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    return StreamingResponse(
        answer_question_stream(req.query, req.student_id), 
        media_type="text/plain"
    )

# Entry point for `python src/api.py`
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
