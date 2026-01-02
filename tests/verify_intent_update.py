import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rag_pipeline import identify_intent

def test():
    queries = [
        "give me the ums navigation",
        "what is the path to apply for leave",
        "ums steps",
        "placement policies"
    ]
    
    print("Testing Intent Identification:")
    for q in queries:
        intent = identify_intent(q)
        print(f"Query: '{q}' -> Intent: {intent}")

if __name__ == "__main__":
    test()
