"""
MCP Data Visualization Server

Transform natural language into beautiful data visualizations using Claude Desktop and DuckDB.
"""

__version__ = "0.0.3"
__author__ = "MCP Visualization Contributors"
__email__ = "support@example.com"

try:
    from .claude_config import configure_claude_desktop
    from .database import create_sample_database
    from .server import test_server_import
except ImportError:
    # Handle case where dependencies aren't installed yet
    pass

__all__ = [
    "configure_claude_desktop", 
    "create_sample_database",
    "test_server_import",
    "__version__",
]