# Update your code/main.py with these fixes:

import asyncio
import sys
import argparse
import logging
from pathlib import Path

# Add the code directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the config_manager instance directly from settings
from config.settings import config_manager, Settings
from utils.logger import setup_logging


def setup_environment():
    """Setup environment for the application"""
    # Set UTF-8 encoding for stdout to handle Unicode characters
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except:
            pass


def print_startup_banner():
    """Print startup banner - only when not in MCP mode"""
    # Skip banner in MCP/STDIO mode to avoid interfering with protocol
    if len(sys.argv) > 1 and any(
        arg in ["--stdio", "--transport=stdio"] for arg in sys.argv
    ):
        return

    # Also check if we're being run from Claude Desktop (no terminal)
    if not sys.stdout.isatty():
        return

    try:
        # Use simple ASCII banner instead of Unicode to avoid encoding issues
        banner = """
==============================================================
           MCP Data Visualization Server v1.0.0            
                                                            
         Transform data requests into beautiful charts   
         * DuckDB for fast local analytics                  
         * Rule-based chart analysis (no external LLM)     
         * Plotly for interactive visualizations            
==============================================================
"""
        print(banner)
    except UnicodeEncodeError:
        # Fallback to simple text if encoding fails
        print("MCP Data Visualization Server v1.0.0 - Starting...")


def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import duckdb
        import pandas
        import plotly

        # Only log to stderr to avoid interfering with MCP protocol
        logging.getLogger(__name__).info("All required dependencies are available")
        return True
    except ImportError as e:
        logging.getLogger(__name__).error(f"Missing dependency: {e}")
        return False


async def check_llm_setup():
    """Check LLM setup - using simple fallback"""
    try:
        from llm.simple_fallback import SimpleFallbackClient

        client = SimpleFallbackClient()
        is_ready = await client.check_connection()

        if is_ready:
            print("✓ Rule-based chart analysis ready (no external LLM needed)", file=sys.stderr)
        
        return is_ready
    except Exception as e:
        print(f"✗ LLM setup check failed: {e}", file=sys.stderr)
        return False


async def main():
    """Main entry point"""
    setup_environment()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP Data Visualization Server")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "websocket", "http"],
        help="Transport method for MCP communication",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for websocket/http transport"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Only print banner if not in MCP stdio mode
    if args.transport != "stdio" or sys.stdout.isatty():
        print_startup_banner()

    # Setup logging to stderr only
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    # Log to stderr to avoid MCP interference
    logger.info("Starting data-viz-server v1.0.0")

    # Check dependencies (log only, don't print)
    if not check_dependencies():
        logger.warning("Some dependencies may be missing")

    # Check LLM setup
    await check_llm_setup()

    # Get server configuration
    try:
        config: Settings = config_manager.get_settings()
        logger.info(
            f"Sample data generation on startup: {config.development.sample_data.generate_on_startup}"
        )
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return 1

    # Import and start the server
    try:
        from mcp_server.server import DataVisualizationMCPServer

        # Create and configure server
        server = DataVisualizationMCPServer()

        # Only print transport info to stderr if we have a terminal
        if sys.stdout.isatty():
            print(f"🚀 Starting MCP server...", file=sys.stderr)
            print(f"📊 Transport: {args.transport}", file=sys.stderr)

        await server.run(transport=args.transport)

    except KeyboardInterrupt:
        if sys.stdout.isatty():
            print("\n🛑 Server shutdown requested", file=sys.stderr)
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        if sys.stdout.isatty():
            print(f"❌ Server error: {e}", file=sys.stderr)
        return 1
    finally:
        if sys.stdout.isatty():
            print("👋 Goodbye!", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()) or 0)
