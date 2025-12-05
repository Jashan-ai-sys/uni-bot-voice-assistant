from mcp.server.fastmcp import FastMCP
from rag_pipeline import answer_question
import sys

# Initialize FastMCP server
mcp = FastMCP("uni-rag-server")

@mcp.tool()
def search_docs(query: str) -> str:
    """
    Search university documents to answer a student's question.
    Use this tool when the user asks about admissions, fees, exams, syllabus, or rules.
    
    Args:
        query: The student's question or search query.
    """
    print(f"🔍 Received query: {query}", file=sys.stderr)
    answer = answer_question(query)
    return answer

if __name__ == "__main__":
    mcp.run()
