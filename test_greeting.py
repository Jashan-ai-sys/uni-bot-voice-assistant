import requests
import json

url = "http://localhost:8000/ask_stream"
payload = {"question": "hi"}

try:
    with requests.post(url, json=payload, stream=True) as r:
        print(f"Status: {r.status_code}")
        full_text = ""
        for chunk in r.iter_content(chunk_size=None):
            if chunk:
                # SSE lines start with "data: "
                # We want to extract the chunk content
                chunk_str = chunk.decode('utf-8')
                print(f"RAW CHUNK: {chunk_str}")
except Exception as e:
    print(f"Error: {e}")
