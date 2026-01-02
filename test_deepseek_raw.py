import os
import requests
import json
from dotenv import load_dotenv

# Force load .env
load_dotenv()

key = os.getenv("RAPIDAPI_KEY")
host = os.getenv("RAPIDAPI_HOST")

print(f"Key: {key[:5]}...")
print(f"Host: {host}")

url = f"https://{host}/v1/chat/completions"

payload = {
	"model": "deepseek-v3",
	"messages": [
		{"role": "user", "content": "Hello, testing connection!"}
	],
    "temperature": 0.7
}

headers = {
	"x-rapidapi-key": key,
	"x-rapidapi-host": host,
	"Content-Type": "application/json"
}

print(f"POST {url}")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
