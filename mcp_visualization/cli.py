"""
Command-line interface for MCP Visualization Server configuration
"""

import click
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text

from .claude_config import ClaudeDesktopConfigManager, configure_claude_desktop
from .server import test_server_import

console = Console()


def print_banner():
    """Print welcome banner"""
    banner = """
Target MCP Data Visualization Server
Transform natural language into beautiful charts with Claude Desktop
"""
    console.print(Panel(banner, style="bold blue"))


def print_success(message: str):
    """Print success message"""
    console.print(f"SUCCESS {message}", style="bold green")


def print_error(message: str):
    """Print error message"""
    console.print(f"ERROR {message}", style="bold red")


def print_warning(message: str):
    """Print warning message"""
    console.print(f"WARNING  {message}", style="bold yellow")


def print_info(message: str):
    """Print info message"""
    console.print(f"INFO  {message}", style="cyan")


@click.group()
@click.version_option()
def main():
    """MCP Data Visualization Server CLI"""
    pass


@main.command()
@click.option('--server-name', default='mcp-duckdb-viz', help='Name for the MCP server')
@click.option('--database-path', type=click.Path(), help='Path to DuckDB database file')
@click.option('--python-path', type=click.Path(), help='Path to Python executable')
@click.option('--force', is_flag=True, help='Overwrite existing configuration')
@click.option('--auto', is_flag=True, help='Use default settings without prompts')
def configure(server_name: str, database_path: Optional[str], python_path: Optional[str], 
              force: bool, auto: bool):
    """Configure Claude Desktop integration"""
    
    if not auto:
        print_banner()
        console.print("Config Setting up Claude Desktop integration...\n")
    
    try:
        manager = ClaudeDesktopConfigManager()
        
        # Show current status
        if not auto:
            console.print("INFO Current Configuration Status:")
            status = manager.get_status()
            
            table = Table()
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Platform", status["platform"])
            table.add_row("Config Path", status["config_path"])
            table.add_row("Config Exists", "SUCCESS Yes" if status["config_exists"] else "ERROR No")
            table.add_row("Config Valid", "SUCCESS Yes" if status["config_valid"] else "ERROR No")
            table.add_row("Existing Servers", ", ".join(status["servers"]) if status["servers"] else "None")
            
            console.print(table)
            console.print()
        
        # Convert string paths to Path objects
        db_path = Path(database_path) if database_path else None
        py_path = python_path
        
        # Auto configuration - no prompts needed
        console.print("Auto-configuring MCP server...")
        
        # Use default Python executable  
        if not py_path:
            py_path = manager.get_python_executable()
        console.print(f"Using Python: {py_path}")
        
        # Skip database setup (no database needed)
        db_path = None
        create_sample = False
        console.print("Database-free mode (connect databases via Claude Desktop)")
        
        # Show simple configuration summary
        console.print(f"Server name: {server_name}")
        console.print(f"Config file: {manager.config_path}")
        
        # Check for existing server and handle gracefully
        if not force and server_name in manager.list_mcp_servers():
            print_warning(f"Server '{server_name}' already exists!")
            if not Confirm.ask("Do you want to update the existing configuration?"):
                console.print("Configuration cancelled.")
                return
            force = True
        
        # Apply configuration
        console.print("\nApplying configuration...")
        
        success, message = configure_claude_desktop(
            server_name=server_name,
            database_path=db_path,
            python_path=py_path,
            force=force
        )
        
        if success:
            print_success(message)
            console.print()
            console.print("[bold green]Next steps:[/bold green]")
            console.print("   1. Restart Claude Desktop completely")
            console.print("   2. Open a new conversation")
            console.print("   3. Try: 'What MCP servers are available?'")
            console.print("   4. Try: 'Browse databases in downloads'")
            console.print("   5. Try: 'Load database from downloads and create a chart'")
            console.print("   6. Try: 'Show me available visualization tools'")
            console.print()
            console.print("[bold cyan]Your MCP Data Visualization Server is ready![/bold cyan]")
            console.print("[dim]Database files in Downloads folder can now be easily browsed and loaded![/dim]")
        else:
            print_error(message)
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Configuration failed: {e}")
        sys.exit(1)


