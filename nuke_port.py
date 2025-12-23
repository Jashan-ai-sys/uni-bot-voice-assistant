import os
import subprocess
import time
import sys

def get_pid_on_port(port):
    try:
        # Run netstat to find the PID listening on the port
        result = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True)
        if not result.stdout:
            return None
        
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if "LISTENING" in line:
                parts = line.split()
                return parts[-1] # PID is the last element
    except Exception as e:
        print(f"Error checking port {port}: {e}")
    return None

def kill_pid(pid):
    print(f"🔫 Killing process PID {pid} on port 8000 (Tree)...")
    subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, check=False)

def kill_all_python():
    print("🔫 Killing ALL python.exe processes (Tree)...")
    subprocess.run("taskkill /F /T /IM python.exe", shell=True, check=False)
    subprocess.run("taskkill /F /T /IM uvicorn.exe", shell=True, check=False)
    # Also kill cmd.exe to close the batch file windows
    print("🔫 Killing ALL cmd.exe processes to close old terminals...")
    subprocess.run("taskkill /F /T /IM cmd.exe", shell=True, check=False)

def main():
    port = 8000
    print(f"--- Nuke Port {port} ---")
    
    # 1. Kill specific port owner
    pid = get_pid_on_port(port)
    if pid:
        kill_pid(pid)
    else:
        print(f"Port {port} seems free (no LISTENING process).")

    # 2. Blanket kill just to be safe (zombies)
    kill_all_python()
    
    # 3. Verify
    time.sleep(2)
    pid = get_pid_on_port(port)
    if pid:
        print(f"❌ FAILED: Port {port} is still held by PID {pid}")
        sys.exit(1)
    else:
        print(f"✅ SUCCESS: Port {port} is completely free.")
        sys.exit(0)

if __name__ == "__main__":
    main()
