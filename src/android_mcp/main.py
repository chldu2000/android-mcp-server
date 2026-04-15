"""Main entry point for the Android MCP Server."""

from fastmcp import FastMCP

mcp = FastMCP("android-mcp-server")


if __name__ == "__main__":
    mcp.run()