@main.command()
@click.option('--server-name', default='mcp-duckdb-viz', help='Name of the MCP server to remove')
def remove(server_name: str):
    """Remove MCP server from Claude Desktop configuration"""
    
    console.print("🗑️  Removing MCP server configuration...\n")
    
    try:
        manager = ClaudeDesktopConfigManager()
        
        # Show current servers
        servers = manager.list_mcp_servers()
        if not servers:
            print_warning("No MCP servers found in configuration")
            return
        
        if server_name not in servers:
            print_error(f"Server '{server_name}' not found")
            console.print("Available servers:")
            for name in servers.keys():
                console.print(f"  • {name}")
            return
        
        # Confirm removal
        if not Confirm.ask(f"Remove server '{server_name}' from Claude Desktop configuration?"):
            console.print("Removal cancelled.")
            return
        
        success, message = manager.remove_mcp_server(server_name)
        
        if success:
            print_success(message)
            print_info("Please restart Claude Desktop to apply changes")
        else:
            print_error(message)
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Removal failed: {e}")
        sys.exit(1)


@main.command()
def status():
    """Show configuration status"""
    
    console.print("CHART MCP Data Visualization Server Status\n")
    
    try:
        manager = ClaudeDesktopConfigManager()
        status = manager.get_status()
        
        # Platform info
        console.print("COMPUTER  Platform Information:")
        platform_table = Table()
        platform_table.add_column("Setting", style="cyan")
        platform_table.add_column("Value", style="white")
        
        platform_table.add_row("Operating System", status["platform"])
        platform_table.add_row("Config Path", status["config_path"])
        platform_table.add_row("Config Directory", "SUCCESS Exists" if status["config_directory_exists"] else "ERROR Missing")
        platform_table.add_row("Config File", "SUCCESS Exists" if status["config_exists"] else "ERROR Missing")
        
        console.print(platform_table)
        console.print()
        
        # Configuration validation
        console.print("SEARCH Configuration Validation:")
        if status["config_exists"]:
            valid_icon = "SUCCESS" if status["config_valid"] else "ERROR"
            console.print(f"{valid_icon} {status['validation_message']}")
        else:
            console.print("ERROR Configuration file does not exist")
        console.print()
        
        # MCP servers
        console.print("Config Configured MCP Servers:")
        if status["servers"]:
            for i, server in enumerate(status["servers"], 1):
                console.print(f"  {i}. {server}")
        else:
            console.print("  No servers configured")
        console.print()
        
        # Server test
        console.print("🧪 Server Import Test:")
        try:
            test_server_import()
            print_success("Server code can be imported successfully")
        except Exception as e:
            print_error(f"Server import failed: {e}")
        
    except Exception as e:
        print_error(f"Status check failed: {e}")
        sys.exit(1)


@main.group()
def databricks():
    """Databricks integration commands (run once for setup, then use Claude Desktop daily)"""
    pass


