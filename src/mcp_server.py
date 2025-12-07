from mcp.server.fastmcp import FastMCP
from rag_pipeline import answer_question
import sys

# Initialize FastMCP server
mcp = FastMCP("uni-rag-server")

import logging

# Setup logging
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "mcp_debug.log")
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("🚀 MCP Server Starting...")

@mcp.tool()
def search_docs(query: str, student_id: str = None) -> str:
    """
    Search university documents to answer a student's question.
    Use this tool when the user asks about admissions, fees, exams, syllabus, or rules.
    
    If the user asks about THEIR specific class, timetable, or schedule (e.g. "When is my next class?"),
    YOU MUST ASK FOR THEIR "Student ID" first. Once they provide it, call this tool with the `student_id` argument.
    
    Args:
        query: The student's question or search query.
        student_id: (Optional) The student's ID (e.g., 12345678) if answering personal questions.
    """
    logging.info(f"🔍 Received query: {query} | Student ID: {student_id}")
    print(f"🔍 Query: {query} | ID: {student_id}", file=sys.stderr)
    try:
        answer = answer_question(query, student_id=student_id)
        logging.info(f"✅ Generated answer length: {len(answer)}")
        return answer
    except Exception as e:
        logging.error(f"❌ Error in search_docs: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
