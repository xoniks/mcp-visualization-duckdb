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
🎯 MCP Data Visualization Server
Transform natural language into beautiful charts with Claude Desktop
"""
    console.print(Panel(banner, style="bold blue"))


def print_success(message: str):
    """Print success message"""
    console.print(f"✅ {message}", style="bold green")


def print_error(message: str):
    """Print error message"""
    console.print(f"❌ {message}", style="bold red")


def print_warning(message: str):
    """Print warning message"""
    console.print(f"⚠️  {message}", style="bold yellow")


def print_info(message: str):
    """Print info message"""
    console.print(f"ℹ️  {message}", style="cyan")


@click.group()
@click.version_option()
def main():
    """MCP Data Visualization Server CLI"""
    pass


@main.command()
@click.option('--server-name', default='data-viz-server', help='Name for the MCP server')
@click.option('--database-path', type=click.Path(), help='Path to DuckDB database file')
@click.option('--python-path', type=click.Path(), help='Path to Python executable')
@click.option('--force', is_flag=True, help='Overwrite existing configuration')
@click.option('--auto', is_flag=True, help='Use default settings without prompts')
def configure(server_name: str, database_path: Optional[str], python_path: Optional[str], 
              force: bool, auto: bool):
    """Configure Claude Desktop integration"""
    
    if not auto:
        print_banner()
        console.print("🔧 Setting up Claude Desktop integration...\n")
    
    try:
        manager = ClaudeDesktopConfigManager()
        
        # Show current status
        if not auto:
            console.print("📋 Current Configuration Status:")
            status = manager.get_status()
            
            table = Table()
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Platform", status["platform"])
            table.add_row("Config Path", status["config_path"])
            table.add_row("Config Exists", "✅ Yes" if status["config_exists"] else "❌ No")
            table.add_row("Config Valid", "✅ Yes" if status["config_valid"] else "❌ No")
            table.add_row("Existing Servers", ", ".join(status["servers"]) if status["servers"] else "None")
            
            console.print(table)
            console.print()
        
        # Convert string paths to Path objects
        db_path = Path(database_path) if database_path else None
        py_path = python_path
        
        # Interactive configuration (if not auto)
        if not auto:
            if not force and server_name in manager.list_mcp_servers():
                print_warning(f"Server '{server_name}' already exists!")
                if not Confirm.ask("Do you want to update the existing configuration?"):
                    console.print("Configuration cancelled.")
                    return
                force = True
            
            # Ask for custom paths
            console.print("📁 Configuration Options:")
            
            if not db_path:
                default_db = manager.get_default_database_path()
                custom_db = Prompt.ask(
                    f"Database path", 
                    default=str(default_db),
                    show_default=True
                )
                db_path = Path(custom_db) if custom_db != str(default_db) else default_db
            
            if not py_path:
                default_python = manager.get_python_executable()
                custom_python = Prompt.ask(
                    "Python executable",
                    default=default_python,
                    show_default=True
                )
                py_path = custom_python if custom_python != default_python else default_python
            
            # Show configuration preview
            console.print("\n📝 Configuration Preview:")
            preview_table = Table()
            preview_table.add_column("Setting", style="cyan")
            preview_table.add_column("Value", style="white")
            
            preview_table.add_row("Server Name", server_name)
            preview_table.add_row("Database Path", str(db_path))
            preview_table.add_row("Python Path", str(py_path))
            preview_table.add_row("Config File", str(manager.config_path))
            
            console.print(preview_table)
            
            if not Confirm.ask("\nProceed with configuration?", default=True):
                console.print("Configuration cancelled.")
                return
        
        # Apply configuration
        console.print("\n🚀 Applying configuration...")
        
        success, message = configure_claude_desktop(
            server_name=server_name,
            database_path=db_path,
            python_path=py_path,
            force=force
        )
        
        if success:
            print_success(message)
            console.print()
            console.print("🔄 Next steps:")
            console.print("   1. Restart Claude Desktop completely")
            console.print("   2. Open a new conversation")
            console.print("   3. Try: 'What MCP servers are available?'")
            console.print("   4. Try: 'List available tables'")
            console.print()
            print_info("Your MCP Data Visualization Server is ready! 🎉")
        else:
            print_error(message)
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Configuration failed: {e}")
        sys.exit(1)


@main.command()
@click.option('--server-name', default='data-viz-server', help='Name of the MCP server to remove')
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
    
    console.print("📊 MCP Data Visualization Server Status\n")
    
    try:
        manager = ClaudeDesktopConfigManager()
        status = manager.get_status()
        
        # Platform info
        console.print("🖥️  Platform Information:")
        platform_table = Table()
        platform_table.add_column("Setting", style="cyan")
        platform_table.add_column("Value", style="white")
        
        platform_table.add_row("Operating System", status["platform"])
        platform_table.add_row("Config Path", status["config_path"])
        platform_table.add_row("Config Directory", "✅ Exists" if status["config_directory_exists"] else "❌ Missing")
        platform_table.add_row("Config File", "✅ Exists" if status["config_exists"] else "❌ Missing")
        
        console.print(platform_table)
        console.print()
        
        # Configuration validation
        console.print("🔍 Configuration Validation:")
        if status["config_exists"]:
            valid_icon = "✅" if status["config_valid"] else "❌"
            console.print(f"{valid_icon} {status['validation_message']}")
        else:
            console.print("❌ Configuration file does not exist")
        console.print()
        
        # MCP servers
        console.print("🔧 Configured MCP Servers:")
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
            console.print("✅ PASS", style="bold green")
            passed += 1
        except Exception as e:
            console.print("❌ FAIL", style="bold red")
            console.print(f"  Error: {e}")
    
    console.print()
    if passed == total:
        print_success(f"All {total} tests passed! 🎉")
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
        
        console.print("🔧 Configured MCP Servers:\n")
        
        for name, config in servers.items():
            console.print(f"📦 [bold]{name}[/bold]")
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
    
    console.print("🗃️  Creating new database with sample data...\n")
    
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


if __name__ == "__main__":
    main()