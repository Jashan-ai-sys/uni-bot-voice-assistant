import sys
import os

try:
    import langchain
    print(f"Langchain version: {langchain.__version__}")
    print(f"Langchain file: {langchain.__file__}")
    
    import langchain.chains
    print("langchain.chains imported successfully")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")

print("Sys path:")
for p in sys.path:
    print(p)
