"""
Main MCP server entry point for package installation
"""

import asyncio
import sys
from pathlib import Path

# Add package to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .mcp_server.server import DataVisualizationMCPServer


def test_server_import():
    """Test that server can be imported (for CLI testing)"""
    try:
        from .mcp_server.server import DataVisualizationMCPServer
        return True
    except ImportError as e:
        raise ImportError(f"Failed to import server: {e}")


async def main():
    """Main entry point for MCP server"""
    try:
        server = DataVisualizationMCPServer()
        await server.run(transport="stdio")
    except KeyboardInterrupt:
        print("Server shutdown requested", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()) or 0)