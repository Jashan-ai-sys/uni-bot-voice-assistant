import os
from dotenv import load_dotenv

# Force reload from file to be sure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path, override=True)

keys = [
    "GOOGLE_API_KEY",
    "OPENROUTER_API_KEY",
    "DEEPGRAM_API_KEY",
    "OLLAMA_BASE_URL"
]

print(f"📂 Loading .env from: {env_path}")
print("-" * 40)
for key in keys:
    value = os.getenv(key)
    if value:
        masked = value[:4] + "*" * 4 + value[-4:] if len(value) > 8 else "****"
        print(f"✅ {key}: {masked}")
    else:
        print(f"❌ {key}: Not Set")
print("-" * 40)
