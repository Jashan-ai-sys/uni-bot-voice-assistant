import requests
import json
import sys

# Force utf-8
sys.stdout.reconfigure(encoding='utf-8')

def test_endpoint():
    url = "http://localhost:8000/ask_stream"
    print(f"Connecting to {url}...")
    
    try:
        with requests.post(url, json={"question": "hello"}, stream=True, timeout=10) as r:
            print(f"Status Code: {r.status_code}")
            print("--- Stream Content ---")
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"RECEIVED: {decoded_line}")
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_endpoint()
