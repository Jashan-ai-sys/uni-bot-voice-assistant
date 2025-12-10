import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rag_pipeline import answer_question

def verify():
    query = "What are the emergency contact numbers for the university women help center?"
    print(f"Query: {query}")
    answer = answer_question(query)
    print("\nAnswer:\n")
    print(answer)

    print("\n" + "="*50 + "\n")
    
    query = "List all hostel emergency numbers"
    print(f"Query: {query}")
    answer = answer_question(query)
    print("\nAnswer:\n")
    print(answer)

if __name__ == "__main__":
    verify()
