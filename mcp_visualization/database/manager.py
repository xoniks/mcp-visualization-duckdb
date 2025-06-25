"""
Database manager for DuckDB operations
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import duckdb
import pandas as pd

# Import the settings and config functions properly
from ..config.settings import (
    get_server_config,
    get_database_config,
    DatabaseConfig,
    SecurityConfig,
    DataConfig,
    DevelopmentConfig,
    InsightsConfig,
)

from ..utils.validators import validate_sql_query
from .queries import QueryBuilder

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        # SUCCESS FIXED: Get config properly using the convenience function
        server_config = get_server_config()
        self.config = server_config.database  # Access the database configuration
        self.security_config = server_config.security  # Add security config
        self.data_config = server_config.data  # Add data config

        # Ensure db_path is a Path object, using the default if not provided
        self.db_path = db_path if db_path else self.config.connection.path
        logger.info(f"Attempting to connect to database at: {self.db_path}")
        self._connect()

    def _connect(self):
        """Establish database connection"""
        try:
            print(f"DEBUG: Starting connection process", file=sys.stderr)
            print(f"DEBUG: Initial db_path = {self.db_path}", file=sys.stderr)
            print(f"DEBUG: db_path type = {type(self.db_path)}", file=sys.stderr)
            
            # Check if database path exists or if we should use in-memory database
            if self.db_path == ":memory:":
                print(f"DEBUG: Using in-memory database mode", file=sys.stderr)
                logger.info(f"Using in-memory database")
            else:
                db_path_obj = Path(self.db_path)
                print(f"DEBUG: Checking file existence for: {db_path_obj}", file=sys.stderr)
                print(f"DEBUG: File exists: {db_path_obj.exists()}", file=sys.stderr)
                
                if db_path_obj.exists():
                    print(f"DEBUG: File found, checking properties", file=sys.stderr)
                    stat_info = db_path_obj.stat()
                    print(f"DEBUG: File size: {stat_info.st_size} bytes", file=sys.stderr)
                    print(f"DEBUG: File is readable: {db_path_obj.is_file()}", file=sys.stderr)
                    logger.info(f"Connecting to DuckDB using path: '{self.db_path}'")
                else:
                    print(f"DEBUG: File not found, switching to in-memory", file=sys.stderr)
                    logger.warning(f"Database file not found at {self.db_path}, using in-memory database")
                    self.db_path = ":memory:"
            
            print(f"DEBUG: Final db_path for connection: {self.db_path}", file=sys.stderr)
            print(f"Attempting DuckDB connection to: {self.db_path}", file=sys.stderr)
            
            # Use a timeout mechanism for the connection
            import threading
            import queue
            import time
            
            def connect_with_timeout():
                print(f"DEBUG: Starting threaded connection attempt", file=sys.stderr)
                result_queue = queue.Queue()
                
                def do_connect():
                    try:
                        print(f"DEBUG: Inside connection thread", file=sys.stderr)
                        
                        # Prepare connection parameters
                        db_str = str(self.db_path)
                        read_only = self.config.connection.read_only if self.db_path != ":memory:" else False
                        
                        print(f"DEBUG: Connection parameters:", file=sys.stderr)
                        print(f"DEBUG:   database: {db_str}", file=sys.stderr)
                        print(f"DEBUG:   read_only: {read_only}", file=sys.stderr)
                        print(f"DEBUG:   memory_limit: {self.config.settings.memory_limit}", file=sys.stderr)
                        print(f"DEBUG:   threads: {self.config.settings.threads}", file=sys.stderr)
                        print(f"DEBUG:   enable_extensions: {self.config.settings.enable_extensions}", file=sys.stderr)
                        
                        print(f"DEBUG: About to call duckdb.connect()", file=sys.stderr)
                        
                        conn = duckdb.connect(
                            database=db_str,
                            read_only=read_only,
                            config={
                                "memory_limit": self.config.settings.memory_limit,
                                "threads": self.config.settings.threads,
                                "enable_external_access": self.config.settings.enable_extensions,
                            },
                        )
                        
                        print(f"DEBUG: duckdb.connect() completed successfully", file=sys.stderr)
                        result_queue.put(('success', conn))
                        
                    except Exception as e:
                        print(f"DEBUG: Exception in connection thread: {type(e).__name__}: {e}", file=sys.stderr)
                        import traceback
                        traceback.print_exc(file=sys.stderr)
                        result_queue.put(('error', str(e)))
                
                print(f"DEBUG: Creating and starting connection thread", file=sys.stderr)
                thread = threading.Thread(target=do_connect, daemon=True)
                thread.start()
                
                # Wait for result with timeout
                timeout_seconds = 15  # Increased timeout to 15 seconds
                print(f"DEBUG: Waiting for connection result (timeout: {timeout_seconds}s)", file=sys.stderr)
                
                try:
                    result_type, result = result_queue.get(timeout=timeout_seconds)
                    print(f"DEBUG: Got result from queue: {result_type}", file=sys.stderr)
                    
                    if result_type == 'success':
                        print(f"DEBUG: Connection successful, returning connection object", file=sys.stderr)
                        return result
                    else:
                        print(f"DEBUG: Connection failed with error: {result}", file=sys.stderr)
                        raise Exception(f"Connection failed: {result}")
                        
                except queue.Empty:
                    print(f"DEBUG: Connection timed out after {timeout_seconds} seconds", file=sys.stderr)
                    raise Exception(f"Connection timed out after {timeout_seconds} seconds")
            
            self.connection = connect_with_timeout()
            print(f"DuckDB connection established successfully", file=sys.stderr)
            logger.info(f"Successfully connected to DuckDB at: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get database connection"""
        if self.connection is None:
            self._connect()
        return self.connection

    def execute_query(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        try:
            # Validate SQL query for security
            if not validate_sql_query(sql, self.security_config):
                raise ValueError("SQL query contains forbidden keywords or patterns")

            logger.debug(f"Executing query: {sql}")

            if params:
                result = self.connection.execute(sql, params).df()
            else:
                result = self.connection.execute(sql).df()

            logger.debug(f"Query returned {len(result)} rows")
            return result

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {sql}")
            raise

    def get_tables(self) -> List[Dict[str, str]]:
        """Get list of available tables with metadata"""
        try:
            result = self.connection.execute(
                """
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'main'
                ORDER BY table_name
                """
            ).fetchall()

            return [{"name": row[0], "type": row[1]} for row in result]

        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            return []

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed table information"""
        try:
            # Get column information
            columns = self.get_columns(table_name)

            # Get row count
            row_count_result = self.connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()
            row_count = row_count_result[0] if row_count_result else 0

            # Get sample data
            sample_data = self.connection.execute(
                f"SELECT * FROM {table_name} LIMIT 5"
            ).df()

            return {
                "name": table_name,
                "columns": columns,
                "row_count": row_count,
                "sample_data": sample_data.to_dict("records"),
            }

        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {"name": table_name, "error": str(e)}

    def get_columns(self, table_name: str) -> List[Dict[str, str]]:
        """Get column information for a table"""
        try:
            result = self.connection.execute(f"DESCRIBE {table_name}").fetchall()
            return [
                {
                    "name": row[0],
                    "type": row[1],
                    "nullable": row[2] if len(row) > 2 else "YES",
                }
                for row in result
            ]

        except Exception as e:
            logger.error(f"Error getting columns for {table_name}: {e}")
            return []

    def get_column_stats(self, table_name: str, column_name: str) -> Dict[str, Any]:
        """Get statistical information for a column"""
        try:
            # Check if column is numeric
            columns = self.get_columns(table_name)
            column_info = next(
                (col for col in columns if col["name"] == column_name), None
            )

            if not column_info:
                return {"error": f"Column {column_name} not found"}

            column_type = column_info["type"].upper()
            is_numeric = any(
                t in column_type
                for t in ["INTEGER", "BIGINT", "DOUBLE", "FLOAT", "DECIMAL", "NUMERIC"]
            )

            stats = {}

            # Basic stats for all columns
            basic_stats = self.connection.execute(
                f"""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT({column_name}) as non_null_count,
                    COUNT(DISTINCT {column_name}) as distinct_count
                FROM {table_name}
            """
            ).fetchone()

            stats.update(
                {
                    "total_count": basic_stats[0],
                    "non_null_count": basic_stats[1],
                    "distinct_count": basic_stats[2],
                    "null_count": basic_stats[0] - basic_stats[1],
                }
            )

            # Numeric stats
            if is_numeric:
                numeric_stats = self.connection.execute(
                    f"""
                    SELECT 
                        MIN({column_name}) as min_value,
                        MAX({column_name}) as max_value,
                        AVG({column_name}) as mean_value,
                        MEDIAN({column_name}) as median_value,
                        STDDEV({column_name}) as std_value
                    FROM {table_name}
                    WHERE {column_name} IS NOT NULL
                """
                ).fetchone()

                stats.update(
                    {
                        "min_value": numeric_stats[0],
                        "max_value": numeric_stats[1],
                        "mean_value": numeric_stats[2],
                        "median_value": numeric_stats[3],
                        "std_value": numeric_stats[4],
                    }
                )

            # Top values
            top_values = self.connection.execute(
                f"""
                SELECT {column_name}, COUNT(*) as count
                FROM {table_name}
                WHERE {column_name} IS NOT NULL
                GROUP BY {column_name}
                ORDER BY count DESC
                LIMIT 10
            """
            ).fetchall()

            stats["top_values"] = [
                {"value": row[0], "count": row[1]} for row in top_values
            ]

            return stats

        except Exception as e:
            logger.error(
                f"Error getting column stats for {table_name}.{column_name}: {e}"
            )
            return {"error": str(e)}

    def load_csv(self, file_path: str, table_name: str, **kwargs) -> Dict[str, Any]:
        """Load CSV file into database"""
        try:
            # Validate file path
            file_path_obj = Path(file_path).resolve()
            if not any(
                str(file_path_obj).startswith(str(Path(p).resolve()))
                for p in self.security_config.file_access.allowed_paths
            ):
                raise ValueError(f"File path not allowed: {file_path}")

            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Load CSV with auto-detection
            self.connection.execute(
                f"""
                CREATE TABLE {table_name} AS 
                SELECT * FROM read_csv_auto('{file_path_obj}')
            """
            )

            # Get table info
            table_info = self.get_table_info(table_name)

            logger.info(f"Successfully loaded {file_path} as table '{table_name}'")
            logger.info(
                f"Table has {table_info['row_count']} rows and {len(table_info['columns'])} columns"
            )

            return {
                "success": True,
                "table_name": table_name,
                "file_path": str(file_path_obj),
                "table_info": table_info,
            }

        except Exception as e:
            logger.error(f"Error loading CSV {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": (
                    str(file_path_obj) if "file_path_obj" in locals() else None
                ),
            }

    def create_view(self, view_name: str, sql: str) -> bool:
        """Create a view from SQL query"""
        try:
            # Validate SQL
            if not validate_sql_query(sql, self.security_config):
                raise ValueError("SQL query contains forbidden keywords or patterns")

            self.connection.execute(f"CREATE VIEW {view_name} AS {sql}")
            logger.info(f"Created view: {view_name}")
            return True

        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False

    def drop_table(self, table_name: str) -> bool:
        """Drop a table (if allowed)"""
        try:
            if "DROP" not in self.security_config.allowed_sql_keywords:
                logger.warning(f"DROP operations not allowed")
                return False

            self.connection.execute(f"DROP TABLE IF EXISTS {table_name}")
            logger.info(f"Dropped table: {table_name}")
            return True

        except Exception as e:
            logger.error(f"Error dropping table {table_name}: {e}")
            return False

    def analyze_data_for_visualization(self, table_name: str) -> Dict[str, Any]:
        """Analyze data to suggest visualization types"""
        try:
            columns = self.get_columns(table_name)
            analysis = {
                "table_name": table_name,
                "columns": columns,
                "column_analysis": {},
                "suggested_charts": [],
            }

            # Analyze each column
            for col in columns:
                col_name = col["name"]
                col_type = col["type"].upper()

                col_analysis = {
                    "type": col_type,
                    "is_numeric": any(
                        t in col_type
                        for t in ["INTEGER", "BIGINT", "DOUBLE", "FLOAT", "DECIMAL"]
                    ),
                    "is_temporal": any(
                        t in col_type for t in ["DATE", "TIMESTAMP", "TIME"]
                    ),
                    "is_categorical": "VARCHAR" in col_type or "TEXT" in col_type,
                }

                # Get basic stats
                stats = self.get_column_stats(table_name, col_name)
                col_analysis.update(stats)

                analysis["column_analysis"][col_name] = col_analysis

            # Suggest chart types based on data
            analysis["suggested_charts"] = self._suggest_chart_types(
                analysis["column_analysis"]
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing data for {table_name}: {e}")
            return {"error": str(e)}

    def _suggest_chart_types(
        self, column_analysis: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Suggest appropriate chart types based on column analysis"""
        suggestions = []

        numeric_cols = [
            name for name, info in column_analysis.items() if info.get("is_numeric")
        ]
        categorical_cols = [
            name for name, info in column_analysis.items() if info.get("is_categorical")
        ]
        temporal_cols = [
            name for name, info in column_analysis.items() if info.get("is_temporal")
        ]

        # Bar chart suggestions
        if categorical_cols and numeric_cols:
            suggestions.append(
                {
                    "chart_type": "bar",
                    "description": "Compare values across categories",
                    "x_suggestions": categorical_cols,
                    "y_suggestions": numeric_cols,
                }
            )

        # Line chart suggestions
        if temporal_cols and numeric_cols:
            suggestions.append(
                {
                    "chart_type": "line",
                    "description": "Show trends over time",
                    "x_suggestions": temporal_cols,
                    "y_suggestions": numeric_cols,
                }
            )

        # Scatter plot suggestions
        if len(numeric_cols) >= 2:
            suggestions.append(
                {
                    "chart_type": "scatter",
                    "description": "Show relationships between numeric variables",
                    "x_suggestions": numeric_cols,
                    "y_suggestions": numeric_cols,
                }
            )

        # Pie chart suggestions
        if categorical_cols:
            # Find categorical columns with reasonable distinct counts
            pie_candidates = [
                name
                for name in categorical_cols
                if column_analysis[name].get("distinct_count", 0) <= 10
            ]
            if pie_candidates:
                suggestions.append(
                    {
                        "chart_type": "pie",
                        "description": "Show proportions of categories",
                        "category_suggestions": pie_candidates,
                    }
                )

        # Histogram suggestions
        if numeric_cols:
            suggestions.append(
                {
                    "chart_type": "histogram",
                    "description": "Show distribution of numeric values",
                    "column_suggestions": numeric_cols,
                }
            )

        return suggestions

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
