"""
Unified database interface for MCP visualization
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd


class DatabaseInterface(ABC):
    """Abstract base class for database managers"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection"""
        pass
    
    @abstractmethod
    def close(self):
        """Close database connection"""
        pass
    
    @abstractmethod
    def get_tables(self) -> List[Dict[str, Any]]:
        """Get list of available tables"""
        pass
    
    @abstractmethod
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, limit: int = 1000) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        pass
    
    @abstractmethod
    def get_sample_data(self, table_name: str, limit: int = 10) -> pd.DataFrame:
        """Get sample data from a table"""
        pass
    
    @abstractmethod
    def get_column_stats(self, table_name: str, column_name: str) -> Dict[str, Any]:
        """Get statistics for a specific column"""
        pass
    
    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information"""
        pass


class DatabaseFactory:
    """Factory for creating database managers"""
    
    @staticmethod
    def create_manager(db_type: str, **kwargs) -> DatabaseInterface:
        """Create appropriate database manager based on type"""
        
        if db_type.lower() == 'duckdb':
            from .manager import DatabaseManager
            return DatabaseManager(**kwargs)
        
        elif db_type.lower() == 'databricks':
            from ..databricks_integration.manager import DatabricksManager
            return DatabricksManager(**kwargs)
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def detect_database_type(connection_string: str = None, **kwargs) -> str:
        """Detect database type from connection parameters"""
        
        # Check for Databricks credentials
        try:
            from ..databricks_integration.credentials import DatabricksCredentialManager
            cred_manager = DatabricksCredentialManager()
            if cred_manager.load_credentials():
                return 'databricks'
        except:
            pass
        
        # Default to DuckDB
        return 'duckdb'