@databricks.command()
@click.option('--server-hostname', help='Databricks workspace hostname (e.g., your-workspace.cloud.databricks.com)')
@click.option('--http-path', help='SQL warehouse HTTP path (e.g., /sql/1.0/warehouses/abc123)')
@click.option('--token', help='Access token (not recommended for security)')
@click.option('--interactive/--no-interactive', default=True, help='Interactive credential setup')
@click.option('--test-connection/--no-test', default=True, help='Test connection before saving')
@click.option('--use-keyring/--no-keyring', default=True, help='Use system keyring for secure storage')
def configure(server_hostname, http_path, token, interactive, test_connection, use_keyring):
    """Configure Databricks connection credentials (run once, then credentials are auto-loaded)"""
    
    print_banner()
    console.print("DATABRICKS Databricks Configuration\n")
    
    try:
        from mcp_visualization.databricks_integration.credentials import DatabricksCredentialManager
        
        cred_manager = DatabricksCredentialManager()
        
        # Check for existing credentials
        existing_creds = cred_manager.load_credentials()
        if existing_creds and not interactive:
            console.print("SUCCESS Existing Databricks credentials found")
            console.print(f"Server: {existing_creds['server_hostname']}")
            console.print(f"HTTP Path: {existing_creds['http_path']}")
            console.print(f"Token: {existing_creds['token'][:8]}..." + existing_creds['token'][-4:])
            return
        
        # Gather credentials
        if interactive or not all([server_hostname, http_path, token]):
            creds = cred_manager.prompt_for_credentials(interactive=True)
            if not creds:
                console.print("Configuration cancelled.")
                return
        else:
            creds = {
                "server_hostname": server_hostname,
                "http_path": http_path,
                "token": token
            }
            
            # Test connection if requested
            if test_connection:
                console.print("Testing connection...")
                try:
                    if not cred_manager.test_connection(server_hostname, http_path, token):
                        print_error("Connection test failed. Please check your credentials.")
                        return
                    print_success("Connection test successful!")
                except Exception as e:
                    print_error(f"Connection test failed with error: {e}")
                    console.print(f"Error details: {type(e).__name__}: {str(e)}")
                    import traceback
                    console.print("Full traceback:")
                    console.print(traceback.format_exc())
                    return
        
        # Store credentials
        console.print("Storing credentials securely...")
        if cred_manager.store_credentials(
            creds["server_hostname"], 
            creds["http_path"], 
            creds["token"],
            use_keyring=use_keyring
        ):
            print_success("Databricks credentials configured successfully!")
            
            # Show next steps
            console.print("\nNext steps:")
            console.print("1. Configure MCP server: mcp-viz configure --database-type databricks")
            console.print("2. Restart Claude Desktop")
            console.print("3. Try: 'What Databricks catalogs are available?'")
        else:
            print_error("Failed to store credentials")
            
    except ImportError:
        print_error("Databricks dependencies not installed. Run: pip install databricks-sql-connector")
        sys.exit(1)
    except Exception as e:
        print_error(f"Databricks configuration failed: {e}")
        sys.exit(1)


@databricks.command()
def status():
    """Show Databricks connection status"""
    
    console.print("DATABRICKS Databricks Connection Status\n")
    
    try:
        from mcp_visualization.databricks_integration.credentials import DatabricksCredentialManager
        
        cred_manager = DatabricksCredentialManager()
        creds = cred_manager.load_credentials()
        
        if not creds:
            print_warning("No Databricks credentials configured")
            console.print("Run: mcp-viz databricks configure")
            return
        
        # Show connection info (masked)
        table = Table()
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Server Hostname", creds["server_hostname"])
        table.add_row("HTTP Path", creds["http_path"])
        
        masked_token = creds["token"][:8] + "..." + creds["token"][-4:] if len(creds["token"]) > 12 else "***"
        table.add_row("Access Token", masked_token)
        
        console.print(table)
        console.print()
        
        # Test connection
        console.print("CONNECTION Testing connection...")
        if cred_manager.test_connection(creds["server_hostname"], creds["http_path"], creds["token"]):
            print_success("Connection successful!")
        else:
            print_error("Connection failed!")
            
    except ImportError:
        print_error("Databricks dependencies not installed. Run: pip install databricks-sql-connector")
    except Exception as e:
        print_error(f"Status check failed: {e}")


