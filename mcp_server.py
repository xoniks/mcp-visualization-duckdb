#!/usr/bin/env python3
"""
Simple launcher for MCP Data Visualization Server
This avoids module path issues and print statement interference
"""
import sys
import os
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault("DUCKDB_DATABASE_PATH", str(project_root / "data" / "mcp.duckdb"))

# Redirect stdout to stderr to avoid MCP protocol interference
# sys.stdout = sys.stderr


async def main():
    """Main entry point"""
    try:
        # Import the main function from your existing main.py
        from code.main import main as code_main

        # Run your existing main function
        return await code_main()

    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()) or 0)
