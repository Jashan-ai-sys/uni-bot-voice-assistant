import os
import subprocess
import time

def kill_process_by_name(name):
    print(f"Assigning termination squads for: {name}")
    try:
        # Windows specific kill
        subprocess.run(f"taskkill /F /IM {name}", shell=True, check=False)
        # Verify
        time.sleep(1)
        res = subprocess.run(f"tasklist | findstr {name}", shell=True, capture_output=True)
        if res.stdout:
            print(f"WARNING: {name} still running! Retrying...")
            subprocess.run(f"taskkill /F /IM {name}", shell=True, check=False)
        else:
            print(f"CONFIRMED: {name} is dead.")
    except Exception as e:
        print(f"Error killing {name}: {e}")

if __name__ == "__main__":
    print("--- STARTING ZOMBIE APOCALYPSE CLEANUP ---")
    kill_process_by_name("python.exe")
    kill_process_by_name("node.exe")
    # Also kill uvicorn if separate
    kill_process_by_name("uvicorn.exe") 
    print("--- CLEANUP COMPLETE ---")
