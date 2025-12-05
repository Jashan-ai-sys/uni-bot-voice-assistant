import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

try:
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    if response.status_code == 200:
        models = response.json()["data"]
        with open("tests/pro_models_list.txt", "w") as f:
            for model in models:
                mid = model["id"].lower()
                if "gemini" in mid and "pro" in mid:
                    f.write(f"{model['id']}\n")
                    print(f"- {model['id']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
