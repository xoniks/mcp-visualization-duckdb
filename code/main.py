# code/main.py
#!/usr/bin/env python3
"""
Main entry point for the MCP Data Visualization Server
"""

import asyncio
import sys
import argparse
import logging
from pathlib import Path

# Add the code directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the config_manager instance directly from settings
# ✅ Import Settings for type hinting consistency
from config.settings import config_manager, Settings
from utils.logger import setup_logging

# Assuming DataVisualizationMCPServer is within mcp_server.server
from mcp_server.server import DataVisualizationMCPServer


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="MCP Data Visualization Server - Natural Language to Charts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Start with default settings
  python main.py --debug            # Enable debug logging
  python main.py --log-file logs/server.log   # Log to file
  python main.py --no-samples         # Don't generate sample data

Environment Variables:
  LOG_LEVEL                   Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  DEBUG_MODE                  Enable debug mode (true/false)
  GENERATE_SAMPLE_DATA        Generate sample data on startup (true/false)
  DATABASE_PATH               Path to DuckDB database file
  OLLAMA_BASE_URL             Ollama server URL (default: http://localhost:11434)
  OLLAMA_MODEL                Ollama model to use (default: codellama:7b)
        """,
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (overrides config)",
    )

    parser.add_argument(
        "--log-file", type=str, help="Log to file (in addition to console)"
    )

    parser.add_argument(
        "--no-samples",
        action="store_true",
        help="Don't generate sample data on startup",
    )

    parser.add_argument("--config", type=str, help="Path to configuration file")

    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="Transport protocol (currently only stdio is supported)",
    )

    parser.add_argument(
        "--version", action="version", version="MCP Data Visualization Server v1.0.0"
    )

    return parser.parse_args()


async def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        import httpx

        # ✅ Get the full settings object from config_manager
        settings: Settings = config_manager.get_settings()
        llm_config = settings.llm.ollama  # Direct access to the OllamaConfig

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{llm_config.base_url}/api/tags", timeout=5.0)

            if response.status_code == 200:
                models_data = response.json()
                models = [model["name"] for model in models_data.get("models", [])]

                if llm_config.model in models:
                    print(f"✅ Ollama connected - Model '{llm_config.model}' available")
                    return True
                else:
                    print(
                        f"⚠️  Ollama connected but model '{llm_config.model}' not found"
                    )
                    print(f"Available models: {', '.join(models[:5])}")
                    print(
                        f"You can pull the model with: ollama pull {llm_config.model}"
                    )
                    return True  # Still functional, just need to pull model
            else:
                print(f"❌ Ollama HTTP error: {response.status_code}")
                return False

    except Exception as e:
        print(f"⚠️  Cannot connect to Ollama: {e}")
        print("Make sure Ollama is running with: ollama serve")
        print("Server will use fallback methods for natural language processing")
        return True  # Don't fail completely, use fallbacks


def print_startup_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🎯 MCP Data Visualization Server v1.0.0            ║
║                                                              ║
║         Transform natural language into beautiful charts     ║
║         • DuckDB for fast local analytics                    ║
║         • Ollama for natural language processing             ║
║         • • Plotly for interactive visualizations            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()

    # Print banner
    print_startup_banner()

    # Load configuration using the global config_manager instance
    # This will load the YAML, .env, and environment variables
    settings: Settings = config_manager.get_settings()

    # Access specific config sections from the 'settings' object
    server_config = settings.server
    dev_config = settings.development

    # Override configuration with command line arguments
    if args.debug:
        log_level = "DEBUG"
    elif args.log_level:
        log_level = args.log_level
    else:
        log_level = server_config.log_level

    # Setup logging
    setup_logging(log_level=log_level, log_file=args.log_file, enable_rich=True)

    logger = logging.getLogger("mcp-viz-server")
    logger.info(f"Starting {server_config.name} v{server_config.version}")

    # --- REMOVE OR RE-THINK THIS SECTION ---
    # The original error was here because 'check_dependencies' is not defined.
    # If you intend to implement a general dependency check, you should create
    # that function (e.g., in utils/dependency_checker.py or within this file).
    # For now, we remove the problematic call.
    #
    # print("🔍 Checking dependencies...")
    # if not await check_dependencies(): # This line caused the error
    #    sys.exit(1)
    # print("✅ All dependencies available")
    #
    # For now, we can just print a placeholder or rely only on Ollama check.
    logger.info("Skipping general dependency check (not implemented yet or removed).")

    # Check Ollama connection (This function IS defined)
    print("🔍 Checking Ollama connection...")
    await check_ollama_connection()

    # Override sample data generation if requested by --no-samples
    # This directly modifies the Pydantic settings object's attribute
    if args.no_samples:
        settings.development.sample_data.generate_on_startup = False
        logger.info("Sample data generation disabled via --no-samples argument.")

    logger.info(
        f"Sample data generation on startup: {settings.development.sample_data.generate_on_startup}"
    )

    try:
        # Create server instance. The server's __init__ will now get config from config_manager.
        server = DataVisualizationMCPServer()

        print("🚀 Starting MCP server...")
        print(f"📊 Transport: {args.transport}")

        await server.run(transport=args.transport)

    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
        logger.info("Server shutdown by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        print("👋 Goodbye!")


def create_sample_chart():
    """Create a sample chart for testing (utility function)"""
    from visualization.chart_generator import ChartGenerator
    from visualization.chart_types import ChartType

    generator = ChartGenerator()
    html_widget = generator.create_sample_chart(ChartType.BAR)

    output_file = Path("sample_chart.html")
    with open(output_file, "w") as f:
        f.write(html_widget)

    print(f"Sample chart saved to: {output_file}")
    return html_widget


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sample":
        create_sample_chart()
    else:
        asyncio.run(main())