@databricks.command()
def test():
    """Test Databricks connection and show available catalogs"""
    
    console.print("DATABASE Testing Databricks Integration\n")
    
    try:
        from mcp_visualization.databricks_integration.manager import DatabricksManager
        
        db_manager = DatabricksManager()
        
        if not db_manager.connect():
            print_error("Failed to connect to Databricks")
            console.print("Run: mcp-viz databricks configure")
            return
        
        print_success("Connected to Databricks!")
        
        # Show connection info
        info = db_manager.get_connection_info()
        console.print(f"Current catalog: {info['current_catalog']}")
        console.print(f"Current schema: {info['current_schema']}")
        console.print()
        
        # List catalogs
        console.print("Available catalogs:")
        catalogs = db_manager.get_catalogs()
        if catalogs:
            for i, catalog in enumerate(catalogs, 1):
                console.print(f"  {i}. {catalog['name']}")
        else:
            console.print("  No catalogs found")
        console.print()
        
        # List schemas in current catalog
        console.print(f"Schemas in '{info['current_catalog']}':")
        schemas = db_manager.get_schemas()
        if schemas:
            for i, schema in enumerate(schemas[:5], 1):  # Show first 5
                console.print(f"  {i}. {schema['name']}")
            if len(schemas) > 5:
                console.print(f"  ... and {len(schemas) - 5} more")
        else:
            console.print("  No schemas found")
        console.print()
        
        # List tables in current schema
        console.print(f"Tables in '{info['current_catalog']}.{info['current_schema']}':")
        tables = db_manager.get_tables()
        if tables:
            for i, table in enumerate(tables[:5], 1):  # Show first 5
                console.print(f"  {i}. {table['name']}")
            if len(tables) > 5:
                console.print(f"  ... and {len(tables) - 5} more")
        else:
            console.print("  No tables found")
        
        db_manager.close()
        print_success("Databricks integration test completed!")
        
    except ImportError:
        print_error("Databricks dependencies not installed. Run: pip install databricks-sql-connector")
    except Exception as e:
        print_error(f"Test failed: {e}")


@databricks.command()
def remove():
    """Remove stored Databricks credentials"""
    
    console.print("DELETE Removing Databricks Credentials\n")
    
    try:
        from mcp_visualization.databricks_integration.credentials import DatabricksCredentialManager
        
        cred_manager = DatabricksCredentialManager()
        
        # Check if credentials exist
        if not cred_manager.load_credentials():
            print_warning("No Databricks credentials found")
            return
        
        # Confirm removal
        if not Confirm.ask("Remove stored Databricks credentials?"):
            console.print("Removal cancelled.")
            return
        
        if cred_manager.delete_credentials():
            print_success("Databricks credentials removed successfully!")
        else:
            print_error("Failed to remove credentials")
            
    except Exception as e:
        print_error(f"Credential removal failed: {e}")




