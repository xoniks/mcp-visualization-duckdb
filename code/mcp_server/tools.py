# Server tools and utilities
"""
MCP tool definitions and registry
"""

import logging
from typing import Dict, List, Any
from mcp.types import Tool

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
