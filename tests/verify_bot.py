import requests
import time
import sys

def verify_bot():
    base_url = "http://localhost:8000"
    print(f"Checking {base_url}...")
    
    # Wait for server to start
    for i in range(10):
        try:
            response = requests.get(base_url)
            if response.status_code == 200:
                print("✅ Home page is accessible.")
                break
        except requests.exceptions.ConnectionError:
            print(f"Waiting for server... ({i+1}/10)")
            time.sleep(2)
    else:
        print("❌ Server failed to start or is not accessible.")
        sys.exit(1)

    # Test /ask endpoint
    print("Testing /ask endpoint...")
    try:
        payload = {"question": "Hello, who are you?"}
        response = requests.post(f"{base_url}/ask", json=payload)
        if response.status_code == 200:
            data = response.json()
            if "answer" in data:
                print(f"✅ /ask endpoint working. Answer: {data['answer'][:50]}...")
            else:
                print(f"❌ /ask endpoint returned unexpected JSON: {data}")
        else:
            print(f"❌ /ask endpoint failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error testing /ask endpoint: {e}")

if __name__ == "__main__":
    verify_bot()
