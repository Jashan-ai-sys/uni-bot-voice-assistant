import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

try:
    from mcp_server import search_documents, query_database, get_metadata
    print("✅ Successfully imported MCP tools.")
    
    # Test get_metadata
    meta = get_metadata()
    print(f"Metadata: {meta}")
    
    # Test search (mocking retrieve_context if needed, but let's try real if vectorstore loads)
    # The rag_pipeline loads vectorstore on import, so it might take a second.
    print("Testing search_documents...")
    res = search_documents("hostel fees")
    print(f"Search Result Length: {len(res)}")
    
    # Test DB
    print("Testing query_database...")
    db_res = query_database("timetable", '{"student_id": "123"}')
    print(f"DB Result: {db_res}")
    
    print("✅ MCP functionality verified locally.")
    
except Exception as e:
    print(f"❌ Verification Failed: {e}")
    import traceback
    traceback.print_exc()
