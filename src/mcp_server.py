import os
import sys

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from src.rag_pipeline import retrieve_context
from src import user_storage
import logging
import json

# Initialize FastMCP server
mcp = FastMCP("uni-rag-server")

# Setup logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "mcp_server.log")
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("🚀 MCP Server Starting...")

# CRITICAL: Pre-load resources to prevent blocking during tool calls
logging.info("📦 Pre-loading RAG resources...")
try:
    from src.rag_pipeline import _lazy_load_resources
    _lazy_load_resources()
    logging.info("✅ Resources loaded successfully")
except Exception as e:
    logging.error(f"❌ Failed to pre-load resources: {e}")
    # Continue anyway - will lazy load on first call

@mcp.tool()
def search_documents(query: str) -> str:
    """
    Search university documents (vectors) for relevant context.
    Returns raw text chunks relevant to the query.
    
    Args:
        query: The search query (e.g., "hostel fees", "exam rules")
    """
    logging.info(f"🔍 [TOOL] search_documents: {query}")
    try:
        context = retrieve_context(query)
        if not context:
            return "No relevant documents found."
        return context
    except Exception as e:
        logging.error(f"❌ Error in search_documents: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def query_database(query_type: str, params: str) -> str:
    """
    Query the structured database (Postgres/JSON) for specific student data.
    
    Args:
        query_type: Type of query. Supported: 'timetable', 'profile'
        params: JSON string of parameters (e.g., '{"student_id": "123"}')
    """
    logging.info(f"💾 [TOOL] query_database: {query_type} | {params}")
    try:
        try:
            p = json.loads(params)
        except:
             return "Error: params must be a valid JSON string"
             
        student_id = p.get("student_id")
        if not student_id:
            return "Error: student_id is required in params"

        if query_type == "timetable":
            data = user_storage.get_user_timetable(student_id)
            if data:
                return json.dumps(data, indent=2)
            return "Timetable not found."
            
        elif query_type == "profile":
            data = user_storage.get_user_profile(student_id)
            if data:
                return json.dumps(data, indent=2)
            return "Profile not found."
            
        return f"Error: Unsupported query_type '{query_type}'"
        
    except Exception as e:
        logging.error(f"❌ Error in query_database: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def check_eligibility(student_id: str, context: str) -> str:
    """
    Checks student eligibility for exams or other activities based on strict rules.
    
    Args:
        student_id: The student's ID (e.g., "12345")
        context: The context to check (e.g., "exam", "fee", "attendance")
    """
    logging.info(f"⚖️ [TOOL] check_eligibility: {student_id} | {context}")
    try:
        record = user_storage.get_academic_record(student_id)
        if not record:
            return "Error: Student record not found."
            
        if context.lower() in ["exam", "exams"]:
            # Rule: Attendance >= 75%
            # We assume 'attendance' in record has 'average_percentage'
            att = record.get("attendance", {}).get("average_percentage", 0)
            if att < 75.0:
                 return f"NOT ELIGIBLE. Attendance is {att}% (Requires 75%)."
            
            # Rule: No Fee Dues
            fees = record.get("fees", {})
            if fees.get("status") != "Paid":
                 return f"NOT ELIGIBLE. Fee status is '{fees.get('status')}'. Please clear dues."
                 
            return "ELIGIBLE. Attendance and Fee requirements met."
            
        elif context.lower() in ["fee", "fees", "dues"]:
            fees = record.get("fees", {})
            return f"Fee Status: {fees.get('status')}. Amount Due: {fees.get('amount_due', 0)}"
            
        elif context.lower() in ["attendance"]:
             att = record.get("attendance", {})
             return f"Average Attendance: {att.get('average_percentage')}%"
             
        return f"Error: Unknown context '{context}'. Supported: exam, fee, attendance."
        
    except Exception as e:
        logging.error(f"❌ Error in check_eligibility: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def get_metadata() -> str:
    """
    Get server metadata and status.
    """
    logging.info("ℹ️ [TOOL] get_metadata")
    return json.dumps({
        "server": "uni-rag-server",
        "version": "1.0",
        "status": "online",
        "capabilities": ["search_documents", "query_database"]
    }, indent=2)

if __name__ == "__main__":
    # fastmcp runs on stdio by default
    print("Listening on Stdio...", file=sys.stderr)
    mcp.run()
