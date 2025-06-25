# Server tools and utilities
"""
MCP tool definitions and registry
"""

import logging
from typing import Dict, List, Any
from pathlib import Path
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for MCP tools"""

    def __init__(self, db_manager, llm_client, chart_generator):
        self.db_manager = db_manager
        self.llm_client = llm_client
        self.chart_generator = chart_generator

        # Define all available tools
        self.tools = self._define_tools()

    def _define_tools(self) -> List[Tool]:
        """Define all MCP tools"""
        return [
            Tool(
                name="list_tables",
                description="List all available database tables with metadata",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="analyze_table",
                description="Get detailed information about a table including columns, types, and sample data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to analyze",
                        }
                    },
                    "required": ["table_name"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="suggest_visualizations",
                description="Get visualization suggestions based on table structure and data types",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to analyze for visualization suggestions",
                        }
                    },
                    "required": ["table_name"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="create_visualization",
                description="Start creating a data visualization from natural language request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request": {
                            "type": "string",
                            "description": "Natural language description of desired visualization",
                        },
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table containing the data to visualize",
                        },
                    },
                    "required": ["request", "table_name"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="configure_chart",
                description="Configure chart parameters by answering column selection questions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request_id": {
                            "type": "string",
                            "description": "Request ID from the create_visualization step",
                        },
                        "x_axis": {
                            "type": "string",
                            "description": "Column name for X-axis",
                        },
                        "y_axis": {
                            "type": "string",
                            "description": "Column name for Y-axis",
                        },
                        "color": {
                            "type": "string",
                            "description": "Column name for color grouping (optional)",
                        },
                        "size": {
                            "type": "string",
                            "description": "Column name for size mapping (optional, for scatter plots)",
                        },
                        "category": {
                            "type": "string",
                            "description": "Column name for categories (for pie charts)",
                        },
                        "values": {
                            "type": "string",
                            "description": "Column name for values (for pie charts)",
                        },
                        "column": {
                            "type": "string",
                            "description": "Column name to analyze (for histograms)",
                        },
                        "groupby": {
                            "type": "string",
                            "description": "Column name for grouping (optional, for box plots)",
                        },
                        "insights": {
                            "type": "string",
                            "description": "Comma-separated list of insights to calculate: max, min, mean, median, distinct_count, total_count, correlation, trend, outliers, distribution",
                        },
                    },
                    "required": ["request_id"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="load_csv_data",
                description="Load CSV file into the database as a new table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the CSV file to load",
                        },
                        "table_name": {
                            "type": "string",
                            "description": "Name for the new table",
                        },
                    },
                    "required": ["file_path", "table_name"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="query_data",
                description="Execute a SQL query on the database and return results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "SQL SELECT query to execute",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return (default: 100)",
                            "default": 100,
                        },
                    },
                    "required": ["sql_query"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="get_column_stats",
                description="Get detailed statistics for a specific column",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table",
                        },
                        "column_name": {
                            "type": "string",
                            "description": "Name of the column to analyze",
                        },
                    },
                    "required": ["table_name", "column_name"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="create_sample_chart",
                description="Create a sample chart for testing (useful for development)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "chart_type": {
                            "type": "string",
                            "description": "Type of chart to create",
                            "enum": [
                                "bar",
                                "line",
                                "scatter",
                                "pie",
                                "histogram",
                                "box",
                                "heatmap",
                                "area",
                            ],
                            "default": "bar",
                        }
                    },
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="validate_chart_config",
                description="Validate if column mappings are appropriate for a chart type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "chart_type": {
                            "type": "string",
                            "description": "Type of chart",
                            "enum": [
                                "bar",
                                "line",
                                "scatter",
                                "pie",
                                "histogram",
                                "box",
                                "heatmap",
                                "area",
                            ],
                        },
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table",
                        },
                        "column_mappings": {
                            "type": "object",
                            "description": "Mapping of chart roles to column names",
                            "additionalProperties": {"type": "string"},
                        },
                    },
                    "required": ["chart_type", "table_name", "column_mappings"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="explain_chart_types",
                description="Get explanations of different chart types and their use cases",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "chart_type": {
                            "type": "string",
                            "description": "Specific chart type to explain (optional)",
                            "enum": [
                                "bar",
                                "line",
                                "scatter",
                                "pie",
                                "histogram",
                                "box",
                                "heatmap",
                                "area",
                            ],
                        }
                    },
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="server_status",
                description="Get server status and health information",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            ),
            # ✅ NEW: Database switching tools
            Tool(
                name="change_database",
                description="Connect to a different DuckDB database file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_path": {
                            "type": "string",
                            "description": "Full path to the DuckDB database file (e.g., C:/path/to/database.duckdb) or ':memory:' for in-memory database",
                        }
                    },
                    "required": ["database_path"],
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="browse_databases",
                description="Browse and list available DuckDB database files in a directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "directory_path": {
                            "type": "string",
                            "description": "Directory path to search for .duckdb files (e.g., C:/data/ or ./databases/)",
                            "default": "./data/",
                        }
                    },
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="list_recent_databases",
                description="List recently used databases for quick switching",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="browse_and_select_database",
                description="Interactively browse and select a database from a directory with numbered options",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "directory_path": {
                            "type": "string",
                            "description": "Directory path to search for .duckdb files",
                            "default": "./data/",
                        },
                        "show_all_files": {
                            "type": "boolean",
                            "description": "Also show non-database files for reference",
                            "default": False,
                        },
                    },
                    "additionalProperties": False,
                },
            ),
            Tool(
                name="select_database_by_number",
                description="Select a database by its number from the browse results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "selection_number": {
                            "type": "integer",
                            "description": "The number of the database from the browse list to connect to",
                        },
                        "directory_path": {
                            "type": "string",
                            "description": "The directory that was browsed (needed to resolve the path)",
                            "default": "./data/",
                        },
                    },
                    "required": ["selection_number"],
                    "additionalProperties": False,
                },
            ),
        ]

    async def handle_browse_and_select_database(
        self, directory_path: str = "./data/", show_all_files: bool = False
    ) -> List[TextContent]:
        """Browse databases with numbered selection"""
        try:
            search_path = Path(directory_path)
            if not search_path.exists():
                return [
                    TextContent(
                        type="text", text=f"❌ Directory not found: {directory_path}"
                    )
                ]

            # Find database files
            db_files = list(search_path.glob("*.duckdb"))

            # Optionally show other files too
            other_files = []
            if show_all_files:
                all_files = [f for f in search_path.iterdir() if f.is_file()]
                other_files = [f for f in all_files if not f.name.endswith(".duckdb")]

            result = f"📁 **Database Browser: {directory_path}**\n\n"

            if db_files:
                result += "🗃️ **Available Databases:**\n"
                for i, db_file in enumerate(db_files, 1):
                    size_mb = db_file.stat().st_size / (1024 * 1024)
                    modified = db_file.stat().st_mtime
                    import datetime

                    mod_date = datetime.datetime.fromtimestamp(modified).strftime(
                        "%Y-%m-%d %H:%M"
                    )

                    result += f"**{i}.** `{db_file.name}` ({size_mb:.1f}MB, modified: {mod_date})\n"

                result += f"\n💡 **To connect:** Use `select_database_by_number` with a number (1-{len(db_files)})\n"
                result += '📝 **Example:** "Select database number 2"\n\n'
            else:
                result += "❌ No .duckdb files found in this directory.\n\n"

            if other_files and show_all_files:
                result += "📄 **Other files in directory:**\n"
                for f in other_files[:10]:  # Limit to 10 files
                    result += f"   • {f.name}\n"
                if len(other_files) > 10:
                    result += f"   ... and {len(other_files) - 10} more files\n"

            result += "\n🔧 **Other options:**\n"
            result += "• Use `change_database` with a full path\n"
            result += "• Use `:memory:` for in-memory database\n"
            result += "• Browse a different directory\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"❌ Error browsing databases: {str(e)}")
            ]

    async def handle_select_database_by_number(
        self, selection_number: int, directory_path: str = "./data/"
    ) -> List[TextContent]:
        """Select database by number from browse results"""
        try:
            search_path = Path(directory_path)
            db_files = sorted(list(search_path.glob("*.duckdb")))

            if not db_files:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ No database files found in {directory_path}",
                    )
                ]

            if selection_number < 1 or selection_number > len(db_files):
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Invalid selection. Please choose a number between 1 and {len(db_files)}",
                    )
                ]

            selected_db = db_files[selection_number - 1]

            # Use the existing change_database logic
            return await self.handle_change_database(str(selected_db))

        except Exception as e:
            return [
                TextContent(type="text", text=f"❌ Error selecting database: {str(e)}")
            ]

    async def list_tools(self) -> List[Tool]:
        """Return list of all available tools"""
        return self.tools

    def get_tool_by_name(self, name: str) -> Tool:
        """Get tool definition by name"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        raise ValueError(f"Tool not found: {name}")

    def validate_tool_arguments(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate tool arguments against schema"""
        try:
            tool = self.get_tool_by_name(tool_name)

            # Basic validation - check required fields
            required_fields = tool.inputSchema.get("required", [])
            for field in required_fields:
                if field not in arguments:
                    return {
                        "valid": False,
                        "error": f"Missing required argument: {field}",
                    }

            # Check for unexpected fields if additionalProperties is False
            if not tool.inputSchema.get("additionalProperties", True):
                allowed_fields = set(tool.inputSchema.get("properties", {}).keys())
                provided_fields = set(arguments.keys())
                unexpected_fields = provided_fields - allowed_fields

                if unexpected_fields:
                    return {
                        "valid": False,
                        "error": f"Unexpected arguments: {', '.join(unexpected_fields)}",
                    }

            return {"valid": True}

        except ValueError as e:
            return {"valid": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error validating tool arguments: {e}")
            return {"valid": False, "error": "Validation error"}

    def get_tool_help(self, tool_name: str = None) -> str:
        """Get help information for tools"""
        if tool_name:
            try:
                tool = self.get_tool_by_name(tool_name)
                help_text = f"**{tool.name}**\n\n"
                help_text += f"Description: {tool.description}\n\n"

                if tool.inputSchema.get("properties"):
                    help_text += "Parameters:\n"
                    for prop_name, prop_def in tool.inputSchema["properties"].items():
                        required = prop_name in tool.inputSchema.get("required", [])
                        prop_type = prop_def.get("type", "unknown")
                        description = prop_def.get("description", "No description")

                        help_text += f"- **{prop_name}** ({prop_type})"
                        if required:
                            help_text += " *required*"
                        help_text += f": {description}\n"

                        if "enum" in prop_def:
                            help_text += (
                                f"  Valid values: {', '.join(prop_def['enum'])}\n"
                            )
                        if "default" in prop_def:
                            help_text += f"  Default: {prop_def['default']}\n"

                return help_text

            except ValueError:
                return f"Tool '{tool_name}' not found."

        else:
            # List all tools
            help_text = "# Available Tools\n\n"

            # Group tools by category
            categories = {
                "Data Management": [
                    "list_tables",
                    "analyze_table",
                    "load_csv_data",
                    "query_data",
                    "get_column_stats",
                ],
                "Visualization": [
                    "create_visualization",
                    "configure_chart",
                    "suggest_visualizations",
                    "validate_chart_config",
                ],
                "Database Management": [
                    "change_database",
                    "browse_databases",
                    "list_recent_databases",
                ],
                "Utilities": [
                    "create_sample_chart",
                    "explain_chart_types",
                    "server_status",
                ],
            }

            for category, tool_names in categories.items():
                help_text += f"## {category}\n\n"
                for tool_name in tool_names:
                    try:
                        tool = self.get_tool_by_name(tool_name)
                        help_text += f"- **{tool.name}**: {tool.description}\n"
                    except ValueError:
                        continue
                help_text += "\n"

            help_text += (
                "Use `explain_chart_types` to learn about available chart types.\n"
            )
            help_text += "Use `server_status` to check server health.\n\n"
            help_text += "For detailed help on a specific tool, ask about that tool specifically."

            return help_text

    # ✅ NEW: Database management methods
    async def handle_change_database(self, database_path: str) -> List[TextContent]:
        """Handle changing database connection"""
        try:
            # Close current connection
            if self.db_manager:
                self.db_manager.close()

            # Create new database manager with new path
            from database.manager import DatabaseManager

            new_path = (
                Path(database_path) if database_path != ":memory:" else database_path
            )
            self.db_manager = DatabaseManager(db_path=new_path)

            # Get table info from new database
            tables = self.db_manager.get_tables()

            return [
                TextContent(
                    type="text",
                    text=f"✅ Successfully connected to database: {database_path}\n\nAvailable tables: {', '.join([t['name'] for t in tables]) if tables else 'No tables found'}",
                )
            ]

        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Failed to connect to database {database_path}: {str(e)}",
                )
            ]

    async def handle_browse_databases(
        self, directory_path: str = "./data/"
    ) -> List[TextContent]:
        """Browse for available database files"""
        try:
            search_path = Path(directory_path)
            if not search_path.exists():
                return [
                    TextContent(
                        type="text", text=f"❌ Directory not found: {directory_path}"
                    )
                ]

            # Find all .duckdb files
            db_files = list(search_path.glob("*.duckdb"))

            if not db_files:
                return [
                    TextContent(
                        type="text",
                        text=f"No .duckdb files found in {directory_path}\n\nYou can:\n1. Create a new database by specifying a new path\n2. Use ':memory:' for an in-memory database",
                    )
                ]

            result = f"📁 Found {len(db_files)} database files in {directory_path}:\n\n"
            for i, db_file in enumerate(db_files, 1):
                # Get file size
                size_mb = db_file.stat().st_size / (1024 * 1024)
                result += f"{i}. **{db_file.name}**\n"
                result += f"   Path: `{db_file}`\n"
                result += f"   Size: {size_mb:.2f} MB\n\n"

            result += "To connect to any of these databases, use the `change_database` tool with the full path."

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"❌ Error browsing databases: {str(e)}")
            ]

    async def handle_list_recent_databases(self) -> List[TextContent]:
        """List recent databases for quick switching"""
        try:
            # This would ideally be stored in the server instance
            # For now, return a simple list
            current_path = str(self.db_manager.db_path) if self.db_manager else "None"

            result = "📂 **Database Management:**\n\n"
            result += f"🔗 **Currently connected:** `{current_path}`\n\n"
            result += "💡 **Available Commands:**\n"
            result += "• `change_database` - Connect to a different database file\n"
            result += "• `browse_databases` - Find database files in a directory\n"
            result += "• Use path like `C:/path/to/database.duckdb` or `:memory:`\n\n"
            result += "**Example usage:**\n"
            result += '• "Connect to C:/my-data/sales.duckdb"\n'
            result += '• "Switch to in-memory database"\n'
            result += '• "Browse databases in ./data/ folder"'

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"❌ Error listing databases: {str(e)}")
            ]
