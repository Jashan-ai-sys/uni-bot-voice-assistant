try:
    import mcp
    print("MCP Package found")
    print(dir(mcp))
    try:
        from mcp import client
        print("mcp.client found")
        print(dir(client))
    except ImportError:
        print("mcp.client NOT found")

    try:
        from mcp.client.stdio import StdioServerParameters, stdio_client
        print("mcp.client.stdio found")
    except ImportError:
        print("mcp.client.stdio NOT found")

except ImportError:
    print("MCP Package NOT found")
