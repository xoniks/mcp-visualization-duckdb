"""
Databricks database manager for MCP visualization
"""

import logging
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import sys

from ..database.interface import DatabaseInterface

logger = logging.getLogger(__name__)


class DatabricksManager(DatabaseInterface):
    """Database manager for Databricks SQL warehouses"""
    
    def __init__(self, server_hostname: str = None, http_path: str = None, access_token: str = None):
        self.server_hostname = server_hostname
        self.http_path = http_path
        self.access_token = access_token
        self.connection = None
        self.current_catalog = "main"
        self.current_schema = "default"
        
        # Load credentials if not provided
        if not all([server_hostname, http_path, access_token]):
            self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from secure storage"""
        try:
            from .credentials import DatabricksCredentialManager
            cred_manager = DatabricksCredentialManager()
            creds = cred_manager.load_credentials()
            
            if creds:
                self.server_hostname = creds.get("server_hostname")
                self.http_path = creds.get("http_path")
                self.access_token = creds.get("token")
                logger.info("Databricks credentials loaded successfully")
            else:
                logger.warning("No Databricks credentials found")
                
        except Exception as e:
            logger.error(f"Failed to load Databricks credentials: {e}")
    
    def connect(self) -> bool:
        """Establish connection to Databricks"""
        try:
            if not all([self.server_hostname, self.http_path, self.access_token]):
                logger.error("Missing Databricks connection parameters")
                return False
            
            from databricks import sql
            
            logger.info(f"Connecting to Databricks: {self.server_hostname}")
            print(f"DEBUG: Connecting to Databricks: {self.server_hostname}", file=sys.stderr)
            
            self.connection = sql.connect(
                server_hostname=self.server_hostname,
                http_path=self.http_path,
                access_token=self.access_token,
                catalog=self.current_catalog,
                schema=self.current_schema
            )
            
            # Test connection
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT current_catalog(), current_schema()")
                result = cursor.fetchone()
                self.current_catalog = result[0] if result[0] else "main"
                self.current_schema = result[1] if result[1] else "default"
            
            logger.info(f"Connected to Databricks catalog: {self.current_catalog}, schema: {self.current_schema}")
            print(f"SUCCESS: Connected to Databricks catalog: {self.current_catalog}, schema: {self.current_schema}", file=sys.stderr)
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Databricks: {e}")
            print(f"ERROR: Failed to connect to Databricks: {e}", file=sys.stderr)
            return False
    
    def close(self):
        """Close Databricks connection"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                logger.info("Databricks connection closed")
        except Exception as e:
            logger.error(f"Error closing Databricks connection: {e}")
    
    def get_catalogs(self) -> List[Dict[str, Any]]:
        """Get list of available catalogs"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW CATALOGS")
                results = cursor.fetchall()
                
                catalogs = []
                for row in results:
                    catalogs.append({
                        "name": row[0],
                        "type": "catalog"
                    })
                
                logger.info(f"Found {len(catalogs)} catalogs")
                return catalogs
                
        except Exception as e:
            logger.error(f"Failed to get catalogs: {e}")
            return []
    
    def get_schemas(self, catalog: str = None) -> List[Dict[str, Any]]:
        """Get list of available schemas in a catalog"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            catalog = catalog or self.current_catalog
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"SHOW SCHEMAS IN {catalog}")
                results = cursor.fetchall()
                
                schemas = []
                for row in results:
                    schemas.append({
                        "name": row[0],
                        "catalog": catalog,
                        "type": "schema"
                    })
                
                logger.info(f"Found {len(schemas)} schemas in catalog {catalog}")
                return schemas
                
        except Exception as e:
            logger.error(f"Failed to get schemas: {e}")
            return []
    
    def get_tables(self, catalog: str = None, schema: str = None) -> List[Dict[str, Any]]:
        """Get list of available tables"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            catalog = catalog or self.current_catalog
            schema = schema or self.current_schema
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"SHOW TABLES IN {catalog}.{schema}")
                results = cursor.fetchall()
                
                tables = []
                for row in results:
                    table_name = row[1]  # Table name is usually in second column
                    tables.append({
                        "name": table_name,
                        "catalog": catalog,
                        "schema": schema,
                        "full_name": f"{catalog}.{schema}.{table_name}",
                        "type": "table"
                    })
                
                logger.info(f"Found {len(tables)} tables in {catalog}.{schema}")
                return tables
                
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            return []
    
    def get_table_info(self, table_name: str, catalog: str = None, schema: str = None) -> Dict[str, Any]:
        """Get detailed information about a table"""
        try:
            if not self.connection:
                if not self.connect():
                    return {}
            
            catalog = catalog or self.current_catalog
            schema = schema or self.current_schema
            full_table_name = f"{catalog}.{schema}.{table_name}"
            
            with self.connection.cursor() as cursor:
                # Get table description
                cursor.execute(f"DESCRIBE TABLE {full_table_name}")
                columns_info = cursor.fetchall()
                
                columns = []
                for row in columns_info:
                    columns.append({
                        "name": row[0],
                        "type": row[1],
                        "nullable": "YES" if row[2] and "NOT NULL" not in str(row[2]) else "NO"
                    })
                
                # Get row count
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {full_table_name}")
                    row_count = cursor.fetchone()[0]
                except:
                    row_count = "Unknown"
                
                table_info = {
                    "name": table_name,
                    "catalog": catalog,
                    "schema": schema,
                    "full_name": full_table_name,
                    "columns": columns,
                    "row_count": row_count,
                    "type": "table"
                }
                
                logger.info(f"Retrieved info for table {full_table_name}")
                return table_info
                
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            return {}
    
    def execute_query(self, query: str, limit: int = 1000) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:
            if not self.connection:
                if not self.connect():
                    return pd.DataFrame()
            
            # Add LIMIT if not present and limit is specified
            if limit and "LIMIT" not in query.upper():
                query = f"{query.rstrip(';')} LIMIT {limit}"
            
            logger.info(f"Executing query: {query[:100]}...")
            print(f"DEBUG: Executing Databricks query: {query[:100]}...", file=sys.stderr)
            
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                
                # Fetch results
                results = cursor.fetchall()
                
                # Convert to DataFrame
                df = pd.DataFrame(results, columns=columns)
                
                logger.info(f"Query executed successfully, returned {len(df)} rows")
                print(f"SUCCESS: Query returned {len(df)} rows", file=sys.stderr)
                return df
                
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            print(f"ERROR: Query execution failed: {e}", file=sys.stderr)
            return pd.DataFrame()
    
    def get_sample_data(self, table_name: str, limit: int = 10, catalog: str = None, schema: str = None) -> pd.DataFrame:
        """Get sample data from a table"""
        try:
            catalog = catalog or self.current_catalog
            schema = schema or self.current_schema
            full_table_name = f"{catalog}.{schema}.{table_name}"
            
            query = f"SELECT * FROM {full_table_name} LIMIT {limit}"
            return self.execute_query(query, limit=None)  # Don't double-limit
            
        except Exception as e:
            logger.error(f"Failed to get sample data from {table_name}: {e}")
            return pd.DataFrame()
    
    def get_column_stats(self, table_name: str, column_name: str, catalog: str = None, schema: str = None) -> Dict[str, Any]:
        """Get statistics for a specific column"""
        try:
            catalog = catalog or self.current_catalog
            schema = schema or self.current_schema
            full_table_name = f"{catalog}.{schema}.{table_name}"
            
            # Get basic stats
            stats_query = f"""
            SELECT 
                COUNT(*) as total_count,
                COUNT({column_name}) as non_null_count,
                COUNT(DISTINCT {column_name}) as distinct_count,
                MIN({column_name}) as min_value,
                MAX({column_name}) as max_value
            FROM {full_table_name}
            """
            
            stats_df = self.execute_query(stats_query, limit=None)
            
            if stats_df.empty:
                return {}
            
            stats = stats_df.iloc[0].to_dict()
            
            # Calculate null percentage
            stats["null_count"] = stats["total_count"] - stats["non_null_count"]
            stats["null_percentage"] = (stats["null_count"] / stats["total_count"]) * 100 if stats["total_count"] > 0 else 0
            
            logger.info(f"Retrieved column stats for {column_name} in {full_table_name}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get column stats for {column_name}: {e}")
            return {}
    
    def switch_catalog_schema(self, catalog: str, schema: str = "default") -> bool:
        """Switch to a different catalog and schema"""
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"USE CATALOG {catalog}")
                cursor.execute(f"USE SCHEMA {schema}")
            
            self.current_catalog = catalog
            self.current_schema = schema
            
            logger.info(f"Switched to catalog: {catalog}, schema: {schema}")
            print(f"SUCCESS: Switched to catalog: {catalog}, schema: {schema}", file=sys.stderr)
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch catalog/schema: {e}")
            print(f"ERROR: Failed to switch catalog/schema: {e}", file=sys.stderr)
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information"""
        return {
            "type": "databricks",
            "server_hostname": self.server_hostname,
            "http_path": self.http_path,
            "current_catalog": self.current_catalog,
            "current_schema": self.current_schema,
            "connected": self.connection is not None
        }