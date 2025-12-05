from rag_pipeline import answer_question
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing RAG Pipeline...")
print("-" * 50)

# Test with a simple question
test_question = "What is LPU?"

print(f"Question: {test_question}")
print("\nGenerating answer...")

try:
    answer = answer_question(test_question)
    print(f"\n✅ Answer received:\n{answer}")
    print("\n" + "=" * 50)
    print("✅ RAG Pipeline is working!")
    print("=" * 50)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
