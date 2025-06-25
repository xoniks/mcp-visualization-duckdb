"""
Claude Desktop configuration manager for automatic MCP server setup
"""

import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ClaudeDesktopConfigManager:
    """Manages Claude Desktop configuration for MCP server integration"""

    def __init__(self):
        self.platform = platform.system()
        self.config_path = self._find_claude_config_path()
        
    def _find_claude_config_path(self) -> Path:
        """Find Claude Desktop config file based on platform"""
        config_paths = {
            'Windows': Path.home() / 'AppData/Roaming/Claude/claude_desktop_config.json',
            'Darwin': Path.home() / 'Library/Application Support/Claude/claude_desktop_config.json',
            'Linux': Path.home() / '.config/claude/claude_desktop_config.json'
        }
        
        if self.platform not in config_paths:
            raise RuntimeError(f"Unsupported platform: {self.platform}")
            
        return config_paths[self.platform]
    
    def config_exists(self) -> bool:
        """Check if Claude Desktop config file exists"""
        return self.config_path.exists()
    
    def create_config_directory(self) -> None:
        """Create Claude Desktop config directory if it doesn't exist"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {self.config_path.parent}")
    
    def load_existing_config(self) -> Dict[str, Any]:
        """Load existing Claude Desktop configuration"""
        if not self.config_exists():
            return {"mcpServers": {}}
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Ensure mcpServers section exists
            if "mcpServers" not in config:
                config["mcpServers"] = {}
                
            return config
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Error reading existing config: {e}")
            return {"mcpServers": {}}
    
    def backup_config(self) -> Optional[Path]:
        """Create backup of existing configuration"""
        if not self.config_exists():
            return None
            
        backup_path = self.config_path.with_suffix('.json.backup')
        shutil.copy2(self.config_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    
    def get_python_executable(self) -> str:
        """Get current Python executable path"""
        return sys.executable
    
    def get_package_path(self) -> Path:
        """Get installed package location"""
        import mcp_visualization
        return Path(mcp_visualization.__file__).parent
    
    def get_default_database_path(self) -> Path:
        """Get default database path in user's home directory"""
        return Path.home() / '.mcp-visualization' / 'data.duckdb'
    
    def get_suggested_database_paths(self) -> list[Path]:
        """Get suggested database locations for user to choose from"""
        suggestions = [
            self.get_default_database_path(),
            Path.home() / 'Documents' / 'mcp-viz.duckdb',
            Path.home() / 'Desktop' / 'data.duckdb',
            Path.cwd() / 'data.duckdb',
        ]
        return suggestions
    
    def create_server_config(self, 
                           server_name: str = "data-viz-server",
                           database_path: Optional[Path] = None,
                           python_path: Optional[str] = None,
                           create_sample_db: bool = True) -> Dict[str, Any]:
        """Create MCP server configuration for Claude Desktop"""
        
        if python_path is None:
            python_path = self.get_python_executable()
        
        # Convert paths to strings for JSON serialization
        # Use forward slashes even on Windows for consistency
        python_str = str(Path(python_path)).replace('\\', '/')
        package_path = str(self.get_package_path().parent).replace('\\', '/')
        
        config = {
            "command": python_str,
            "args": ["-m", "mcp_visualization.server"],
            "cwd": package_path,
        }
        
        # Only add database path if specified
        if database_path is not None:
            # Ensure database directory exists
            database_path.parent.mkdir(parents=True, exist_ok=True)
            db_str = str(database_path).replace('\\', '/')
            config["env"] = {
                "DUCKDB_DATABASE_PATH": db_str
            }
            logger.debug(f"Database: {db_str}")
            
            # Create sample database if requested
            if create_sample_db:
                try:
                    from .database import create_sample_database
                    create_sample_database(str(database_path))
                    logger.info(f"Created sample database at {database_path}")
                except Exception as e:
                    logger.warning(f"Could not create sample database: {e}")
        else:
            logger.info("No default database - users can connect to any database via Claude Desktop")
        
        logger.info(f"Created server config for {server_name}")
        logger.debug(f"Python: {python_str}")
        logger.debug(f"Working dir: {package_path}")
        
        return config
    
    def add_mcp_server(self, 
                      server_name: str = "data-viz-server",
                      database_path: Optional[Path] = None,
                      python_path: Optional[str] = None,
                      backup: bool = True) -> Tuple[bool, str]:
        """
        Add MCP server to Claude Desktop configuration
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create config directory if needed
            self.create_config_directory()
            
            # Backup existing config
            if backup and self.config_exists():
                self.backup_config()
            
            # Load existing configuration
            config = self.load_existing_config()
            
            # Check if server already exists
            if server_name in config["mcpServers"]:
                return False, f"Server '{server_name}' already exists in configuration"
            
            # Create server configuration
            server_config = self.create_server_config(
                server_name=server_name,
                database_path=database_path,
                python_path=python_path
            )
            
            # Add server to configuration
            config["mcpServers"][server_name] = server_config
            
            # Write updated configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully added '{server_name}' to Claude Desktop configuration")
            return True, f"Successfully configured '{server_name}' for Claude Desktop"
            
        except Exception as e:
            error_msg = f"Failed to configure Claude Desktop: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def remove_mcp_server(self, server_name: str = "data-viz-server") -> Tuple[bool, str]:
        """Remove MCP server from Claude Desktop configuration"""
        try:
            if not self.config_exists():
                return False, "Claude Desktop configuration file not found"
            
            config = self.load_existing_config()
            
            if server_name not in config["mcpServers"]:
                return False, f"Server '{server_name}' not found in configuration"
            
            # Backup before removal
            self.backup_config()
            
            # Remove server
            del config["mcpServers"][server_name]
            
            # Write updated configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully removed '{server_name}' from Claude Desktop configuration")
            return True, f"Successfully removed '{server_name}' from Claude Desktop"
            
        except Exception as e:
            error_msg = f"Failed to remove server from Claude Desktop: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def update_mcp_server(self, 
                         server_name: str = "data-viz-server",
                         database_path: Optional[Path] = None,
                         python_path: Optional[str] = None) -> Tuple[bool, str]:
        """Update existing MCP server configuration"""
        try:
            # First remove the existing server
            success, message = self.remove_mcp_server(server_name)
            if not success and "not found" not in message:
                return False, message
            
            # Then add it back with new configuration
            return self.add_mcp_server(server_name, database_path, python_path, backup=False)
            
        except Exception as e:
            error_msg = f"Failed to update server configuration: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def list_mcp_servers(self) -> Dict[str, Any]:
        """List all configured MCP servers"""
        config = self.load_existing_config()
        return config.get("mcpServers", {})
    
    def validate_config(self) -> Tuple[bool, str]:
        """Validate Claude Desktop configuration"""
        try:
            if not self.config_exists():
                return False, "Configuration file does not exist"
            
            config = self.load_existing_config()
            
            if "mcpServers" not in config:
                return False, "No mcpServers section in configuration"
            
            servers = config["mcpServers"]
            if not servers:
                return True, "Configuration valid but no servers configured"
            
            # Validate each server configuration
            for server_name, server_config in servers.items():
                required_fields = ["command", "args"]
                for field in required_fields:
                    if field not in server_config:
                        return False, f"Server '{server_name}' missing required field: {field}"
                
                # Check if Python executable exists
                python_path = server_config["command"]
                if not Path(python_path).exists():
                    return False, f"Python executable not found: {python_path}"
            
            return True, f"Configuration valid with {len(servers)} server(s)"
            
        except Exception as e:
            return False, f"Configuration validation failed: {e}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of Claude Desktop configuration"""
        status = {
            "platform": self.platform,
            "config_path": str(self.config_path),
            "config_exists": self.config_exists(),
            "config_directory_exists": self.config_path.parent.exists(),
        }
        
        if self.config_exists():
            valid, message = self.validate_config()
            status["config_valid"] = valid
            status["validation_message"] = message
            status["servers"] = list(self.list_mcp_servers().keys())
        else:
            status["config_valid"] = False
            status["validation_message"] = "Configuration file does not exist"
            status["servers"] = []
        
        return status


def configure_claude_desktop(server_name: str = "data-viz-server",
                           database_path: Optional[Path] = None,
                           python_path: Optional[str] = None,
                           force: bool = False) -> Tuple[bool, str]:
    """
    Convenience function to configure Claude Desktop
    
    Args:
        server_name: Name for the MCP server
        database_path: Path to DuckDB database file
        python_path: Path to Python executable
        force: Whether to overwrite existing configuration
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    manager = ClaudeDesktopConfigManager()
    
    if force:
        # Update existing configuration
        return manager.update_mcp_server(server_name, database_path, python_path)
    else:
        # Add new configuration (fails if exists)
        return manager.add_mcp_server(server_name, database_path, python_path)