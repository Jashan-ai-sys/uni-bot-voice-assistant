import requests
import json
import time

url = "http://localhost:8000/ask_stream"
payload = {
    "question": "where can i meet her", 
    "student_id": "12345", # Forces timetable path check
    "session_id": "debug_intent"
}

print(f"Sending: {payload['question']} with student_id...")

try:
    with requests.post(url, json=payload, stream=True) as r:
        for line in r.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if "data: " in decoded:
                        print(decoded)
except Exception as e:
    print(f"Error: {e}")
