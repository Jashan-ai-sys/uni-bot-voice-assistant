import asyncio
import sys
import os
import logging
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp-client")

class UniMcpClient:
    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()

    async def __aenter__(self):
        """
        Context Manager entry: Connects to MCP Server.
        """
        python_exe = sys.executable
        # Assume mcp_server.py is in the same directory
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
        
        logger.info(f"Connecting to MCP Server: {script_path}")
        
        server_params = StdioServerParameters(
            command=python_exe,
            args=[script_path],
            env=os.environ.copy()
        )

        try:
            read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await self.session.initialize()
            logger.info("✅ Connected to MCP Server.")
            return self
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            await self.exit_stack.aclose()
            raise e

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Context Manager exit: Closes connection.
        """
        await self.exit_stack.aclose()
        logger.info("🔌 Disconnected from MCP Server.")

    async def get_tools(self):
        """Returns list of available tools."""
        if not self.session:
            raise RuntimeError("Not connected")
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, name: str, args: dict):
        """Calls a tool by name with arguments."""
        if not self.session:
            raise RuntimeError("Not connected")
        
        # Returns CallToolResult
        return await self.session.call_tool(name, arguments=args)

async def run_interactive_cli():
    """
    CLI loop for manual testing (backward compatibility).
    """
    async with UniMcpClient() as client:
        # List Tools
        tools = await client.get_tools()
        print(f"Connected. Available Tools: {[t.name for t in tools]}")
        
        print("\n🤖 MCP Client Ready. Type 'exit' to quit.")
        print("Commands: /tools, /call <tool> <json_args>")
        
        while True:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, "\n> ")
                user_input = user_input.strip()
                
                if user_input.lower() == 'exit':
                    break
                    
                if user_input.startswith("/tools"):
                    tools = await client.get_tools()
                    print("🛠️ Tools:")
                    for t in tools:
                        print(f" - {t.name}: {t.description}")
                        
                elif user_input.startswith("/call"):
                    parts = user_input.split(" ", 2)
                    if len(parts) < 3:
                        print("Usage: /call <tool_name> <json_args>")
                        continue
                        
                    tool_name = parts[1]
                    import json
                    try:
                        args = json.loads(parts[2])
                    except:
                        print("Invalid JSON args")
                        continue
                        
                    logger.info(f"Calling {tool_name} with {args}")
                    result = await client.call_tool(tool_name, args)
                    
                    print("\n📝 Result:")
                    for content in result.content:
                        if content.type == 'text':
                            print(content.text)
                        else:
                            print(f"[{content.type}]")
                else:
                        print("Unknown command. Try /tools or /call")
                        
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_interactive_cli())
    except KeyboardInterrupt:
        print("\nExiting...")
