import asyncio
import json
import logging
import sys
import os
from typing import List, Dict, Any

# Fix path for standalone execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.llm_router import get_llm

# Import our MCP Client
from src.mcp_client import UniMcpClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("uni-agent")

class UniAgent:
    def __init__(self):
        # Initialize LLM via Router
        self.llm = get_llm()
        self.history = []
        self.system_prompt = ""

    def _build_system_prompt(self, tools: List[Any]):
        """Constructs the system prompt with tool definitions."""
        tool_desc = ""
        for t in tools:
            tool_desc += f"- {t.name}: {t.description}\n"
            # Parse inputsSchema (JSON Schema) for more detail if needed
            # For now, description is usually enough for simple tools
            
        self.system_prompt = f"""You are JARVIS, an intelligent university assistant.
You have access to the following tools:

{tool_desc}

CRITICAL RULES:
1. If the user asks a question that requires information from the university (fees, rules, locations), use 'search_documents'.
2. If the user asks about THEIR specific data (timetable, profile), ask for their Student ID first (if not provided). Once you have it, use 'query_database'.
3. To call a tool, you MUST use this EXACT format and STOP immediately after:
   Action: <tool_name>
   Action Input: <json_string>
   
   DO NOT write anything else after the Action Input. STOP THERE.
   
4. NEVER write "Observation:" yourself. The system will provide observations to you.
5. After the SYSTEM gives you an "Observation:", use that information to answer the user in 1-2 sentences.
6. FOR ELIGIBILITY (Exams, Fees): ALWAYS use 'check_eligibility'. Do NOT guess. The tool is the final judge.

CORRECT Example:
User: What are the hostel fees?
Assistant: Action: search_documents
Action Input: {{"query": "hostel fees"}}

[System provides Observation]
Observation: The hostel fee is $1000 per year.
Assistant: The hostel fee is $1000 per year.

WRONG Example (DO NOT DO THIS):
User: What are the hostel fees?
Assistant: Action: search_documents
Action Input: {{"query": "hostel fees"}}
Observation: The hostel fee is... ← WRONG! Do not write observations!

User: Am I eligible for the exam?
Assistant: I need your Student ID to check eligibility.

User: My ID is 12345.
Assistant: Action: check_eligibility
Action Input: {{"student_id": "12345", "context": "exam"}}
"""
        return self.system_prompt

    async def chat_loop(self):
        """Main ReAct Loop."""
        async with UniMcpClient() as mcp:
            # 1. Discover Tools
            tools = await mcp.get_tools()
            logger.info(f"Agent initialized with tools: {[t.name for t in tools]}")
            
            # 2. Build Prompt
            system_msg = SystemMessage(content=self._build_system_prompt(tools))
            self.history = [system_msg]
            
            print("\n==================================================")
            print("🚀 LPU Bot (MCP Architecture)")
            print("   - Engine:  llama.cpp (via Ollama)")
            print("   - OS:      MCP Server (Capabilities)")
            print("   - Product: Intelligent Agent")
            print("==================================================")
            print("“We use llama.cpp as a local LLM inference engine and MCP as the capability layer,")
            print(" allowing secure, cost-free, and tool-driven AI workflows.”")
            print("==================================================\n")
            print("🤖 JARVIS Agent Ready. Ask me anything!")
            
            while True:
                try:
                    user_input = await asyncio.get_event_loop().run_in_executor(None, input, "\nUser: ")
                    user_input = user_input.strip()
                    if user_input.lower() in ['exit', 'quit']:
                        break
                        
                    self.history.append(HumanMessage(content=user_input))
                    
                    # Run Step
                    await self._run_step(mcp)
                    
                except Exception as e:
                    logger.error(f"Error: {e}")

    async def _run_step(self, mcp: UniMcpClient):
        """Executes one or more steps (LLM -> Tool -> LLM)."""
        # Limit steps to prevent infinite loops
        for _ in range(3):
            # Invoke LLM
            response = self.llm.invoke(self.history)
            content = response.content
            print(f"\nModel: {content}")
            
            self.history.append(AIMessage(content=content))
            
            # Check for Intent
            if "Action:" in content:
                # Parse Tool Call (Naive parsing for stability)
                try:
                    lines = content.split('\n')
                    action_line = next(line for line in lines if "Action:" in line)
                    tool_name = action_line.split("Action:", 1)[1].strip()
                    
                    # Look for input
                    # Sometimes LLM puts it on same line, sometimes next
                    start_marker = "Action Input:"
                    if start_marker not in content:
                        print("❌ invalid action format: missing input")
                        continue
                        
                    # Extract everything after "Action Input:"
                    input_segment = content.split(start_marker, 1)[1].strip()
                    
                    # Robust JSON extraction
                    def extract_json(s):
                        s = s.strip()
                        # If wrapped in code blocks, strip them
                        if "```" in s:
                           s = s.split("```")[1]
                           if s.startswith("json"): s = s[4:]
                        
                        s = s.strip()
                        # Find outer braces
                        start = s.find('{')
                        end = s.rfind('}')
                        if start != -1 and end != -1:
                            s = s[start:end+1]
                        return json.loads(s)

                    try:
                        args = extract_json(input_segment)
                    except Exception as e:
                        print(f"❌ JSON Parse Error: {e} | Input: {input_segment[:50]}...")
                        self.history.append(HumanMessage(content=f"System Error: Invalid JSON in Action Input. {e}"))
                        continue
                    
                    print(f"⚙️ Executing {tool_name} with {args} ...")
                    
                    # Execute
                    result_obj = await mcp.call_tool(tool_name, args)
                    
                    # Extract text content
                    # Result is list of Content objects
                    observation = ""
                    for c in result_obj.content:
                        if c.type == 'text':
                            observation += c.text + "\n"
                    
                    # Feed back to LLM
                    obs_msg = f"Observation: {observation}"
                    self.history.append(HumanMessage(content=obs_msg))
                    
                    print(f"✅ Tool executed. Observation added to history.") # Debug
                    print(f"📝 Continuing loop to let LLM generate final answer...") # Debug
                    
                    # Continue loop to let LLM interpret observation
                    continue
                    
                except Exception as ToolErr:
                    print(f"❌ Tool Execution Failed: {ToolErr}")
                    self.history.append(HumanMessage(content=f"System Error: Failed to execute tool. {ToolErr}"))
            
            # If no action, we are done
            break

    async def process_query_stream(self, query: str, student_id: str = None):
        """
        Process a single query with streaming response (for FastAPI integration).
        Yields text chunks as the agent thinks and responds.
        
        Args:
            query: User's question
            student_id: Optional student ID for personalized queries
        """
        async with UniMcpClient() as mcp:
            # 1. Discover Tools
            tools = await mcp.get_tools()
            
            # 2. Build Prompt (inject student_id if provided)
            system_msg = SystemMessage(content=self._build_system_prompt(tools))
            
            # Add context about student ID if provided
            if student_id:
                query = f"[Student ID: {student_id}] {query}"
            
            self.history = [system_msg, HumanMessage(content=query)]
            
            # 3. Run agent loop with streaming
            for step_num in range(3):  # Limit steps
                # Invoke LLM
                response = self.llm.invoke(self.history)
                content = response.content
                
                self.history.append(AIMessage(content=content))
                
                # Check for tool call
                if "Action:" in content:
                    try:
                        # Parse tool call
                        lines = content.split('\n')
                        action_line = next(line for line in lines if "Action:" in line)
                        tool_name = action_line.split("Action:", 1)[1].strip()
                        
                        if "Action Input:" not in content:
                            yield f"❌ Error: Invalid action format\n"
                            break
                        
                        input_segment = content.split("Action Input:", 1)[1].strip()
                        
                        # Extract JSON
                        def extract_json(s):
                            s = s.strip()
                            if "```" in s:
                                s = s.split("```")[1]
                                if s.startswith("json"): s = s[4:]
                            s = s.strip()
                            start = s.find('{')
                            end = s.rfind('}')
                            if start != -1 and end != -1:
                                s = s[start:end+1]
                            return json.loads(s)
                        
                        args = extract_json(input_segment)
                        
                        # Notify user of tool use
                        yield f"🔍 [Using {tool_name}...]\n"
                        
                        # Execute tool
                        result_obj = await mcp.call_tool(tool_name, args)
                        
                        # Extract observation
                        observation = ""
                        for c in result_obj.content:
                            if c.type == 'text':
                                observation += c.text + "\n"
                        
                        # Feed back to history
                        self.history.append(HumanMessage(content=f"Observation: {observation}"))
                        
                        # Continue loop for final answer
                        continue
                        
                    except Exception as e:
                        yield f"❌ Tool error: {str(e)}\n"
                        break
                else:
                    # No tool call - this is the final answer
                    # Stream it word by word for better UX
                    words = content.split()
                    for i, word in enumerate(words):
                        yield word + (" " if i < len(words) - 1 else "")
                        await asyncio.sleep(0.01)  # Simulated streaming delay
                    break


if __name__ == "__main__":
    agent = UniAgent()
    try:
        asyncio.run(agent.chat_loop())
    except KeyboardInterrupt:
        print("\nExiting...")
