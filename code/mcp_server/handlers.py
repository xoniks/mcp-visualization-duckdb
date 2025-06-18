"""
Request handlers for MCP tools
"""

import logging
import json
from typing import Dict, List, Any, Optional
from mcp.types import TextContent

from visualization.chart_types import ChartType, InsightType, chart_registry
from database.queries import QueryFilter
from mcp_server.types import VisualizationRequest

logger = logging.getLogger(__name__)


class RequestHandler:
    """Handles MCP tool requests"""

    def __init__(self, db_manager, llm_client, chart_generator, active_requests):
        self.db_manager = db_manager
        self.llm_client = llm_client
        self.chart_generator = chart_generator
        self.active_requests = active_requests

    async def handle_tool_call(self, name: str, arguments: dict) -> List[TextContent]:
        """Route tool calls to appropriate handlers"""
        try:
            # Map tool names to handler methods
            handlers = {
                "list_tables": self._handle_list_tables,
                "analyze_table": self._handle_analyze_table,
                "suggest_visualizations": self._handle_suggest_visualizations,
                "create_visualization": self._handle_create_visualization,
                "configure_chart": self._handle_configure_chart,
                "load_csv_data": self._handle_load_csv_data,
                "query_data": self._handle_query_data,
                "get_column_stats": self._handle_get_column_stats,
                "create_sample_chart": self._handle_create_sample_chart,
                "validate_chart_config": self._handle_validate_chart_config,
                "explain_chart_types": self._handle_explain_chart_types,
                "server_status": self._handle_server_status,
            }

            handler = handlers.get(name)
            if not handler:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

            return await handler(arguments)

        except Exception as e:
            logger.error(f"Error handling tool call '{name}': {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_list_tables(self, arguments: dict) -> List[TextContent]:
        """Handle list_tables tool"""
        try:
            tables = self.db_manager.get_tables()

            if not tables:
                return [
                    TextContent(
                        type="text",
                        text="No tables found in the database. Use 'load_csv_data' to add data, or check your database connection.",
                    )
                ]

            response = "**Available Tables:**\n\n"
            for table in tables:
                table_info = self.db_manager.get_table_info(table["name"])
                response += f"📊 **{table['name']}** ({table['type']})\n"
                if "row_count" in table_info:
                    response += f"   - {table_info['row_count']} rows, {len(table_info.get('columns', []))} columns\n"
                response += "\n"

            response += "Use `analyze_table` to get detailed information about a specific table."

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return [TextContent(type="text", text=f"Error listing tables: {e}")]

    async def _handle_analyze_table(self, arguments: dict) -> List[TextContent]:
        """Handle analyze_table tool"""
        try:
            table_name = arguments["table_name"]
            table_info = self.db_manager.get_table_info(table_name)

            if "error" in table_info:
                return [TextContent(type="text", text=f"Error: {table_info['error']}")]

            response = f"# Table Analysis: {table_name}\n\n"
            response += f"**Rows:** {table_info['row_count']}\n"
            response += f"**Columns:** {len(table_info['columns'])}\n\n"

            response += "## Column Information\n\n"
            for col in table_info["columns"]:
                response += f"- **{col['name']}** ({col['type']})"
                if col.get("nullable") == "NO":
                    response += " *required*"
                response += "\n"

            # Show sample data
            if table_info.get("sample_data"):
                response += "\n## Sample Data (first 5 rows)\n\n"
                sample_df = self.db_manager.execute_query(
                    f"SELECT * FROM {table_name} LIMIT 5"
                )
                if not sample_df.empty:
                    response += "```\n"
                    response += sample_df.to_string(index=False)
                    response += "\n```\n"

            response += f"\nUse `suggest_visualizations` with table '{table_name}' to get visualization recommendations."

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error analyzing table: {e}")
            return [TextContent(type="text", text=f"Error analyzing table: {e}")]

    async def _handle_suggest_visualizations(
        self, arguments: dict
    ) -> List[TextContent]:
        """Handle suggest_visualizations tool"""
        try:
            table_name = arguments["table_name"]
            columns = self.db_manager.get_columns(table_name)

            if not columns:
                return [
                    TextContent(
                        type="text",
                        text=f"Table '{table_name}' not found or has no columns.",
                    )
                ]

            # Get suggestions from chart registry
            suggestions = chart_registry.suggest_chart_types(columns)

            if not suggestions:
                return [
                    TextContent(
                        type="text",
                        text="No suitable visualizations found for this data.",
                    )
                ]

            response = f"# Visualization Suggestions for '{table_name}'\n\n"

            for i, suggestion in enumerate(suggestions[:5], 1):  # Top 5 suggestions
                response += f"## {i}. {suggestion['name']}\n"
                response += f"**Description:** {suggestion['description']}\n"
                response += f"**Why it fits:** {suggestion['reason']}\n"

                if suggestion.get("use_cases"):
                    response += f"**Use cases:** {', '.join(suggestion['use_cases'])}\n"

                response += f"**Chart type:** `{suggestion['chart_type']}`\n\n"

            response += "To create a visualization, use `create_visualization` with your chosen chart type and a natural language description of what you want to visualize."

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error suggesting visualizations: {e}")
            return [
                TextContent(type="text", text=f"Error suggesting visualizations: {e}")
            ]

    async def _handle_create_visualization(self, arguments: dict) -> List[TextContent]:
        """Handle create_visualization tool"""
        try:
            request = arguments["request"]
            table_name = arguments["table_name"]

            # Validate table exists
            columns = self.db_manager.get_columns(table_name)
            if not columns:
                return [
                    TextContent(type="text", text=f"Table '{table_name}' not found.")
                ]

            column_names = [col["name"] for col in columns]

            # Use LLM to detect chart type
            llm_response = await self.llm_client.detect_chart_type(
                request, column_names, table_name
            )

            if not llm_response.get("success"):
                return [
                    TextContent(
                        type="text",
                        text="Error detecting chart type. Please be more specific about what you want to visualize.",
                    )
                ]

            try:
                chart_type = ChartType(llm_response["chart_type"])
            except ValueError:
                chart_type = ChartType.BAR  # Default fallback

            # Generate request ID and store request
            request_id = f"req_{len(self.active_requests)}"
            viz_request = VisualizationRequest(
                id=request_id,
                chart_type=chart_type,
                table_name=table_name,
                original_request=request,
                column_mappings={},
                insights_requested=[],
                status="pending_config",
            )

            self.active_requests[request_id] = viz_request

            # Generate configuration questions
            questions = self._generate_configuration_questions(chart_type, columns)

            response = f"🎯 **Visualization Request Processed**\n\n"
            response += f"**Detected Chart Type:** {chart_type.value.title()} Chart\n"
            response += f"**Confidence:** {llm_response.get('confidence', 'N/A')}\n"
            response += f"**Request ID:** `{request_id}`\n\n"

            if llm_response.get("reasoning"):
                response += f"**Why this chart type:** {llm_response['reasoning']}\n\n"

            response += "## Configuration Needed\n\n"
            response += questions
            response += f"\n\n**Next Step:** Use `configure_chart` with request ID `{request_id}` and your column selections."

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return [TextContent(type="text", text=f"Error creating visualization: {e}")]

    def _generate_configuration_questions(
        self, chart_type: ChartType, columns: List[Dict[str, str]]
    ) -> str:
        """Generate configuration questions based on chart type"""
        col_list = ", ".join([f"`{col['name']}` ({col['type']})" for col in columns])

        questions = f"Available columns: {col_list}\n\n"

        # Get chart definition for requirements
        chart_def = chart_registry.get_chart_definition(chart_type)

        if chart_def:
            questions += "Please specify:\n\n"
            for req in chart_def.column_requirements:
                status = "**Required**" if req.required else "*Optional*"
                questions += f"- **{req.name}** ({status}): {req.description}\n"
                questions += f"  Expected data types: {', '.join(req.data_types)}\n"

            # Add insights options
            questions += "\n**Insights** (*Optional*): Which statistical insights would you like?\n"
            questions += "Choose from: `max`, `min`, `mean`, `median`, `distinct_count`, `total_count`, `correlation`, `trend`, `outliers`, `distribution`\n"

        return questions

    async def _handle_configure_chart(self, arguments: dict) -> List[TextContent]:
        """Handle configure_chart tool"""
        try:
            request_id = arguments["request_id"]

            if request_id not in self.active_requests:
                return [
                    TextContent(
                        type="text",
                        text=f"Request ID '{request_id}' not found. Please start a new visualization request.",
                    )
                ]

            viz_request = self.active_requests[request_id]

            # Update column mappings
            column_mappings = {}
            for key, value in arguments.items():
                if key != "request_id" and key != "insights" and value:
                    column_mappings[key] = value

            viz_request.column_mappings = column_mappings

            # Parse insights
            insights_requested = []
            if arguments.get("insights"):
                insight_names = [
                    name.strip() for name in arguments["insights"].split(",")
                ]
                for name in insight_names:
                    try:
                        insights_requested.append(InsightType(name))
                    except ValueError:
                        logger.warning(f"Unknown insight type: {name}")

            viz_request.insights_requested = insights_requested

            # Validate configuration
            columns = self.db_manager.get_columns(viz_request.table_name)
            validation = chart_registry.validate_chart_configuration(
                viz_request.chart_type, column_mappings, columns
            )

            if not validation["valid"]:
                error_msg = "Configuration validation failed:\n\n"
                for error in validation["errors"]:
                    error_msg += f"❌ {error}\n"
                return [TextContent(type="text", text=error_msg)]

            # Generate visualization
            try:
                df = self.db_manager.execute_query(
                    f"SELECT * FROM {viz_request.table_name}"
                )

                html_widget, insights = self.chart_generator.generate_chart(
                    viz_request.chart_type,
                    df,
                    column_mappings,
                    insights_requested,
                    title=f"{viz_request.chart_type.value.title()} Chart - {viz_request.table_name}",
                )

                viz_request.status = "completed"

                # Format response
                response = f"✅ **Chart Generated Successfully!**\n\n"
                response += f"**Chart Type:** {viz_request.chart_type.value.title()}\n"
                response += (
                    f"**Data Source:** {viz_request.table_name} ({len(df)} rows)\n"
                )
                response += (
                    f"**Columns Used:** {', '.join(column_mappings.values())}\n\n"
                )

                # Add insights if available
                if insights:
                    response += "## 📊 Statistical Insights\n\n"
                    response += self._format_insights(insights)
                    response += "\n\n"

                response += "## 📈 Interactive Chart\n\n"
                response += html_widget

                # Clean up request
                del self.active_requests[request_id]

                return [TextContent(type="text", text=response)]

            except Exception as e:
                viz_request.status = "error"
                viz_request.error_message = str(e)
                return [TextContent(type="text", text=f"Error generating chart: {e}")]

        except Exception as e:
            logger.error(f"Error configuring chart: {e}")
            return [TextContent(type="text", text=f"Error configuring chart: {e}")]

    def _format_insights(self, insights: Dict[str, Any]) -> str:
        """Format insights for display"""
        formatted = ""

        for key, value in insights.items():
            if key in ["correlations", "trends"]:
                continue

            if isinstance(value, dict) and "error" not in value:
                formatted += f"**{key}:**\n"
                for metric, metric_value in value.items():
                    if isinstance(metric_value, dict):
                        continue
                    formatted += f"  - {metric}: {metric_value}\n"
                formatted += "\n"

        # Handle correlations
        if (
            "correlations" in insights
            and "strong_correlations" in insights["correlations"]
        ):
            strong_corrs = insights["correlations"]["strong_correlations"]
            if strong_corrs:
                formatted += "**Strong Correlations:**\n"
                for corr in strong_corrs:
                    formatted += f"  - {corr['column1']} ↔ {corr['column2']}: {corr['correlation']} ({corr['strength']} {corr['direction']})\n"
                formatted += "\n"

        return formatted

    async def _handle_load_csv_data(self, arguments: dict) -> List[TextContent]:
        """Handle load_csv_data tool"""
        try:
            file_path = arguments["file_path"]
            table_name = arguments["table_name"]

            result = self.db_manager.load_csv(file_path, table_name)

            if result["success"]:
                table_info = result["table_info"]
                response = f"✅ **CSV Loaded Successfully**\n\n"
                response += f"**Table Name:** {table_name}\n"
                response += f"**File:** {file_path}\n"
                response += f"**Rows:** {table_info['row_count']}\n"
                response += f"**Columns:** {len(table_info['columns'])}\n\n"

                response += "**Column Types:**\n"
                for col in table_info["columns"]:
                    response += f"- {col['name']}: {col['type']}\n"

                response += f"\nUse `analyze_table` with '{table_name}' to explore the data further."

            else:
                response = f"❌ **Failed to Load CSV**\n\n"
                response += f"Error: {result['error']}"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return [TextContent(type="text", text=f"Error loading CSV: {e}")]

    async def _handle_query_data(self, arguments: dict) -> List[TextContent]:
        """Handle query_data tool"""
        try:
            sql_query = arguments["sql_query"]
            limit = arguments.get("limit", 100)

            # Add LIMIT if not present
            if "LIMIT" not in sql_query.upper():
                sql_query = f"{sql_query} LIMIT {limit}"

            df = self.db_manager.execute_query(sql_query)

            response = f"## Query Results\n\n"
            response += f"**Query:** `{sql_query}`\n"
            response += f"**Rows Returned:** {len(df)}\n\n"

            if not df.empty:
                response += "**Data:**\n```\n"
                response += df.to_string(index=False)
                response += "\n```"
            else:
                response += "No data returned."

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return [TextContent(type="text", text=f"Error executing query: {e}")]

    async def _handle_get_column_stats(self, arguments: dict) -> List[TextContent]:
        """Handle get_column_stats tool"""
        try:
            table_name = arguments["table_name"]
            column_name = arguments["column_name"]

            stats = self.db_manager.get_column_stats(table_name, column_name)

            if "error" in stats:
                return [TextContent(type="text", text=f"Error: {stats['error']}")]

            response = f"# Column Statistics: {table_name}.{column_name}\n\n"

            # Basic stats
            response += "## Basic Statistics\n"
            response += f"- **Total Count:** {stats.get('total_count', 'N/A')}\n"
            response += f"- **Non-null Count:** {stats.get('non_null_count', 'N/A')}\n"
            response += f"- **Null Count:** {stats.get('null_count', 'N/A')}\n"
            response += (
                f"- **Distinct Values:** {stats.get('distinct_count', 'N/A')}\n\n"
            )

            # Numeric stats if available
            if stats.get("min_value") is not None:
                response += "## Numeric Statistics\n"
                response += f"- **Minimum:** {stats.get('min_value')}\n"
                response += f"- **Maximum:** {stats.get('max_value')}\n"
                response += f"- **Mean:** {stats.get('mean_value')}\n"
                response += f"- **Median:** {stats.get('median_value')}\n"
                response += f"- **Standard Deviation:** {stats.get('std_value')}\n\n"

            # Top values
            if stats.get("top_values"):
                response += "## Most Common Values\n"
                for item in stats["top_values"][:10]:  # Top 10
                    response += f"- **{item['value']}:** {item['count']} occurrences\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting column stats: {e}")
            return [TextContent(type="text", text=f"Error getting column stats: {e}")]

    async def _handle_create_sample_chart(self, arguments: dict) -> List[TextContent]:
        """Handle create_sample_chart tool"""
        try:
            chart_type_str = arguments.get("chart_type", "bar")
            chart_type = ChartType(chart_type_str)

            html_widget = self.chart_generator.create_sample_chart(chart_type)

            response = f"📊 **Sample {chart_type.value.title()} Chart**\n\n"
            response += (
                "This is a sample chart with generated data for testing purposes.\n\n"
            )
            response += html_widget

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error creating sample chart: {e}")
            return [TextContent(type="text", text=f"Error creating sample chart: {e}")]

    async def _handle_validate_chart_config(self, arguments: dict) -> List[TextContent]:
        """Handle validate_chart_config tool"""
        try:
            chart_type = ChartType(arguments["chart_type"])
            table_name = arguments["table_name"]
            column_mappings = arguments["column_mappings"]

            columns = self.db_manager.get_columns(table_name)
            if not columns:
                return [
                    TextContent(type="text", text=f"Table '{table_name}' not found.")
                ]

            validation = chart_registry.validate_chart_configuration(
                chart_type, column_mappings, columns
            )

            if validation["valid"]:
                response = "✅ **Configuration Valid**\n\n"
                response += f"The column mappings are appropriate for a {chart_type.value} chart.\n"

                if validation.get("warnings"):
                    response += "\n⚠️ **Warnings:**\n"
                    for warning in validation["warnings"]:
                        response += f"- {warning}\n"
            else:
                response = "❌ **Configuration Invalid**\n\n"
                response += "**Errors:**\n"
                for error in validation["errors"]:
                    response += f"- {error}\n"

                if validation.get("missing_required"):
                    response += f"\n**Missing Required Fields:** {', '.join(validation['missing_required'])}\n"

                if validation.get("invalid_types"):
                    response += "\n**Type Mismatches:**\n"
                    for invalid in validation["invalid_types"]:
                        response += f"- {invalid['requirement']}: expected {'/'.join(invalid['expected'])}, got {invalid['actual']}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error validating chart config: {e}")
            return [
                TextContent(type="text", text=f"Error validating chart config: {e}")
            ]

    async def _handle_explain_chart_types(self, arguments: dict) -> List[TextContent]:
        """Handle explain_chart_types tool"""
        try:
            specific_type = arguments.get("chart_type")

            if specific_type:
                # Explain specific chart type
                chart_type = ChartType(specific_type)
                definition = chart_registry.get_chart_definition(chart_type)

                if not definition:
                    return [
                        TextContent(
                            type="text", text=f"Chart type '{specific_type}' not found."
                        )
                    ]

                response = f"# {definition.name}\n\n"
                response += f"**Description:** {definition.description}\n\n"

                response += "**Use Cases:**\n"
                for use_case in definition.use_cases:
                    response += f"- {use_case}\n"
                response += "\n"

                response += "**Requirements:**\n"
                for req in definition.column_requirements:
                    status = "Required" if req.required else "Optional"
                    response += f"- **{req.name}** ({status}): {req.description}\n"
                    response += f"  Data types: {', '.join(req.data_types)}\n"
                response += "\n"

                response += "**Supported Insights:**\n"
                insight_names = [
                    insight.value for insight in definition.supported_insights
                ]
                response += f"{', '.join(insight_names)}\n"

            else:
                # Explain all chart types
                response = "# Chart Types Guide\n\n"

                for chart_type in ChartType:
                    definition = chart_registry.get_chart_definition(chart_type)
                    if definition:
                        response += f"## {definition.name} (`{chart_type.value}`)\n"
                        response += f"{definition.description}\n\n"
                        response += (
                            f"**Best for:** {', '.join(definition.use_cases[:2])}\n\n"
                        )

                response += "Use `explain_chart_types` with a specific chart_type parameter to get detailed information about that chart type."

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error explaining chart types: {e}")
            return [TextContent(type="text", text=f"Error explaining chart types: {e}")]

    async def _handle_server_status(self, arguments: dict) -> List[TextContent]:
        """Handle server_status tool"""
        try:
            # Get component status
            db_status = "✅ Connected" if self.db_manager else "❌ Not initialized"
            llm_status = "❌ Not connected"

            if self.llm_client:
                llm_connected = await self.llm_client.check_connection()
                llm_status = "✅ Connected" if llm_connected else "⚠️ Connection issues"

            chart_status = "✅ Ready" if self.chart_generator else "❌ Not initialized"

            # Get database info
            tables = self.db_manager.get_tables() if self.db_manager else []
            active_requests = len(self.active_requests)

            response = "# Server Status\n\n"
            response += "## Component Status\n"
            response += f"- **Database:** {db_status}\n"
            response += f"- **LLM Client:** {llm_status}\n"
            response += f"- **Chart Generator:** {chart_status}\n\n"

            response += "## Database Information\n"
            response += f"- **Tables:** {len(tables)}\n"
            if tables:
                response += (
                    f"- **Table Names:** {', '.join([t['name'] for t in tables])}\n"
                )
            response += "\n"

            response += "## Active Requests\n"
            response += f"- **Pending Visualizations:** {active_requests}\n"

            if self.active_requests:
                response += "\n**Active Request Details:**\n"
                for req_id, req in self.active_requests.items():
                    response += f"- `{req_id}`: {req.chart_type.value} chart for {req.table_name} ({req.status})\n"

            # LLM model info
            if self.llm_client:
                try:
                    models = await self.llm_client.list_models()
                    if models:
                        response += f"\n## Available LLM Models\n"
                        response += f"- {', '.join(models[:5])}"  # Show first 5 models
                        if len(models) > 5:
                            response += f" and {len(models) - 5} more"
                except:
                    pass

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            return [TextContent(type="text", text=f"Error getting server status: {e}")]
