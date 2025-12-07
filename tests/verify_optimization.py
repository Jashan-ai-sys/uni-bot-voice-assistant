import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rag_pipeline import answer_question, identify_intent

def verify():
    test_cases = [
        "Where is the library located?",
        "What is the fee for B.Tech CSE?",
        "What are the hostel timings?",
        "Show me emergency contact numbers"
    ]
    
    print("🔍 Testing Intent Recognition:")
    for query in test_cases:
        intent = identify_intent(query)
        print(f"  - '{query}' -> Filter: {intent}")
        
    print("\n" + "="*50 + "\n")
    
    print("🤖 Testing Full Answers (with citations):")
    for query in test_cases:
        print(f"\nQuery: {query}")
        print("-" * 20)
        answer = answer_question(query)
        print(answer)
        print("-" * 20)

if __name__ == "__main__":
    verify()
