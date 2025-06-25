# code/mcp_server/server.py

import asyncio
import logging
import uuid
from pathlib import Path  # ✅ ADDED: Missing Path import
from typing import Dict, List, Any, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
    ServerCapabilities,
    ToolsCapability,
)  # ✅ FIXED: Correct import name

# Import the config_manager and the specific config types for type hinting
from ..config.settings import config_manager, ServerConfig, DevelopmentConfig, Settings
from ..database.manager import DatabaseManager
from ..llm.simple_fallback import SimpleFallbackClient
from ..visualization.chart_generator import ChartGenerator
from ..visualization.chart_types import ChartType, InsightType, chart_registry
from ..utils.logger import setup_logging
from .tools import ToolRegistry
from .handlers import RequestHandler
from .types import VisualizationRequest

logger = logging.getLogger(__name__)


class DataVisualizationMCPServer:
    """Main MCP server for data visualization"""

    def __init__(self):
        # ✅ Load the full settings object from the global config_manager
        self.settings: Settings = config_manager.get_settings()
        # ✅ Access specific config sections from the settings object
        self.server_config: ServerConfig = self.settings.server
        self.dev_config: DevelopmentConfig = self.settings.development

        # Initialize MCP server
        self.server = Server(self.server_config.name)  # Use the loaded config

        # Initialize components (these will now implicitly use config_manager internally)
        self.db_manager: Optional[DatabaseManager] = None
        self.llm_client: Optional[SimpleFallbackClient] = None
        self.chart_generator: Optional[ChartGenerator] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self.request_handler: Optional[RequestHandler] = None

        # Active requests tracking
        self.active_requests: Dict[str, VisualizationRequest] = {}

        # Setup logging - use the log_level from the loaded config
        setup_logging(self.server_config.log_level)

        # Register MCP handlers
        self._register_mcp_handlers()

        logger.info(
            f"Initialized MCP server: {self.server_config.name} v{self.server_config.version}"
        )

    async def initialize(self):
        """Initialize server components"""
        try:
            # Initialize database manager (it will get config from config_manager itself)
            self.db_manager = DatabaseManager()
            logger.info("Database manager initialized")

            # Initialize simple fallback client (no external LLM needed)
            self.llm_client = SimpleFallbackClient()
            
            # Check connection (always succeeds for fallback)
            fallback_ready = await self.llm_client.check_connection()
            logger.info("Using rule-based fallback for chart analysis (no external LLM required)")

            # Initialize chart generator (it will get config from config_manager itself)
            self.chart_generator = ChartGenerator()
            logger.info("Chart generator initialized")

            # Initialize tool registry and request handler
            self.tool_registry = ToolRegistry(
                self.db_manager, self.llm_client, self.chart_generator
            )
            self.request_handler = RequestHandler(
                self.db_manager,
                self.llm_client,
                self.chart_generator,
                self.active_requests,
            )

            # Load sample data if enabled in development config
            # ✅ Access the nested generate_on_startup attribute
            if self.settings.development.sample_data.generate_on_startup:
                await self._load_sample_data()

            logger.info("MCP server initialization completed")

            # --- START: Consolidated status prints ---
            print("\n" + "=" * 60)
            print("MCP Data Visualization Server is ready!")
            print(
                f"🗃️ Database: {self.db_manager.db_path if self.db_manager and hasattr(self.db_manager, 'db_path') else 'Not initialized'}"
            )
            print(
                f"🧠 LLM: Rule-based chart analysis (no external LLM needed)"
            )
            print(f"📈 Charts: Plotly HTML widgets")
            # ✅ Access the nested generate_on_startup attribute
            if self.settings.development.sample_data.generate_on_startup:
                print("🎲 Sample data generated and loaded")
            print("Connect your MCP client to start visualizing data")
            print("=" * 60 + "\n")
            # --- END: Consolidated status prints ---

        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise  # Re-raise to main for consistent exit handling

    def _register_mcp_handlers(self):
        """Register MCP protocol handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            if not self.tool_registry:
                return []
            return await self.tool_registry.list_tools()

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Handle tool calls"""
            if not self.request_handler:
                return [TextContent(type="text", text="Server not initialized")]
            return await self.request_handler.handle_tool_call(name, arguments)

        @self.server.list_resources()
        async def handle_list_resources():
            """List available resources"""
            return []

        @self.server.read_resource()
        async def handle_read_resource(uri: str):
            """Read resource content"""
            return TextContent(type="text", text="Resource reading not implemented")

    async def _load_sample_data(self):
        """Load sample data for development"""
        try:
            logger.info("Loading sample data...")

            import pandas as pd
            import numpy as np
            from datetime import datetime, timedelta

            np.random.seed(42)

            # Loop through configured sample datasets
            # ✅ Access the datasets from the settings object
            for dataset_config in self.settings.development.sample_data.datasets:
                file_path = dataset_config.file
                table_name = dataset_config.name

                # ✅ FIXED: Ensure Path object is used correctly
                file_path_obj = Path(file_path)
                file_path_obj.parent.mkdir(parents=True, exist_ok=True)

                # Generate DataFrame based on table_name as per your original logic
                df_to_load = None
                if table_name == "sales":
                    start_date = datetime(2023, 1, 1)
                    dates = [start_date + timedelta(days=i) for i in range(365)]
                    regions = ["North", "South", "East", "West"]
                    products = ["Product A", "Product B", "Product C", "Product D"]
                    sales_data = []
                    for i, date in enumerate(dates):
                        for region in regions:
                            for product in products:
                                sales_data.append(
                                    {
                                        "date": date.strftime("%Y-%m-%d"),
                                        "region": region,
                                        "product": product,
                                        "sales_amount": np.random.normal(1000, 200),
                                        "quantity": np.random.poisson(50),
                                        "customer_count": np.random.poisson(25),
                                    }
                                )
                    df_to_load = pd.DataFrame(sales_data)
                elif table_name == "customers":
                    regions = ["North", "South", "East", "West"]
                    customer_data = []
                    for i in range(1000):
                        customer_data.append(
                            {
                                "customer_id": f"C{i+1:04d}",
                                "age": np.random.randint(18, 80),
                                "gender": np.random.choice(["M", "F"]),
                                "segment": np.random.choice(
                                    ["Premium", "Standard", "Basic"]
                                ),
                                "lifetime_value": np.random.exponential(2000),
                                "region": np.random.choice(regions),
                            }
                        )
                    df_to_load = pd.DataFrame(customer_data)
                elif table_name == "products":
                    # ✅ ADDED: Products sample data generation
                    categories = ["Electronics", "Clothing", "Home", "Sports"]
                    products_data = []
                    for i in range(100):
                        products_data.append(
                            {
                                "product_id": f"P{i+1:04d}",
                                "product_name": f"Product {i+1}",
                                "category": np.random.choice(categories),
                                "price": np.random.uniform(10, 1000),
                                "cost": np.random.uniform(5, 500),
                                "weight": np.random.uniform(0.1, 10),
                                "rating": np.random.uniform(1, 5),
                            }
                        )
                    df_to_load = pd.DataFrame(products_data)

                if df_to_load is not None:
                    # Save to CSV (optional, if you want to persist the generated data)
                    df_to_load.to_csv(file_path_obj, index=False)
                    # Then load into the database using db_manager.load_csv
                    result = self.db_manager.load_csv(
                        str(file_path_obj), table_name
                    )  # Convert Path to str
                    if result["success"]:
                        logger.info(
                            f"Loaded {table_name} data: {result['table_info']['row_count']} rows"
                        )
                    else:
                        logger.error(
                            f"Failed to load {table_name} from CSV: {result.get('error', 'Unknown error')}"
                        )
                else:
                    logger.warning(
                        f"No generation logic for sample dataset '{table_name}'. Skipping."
                    )

            logger.info("Sample data loading completed")

        except Exception as e:
            logger.error(f"Error loading sample data: {e}")

    async def run(self, transport: str = "stdio"):
        """Run the MCP server"""
        try:
            await self.initialize()

            if transport == "stdio":
                from mcp.server.stdio import stdio_server

                logger.info("Starting MCP server with STDIO transport")
                print(f"🚀 Starting MCP server...")
                print(f"📊 Transport: {transport}")
                async with stdio_server() as (read_stream, write_stream):
                    # ✅ FIXED: Added required capabilities
                    await self.server.run(
                        read_stream,
                        write_stream,
                        InitializationOptions(
                            server_name=self.server_config.name,
                            server_version=self.server_config.version,
                            capabilities=ServerCapabilities(tools=ToolsCapability()),
                        ),
                    )
            else:
                raise ValueError(f"Unsupported transport: {transport}")

        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up server resources"""
        try:
            if self.llm_client:
                await self.llm_client.close()

            if self.db_manager:
                # db_manager.close() is sync, so direct call is fine
                self.db_manager.close()

            logger.info("Server cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"req_{uuid.uuid4().hex[:8]}"

    def get_active_request(self, request_id: str) -> Optional[VisualizationRequest]:
        """Get active request by ID"""
        return self.active_requests.get(request_id)

    def add_active_request(self, request: VisualizationRequest):
        """Add request to active requests"""
        self.active_requests[request.id] = request

    def remove_active_request(self, request_id: str):
        """Remove request from active requests"""
        if request_id in self.active_requests:
            del self.active_requests[request_id]

    def get_server_status(self) -> Dict[str, Any]:
        """Get server status information"""
        return {
            "name": self.server_config.name,
            "version": self.server_config.version,
            "active_requests": len(self.active_requests),
            "database_connected": self.db_manager is not None,
            "llm_connected": self.llm_client is not None,
            "components_initialized": all(
                [
                    self.db_manager,
                    self.llm_client,
                    self.chart_generator,
                    self.tool_registry,
                    self.request_handler,
                ]
            ),
        }


# Convenience function for running the server (kept for main.py's __name__ == "__main__")
async def run_server():
    """Run the MCP server"""
    server = DataVisualizationMCPServer()
    await server.run()
