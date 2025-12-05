import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rag_pipeline import answer_question

if __name__ == "__main__":
    q = "how do i get to 32 block"
    print(f"Question: {q}")
    ans = answer_question(q)
    
    with open("tests/reproduce_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Question: {q}\n")
        f.write(f"Answer: {ans}\n")
    
    print(f"Answer written to tests/reproduce_output.txt")
