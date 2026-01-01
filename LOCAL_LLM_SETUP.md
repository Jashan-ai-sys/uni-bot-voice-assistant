# Local LLM Setup Guide

## Option 1: Use Ollama (Recommended for Windows)

### Installation:
1. Download Ollama from: https://ollama.com/download
2. Install it on your system
3. Open terminal and run:
   ```
   ollama pull llama3.2:3b
   ```

### Update your code:
In `src/rag_pipeline.py`, replace the LLM initialization:

```python
# OLD (Google Gemini - API calls)
from langchain_google_genai import ChatGoogleGenerativeAI
LLM = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# NEW (Ollama - Local, Free)
from langchain_community.llms import Ollama
LLM = Ollama(
    model="llama3.2:3b",
    temperature=0.1
)
```

### Benefits:
- ✅ Completely FREE
- ✅ No quota limits
- ✅ Works offline
- ✅ Fast responses
- ✅ Privacy (data stays local)

### Recommended Models:
- `llama3.2:3b` - Fast, good quality (2GB)
- `phi3:mini` - Very fast, smaller (2GB)
- `mistral:7b` - Better quality (4GB)

---

## Option 2: Use GPT4All (Alternative)

### Installation:
```bash
pip install gpt4all
```

### Code:
```python
from langchain_community.llms import GPT4All

LLM = GPT4All(
    model="mistral-7b-openorca.Q4_0.gguf",
    max_tokens=512
)
```

---

## Comparison:

| Solution | Cost | Speed | Quality | Quota |
|----------|------|-------|---------|-------|
| Google Gemini | Paid | Fast | Excellent | Limited |
| Ollama (Local) | Free | Medium | Good | Unlimited |
| GPT4All | Free | Medium | Good | Unlimited |

---

## Hybrid Approach (Best of Both Worlds):

Use local LLM for simple queries, Google Gemini for complex ones:

```python
def get_llm(query_complexity="simple"):
    if query_complexity == "simple":
        return Ollama(model="llama3.2:3b")
    else:
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash")
```
