"""Main entry point for the Android MCP Server."""

import sys
from .server import create_mcp_server


def main():
    """Run the MCP server."""
    mcp = create_mcp_server()

    # Check if adb is available
    import subprocess
    try:
        subprocess.run(["adb", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: adb not found. Please install Android SDK platform-tools.", file=sys.stderr)

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
