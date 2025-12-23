"""
Test streaming RAG pipeline directly
"""
import asyncio
import sys
sys.path.append('src')

from rag_pipeline import answer_question_stream

async def test_streaming():
    print("🧪 Testing RAG Streaming Pipeline\n")
    print("=" * 60)
    
    query = "What are the hostel rules?"
    print(f"Query: {query}\n")
    print("Response:")
    print("-" * 60)
    
    chunk_count = 0
    total_text = ""
    
    try:
        async for chunk in answer_question_stream(query, None):
            chunk_count += 1
            total_text += chunk
            print(chunk, end='', flush=True)
        
        print("\n" + "=" * 60)
        print(f"\n✅ Test Complete!")
        print(f"   - Total chunks: {chunk_count}")
        print(f"   - Total chars: {len(total_text)}")
        print(f"   - Response received: {'YES' if total_text else 'NO'}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_streaming())
