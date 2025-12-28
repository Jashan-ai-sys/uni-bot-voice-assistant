#!/usr/bin/env python3
"""
Quick test to verify MCP agent loop works correctly
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_agent import UniAgent

async def test_single_query():
    """Test single query without interactive loop"""
    agent = UniAgent()
    
    # Test query
    query = "What are the hostel fees?"
    
    print(f"\n{'='*60}")
    print(f"Testing Agent with Query: {query}")
    print(f"{'='*60}\n")
    
    try:
        # Use the streaming method designed for web app
        print("🔄 Starting agent stream...\n")
        async for chunk in agent.process_query_stream(query):
            print(chunk, end='', flush=True)
        print("\n\n✅ Test complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_query())
