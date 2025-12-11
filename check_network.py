import socket
import sys
import requests

# Force utf-8
sys.stdout.reconfigure(encoding='utf-8')

def check_connectivity():
    print("--- Network Connectivity Test ---")
    
    # 1. Check DNS resolution
    try:
        host = "generativelanguage.googleapis.com"
        print(f"Resolving {host}...")
        ip = socket.gethostbyname(host)
        print(f"Resolved to {ip}")
    except Exception as e:
        print(f"DNS Resolution Failed: {e}")
        return

    # 2. Check HTTP Reachability
    try:
        url = f"https://{host}"
        print(f"Pinging {url}...")
        resp = requests.get(url, timeout=5)
        print(f"Response: {resp.status_code}")
    except Exception as e:
        print(f"HTTP Request Failed: {e}")

if __name__ == "__main__":
    check_connectivity()
