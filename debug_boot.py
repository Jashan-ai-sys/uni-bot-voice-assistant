
import sys
import os
import traceback

print("🔍 DEBUG: Starting boot diagnosis...", file=sys.stderr)
print(f"🔍 DEBUG: CWD: {os.getcwd()}", file=sys.stderr)
print(f"🔍 DEBUG: Content of src/: {os.listdir('src') if os.path.exists('src') else 'NOT FOUND'}", file=sys.stderr)
print(f"🔍 DEBUG: SYS.PATH: {sys.path}", file=sys.stderr)

try:
    print("🔍 DEBUG: Attempting 'import src.web_app'...", file=sys.stderr)
    import src.web_app
    print("✅ DEBUG: Import successful!", file=sys.stderr)
except Exception:
    print("❌ DEBUG: Import FAILED!", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

print("🔍 DEBUG: Attempting to run uvicorn...", file=sys.stderr)
import uvicorn
uvicorn.run("src.web_app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
