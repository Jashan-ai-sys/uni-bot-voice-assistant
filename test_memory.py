import requests
import json
import time

url = "http://localhost:8000/ask_stream"
session_id = "test_sess_003" # New session

def ask(question):
    print(f"\nUser: {question}")
    payload = {"question": question, "session_id": session_id}
    
    # We will just verify that we get *something* back containing the expected keywords
    start_time = time.time()
    response_text = ""
    
    try:
        with requests.post(url, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if "data: " in decoded:
                         try:
                             json_part = decoded.replace("data: ", "")
                             data = json.loads(json_part)
                             if "chunk" in data:
                                 chunk = data["chunk"]
                                 response_text += chunk
                                 print(chunk, end="", flush=True)
                         except:
                             pass
    except Exception as e:
        print(f"Error: {e}")
        
    print(f"\n[Done in {time.time() - start_time:.2f}s]")
    return response_text

# Turn 1
print("--- TURN 1 ---")
ans1 = ask("Who is Rashmi Mittal?")

# Turn 2
print("\n--- TURN 2 ---")
ans2 = ask("When can I meet her?")

# Verification
if "Rashmi" in ans2 or "Mrs." in ans2 or "Pro Chancellor" in ans2 or "Block 29" in ans2:
    print("\n✅ MEMORY TEST PASSED: Bot understood 'her'.")
else:
    print("\n❌ MEMORY TEST FAILED: Bot did not reference context.")
