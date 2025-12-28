import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print(f"Testing Health Check...")
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        sys.exit(1)

def test_search():
    print(f"\nTesting search_documents...")
    payload = {"query": "hostel fees"}
    try:
        resp = requests.post(f"{BASE_URL}/search_documents", json=payload)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        result = data.get("result", "")
        print(f"Result Length: {len(result)}")
        print(f"Snippet: {result[:100]}...")
    except Exception as e:
        print(f"Search Failed: {e}")

def test_db():
    print(f"\nTesting query_database (Profile)...")
    # Assuming user 12345678 doesn't exist but we want to see the tool handle it, 
    # OR we can create a dummy user first? 
    # The current user_storage relies on files.
    # Let's try a generic ID.
    payload = {
        "query_type": "profile",
        "params": {"student_id": "12345678"}
    }
    try:
        resp = requests.post(f"{BASE_URL}/query_database", json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"DB Query Failed: {e}")

if __name__ == "__main__":
    # Wait for server to definitely be up
    time.sleep(3)
    test_health()
    test_search()
    test_db()