@main.command()
def test():
    """Test server functionality"""
    
    console.print("🧪 Testing MCP Data Visualization Server\n")
    
    tests = [
        ("Import server module", test_server_import),
        ("Claude Desktop config detection", lambda: ClaudeDesktopConfigManager().get_status()),
        ("Database path creation", lambda: ClaudeDesktopConfigManager().get_default_database_path().parent.mkdir(parents=True, exist_ok=True)),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            console.print(f"Running: {test_name}... ", end="")
            test_func()
            console.print("SUCCESS PASS", style="bold green")
            passed += 1
        except Exception as e:
            console.print("ERROR FAIL", style="bold red")
            console.print(f"  Error: {e}")
    
    console.print()
    if passed == total:
        print_success(f"All {total} tests passed! COMPLETE")
    else:
        print_warning(f"{passed}/{total} tests passed")
        if passed < total:
            sys.exit(1)


@main.command()
def list_servers():
    """List all configured MCP servers"""
    
    try:
        manager = ClaudeDesktopConfigManager()
        servers = manager.list_mcp_servers()
        
        if not servers:
            print_info("No MCP servers configured")
            return
        
        console.print("Config Configured MCP Servers:\n")
        
        for name, config in servers.items():
            console.print(f"PACKAGE [bold]{name}[/bold]")
            console.print(f"   Command: {config.get('command', 'N/A')}")
            console.print(f"   Args: {' '.join(config.get('args', []))}")
            console.print(f"   Working Dir: {config.get('cwd', 'N/A')}")
            
            if 'env' in config:
                console.print("   Environment:")
                for key, value in config['env'].items():
                    console.print(f"     {key}: {value}")
            console.print()
            
    except Exception as e:
        print_error(f"Failed to list servers: {e}")
        sys.exit(1)


@main.command()
@click.option('--path', type=click.Path(exists=True), help='Path to database file')
def create_db(path: Optional[str]):
    """Create a new DuckDB database with sample data"""
    
    console.print("Database  Creating new database with sample data...\n")
    
    try:
        from .database import create_sample_database
        
        if not path:
            manager = ClaudeDesktopConfigManager()
            path = str(manager.get_default_database_path())
        
        db_path = Path(path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        create_sample_database(str(db_path))
        print_success(f"Database created: {db_path}")
        print_info("Database includes sample tables: sales, customers, products")
        
    except Exception as e:
        print_error(f"Database creation failed: {e}")
        sys.exit(1)


@main.command()
def setup_samples():
    """Extract and set up sample database from package"""
    try:
        from .install_helper import main as install_main
        return install_main()
    except Exception as e:
        print_error(f"Sample setup failed: {e}")
        sys.exit(1)


@main.command()
def find_samples():
    """Find and show sample database location"""
    try:
        from pathlib import Path
        
        # Check Downloads directory first (primary location)
        user_home = Path.home()
        sample_dir = user_home / "Downloads" / "mcp-visualization-samples"
        sample_db = sample_dir / "sample.duckdb"
        
        # Also check backup location
        backup_dir = user_home / ".mcp-visualization" / "samples"
        backup_db = backup_dir / "sample.duckdb"
        
        console.print("🔍 [bold]Searching for sample databases...[/bold]\n")
        
        if sample_db.exists():
            size_mb = sample_db.stat().st_size / (1024 * 1024)
            console.print(f"✅ [green]Sample database found![/green]")
            console.print(f"   📍 Location: {sample_db}")
            console.print(f"   📊 Size: {size_mb:.2f} MB")
            console.print(f"   📁 Directory: {sample_dir}")
            
            # Check if backup also exists
            if backup_db.exists():
                console.print(f"   🔄 Backup: {backup_db}")
            
            # Check if README exists
            readme_path = sample_dir / "README.md"
            if readme_path.exists():
                console.print(f"   📝 Documentation: {readme_path}")
            
            console.print(f"\n💡 [cyan]To use this database:[/cyan]")
            console.print(f'   • Say: "Load database from {sample_db}"')
            console.print(f'   • Or configure it permanently with: mcp-viz configure')
            
        elif backup_db.exists():
            size_mb = backup_db.stat().st_size / (1024 * 1024)
            console.print(f"✅ [green]Sample database found in backup location![/green]")
            console.print(f"   📍 Location: {backup_db}")
            console.print(f"   📊 Size: {size_mb:.2f} MB")
            console.print(f"   📁 Directory: {backup_dir}")
            
            console.print(f"\n💡 [cyan]To use this database:[/cyan]")
            console.print(f'   • Say: "Load database from {backup_db}"')
            console.print(f'   • Or configure it permanently with: mcp-viz configure')
            
        else:
            # Check if we have CSV files in the package
            try:
                import pkg_resources
                package_data_dir = Path(pkg_resources.resource_filename('mcp_visualization', 'data'))
                csv_files = list(package_data_dir.glob("*.csv"))
                
                if csv_files:
                    console.print("📊 [yellow]Sample CSV files found in package[/yellow]")
                    console.print(f"   📁 Package data: {package_data_dir}")
                    for csv_file in csv_files:
                        console.print(f"   - {csv_file.name}")
                    console.print(f"\n💡 [cyan]To create sample database:[/cyan]")
                    console.print(f"   Run: mcp-viz setup-samples")
                else:
                    console.print("❌ [red]No sample data found[/red]")
                    console.print(f"   Expected database: {sample_db}")
                    console.print(f"   Expected CSV files: {package_data_dir}")
                    console.print(f"\n💡 [cyan]To set up sample database:[/cyan]")
                    console.print(f"   Run: mcp-viz setup-samples")
                    
            except Exception as pkg_error:
                console.print("❌ [red]Sample database not found[/red]")
                console.print(f"   Expected location: {sample_db}")
                console.print(f"\n💡 [cyan]To set up sample database:[/cyan]")
                console.print(f"   Run: mcp-viz setup-samples")
            
    except Exception as e:
        print_error(f"Search failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()