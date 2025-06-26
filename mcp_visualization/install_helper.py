#!/usr/bin/env python3
"""
Post-installation helper to extract sample database and guide users
"""
import os
import sys
from pathlib import Path
import shutil
import pkg_resources

def extract_sample_database():
    """Create sample database from CSV files in the package"""
    try:
        # Get the package data directory
        package_data_dir = Path(pkg_resources.resource_filename('mcp_visualization', 'data'))
        
        print("MCP Visualization - Sample Database Setup")
        print("=" * 45)
        
        # Check for CSV files
        csv_files = list(package_data_dir.glob("*.csv"))
        if not csv_files:
            print("WARNING: Sample CSV files not found in package")
            print(f"   Expected location: {package_data_dir}")
            return None
            
        print(f"Found {len(csv_files)} sample CSV files")
        for csv_file in csv_files:
            print(f"   - {csv_file.name}")
            
        # Create user data directory in Downloads (more visible)
        user_home = Path.home()
        sample_dir = user_home / "Downloads" / "mcp-visualization-samples"
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        # Also create backup location
        backup_dir = user_home / ".mcp-visualization" / "samples"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create DuckDB database from CSV files
        sample_db_dest = sample_dir / "sample.duckdb"
        print(f"Creating sample database...")
        print(f"   Location: {sample_db_dest}")
        
        # Import duckdb
        import duckdb
        
        # Remove existing database if it exists
        if sample_db_dest.exists():
            sample_db_dest.unlink()
            
        # Create database and import CSV files with timeout protection
        try:
            print(f"   Connecting to DuckDB (this may take a moment on Windows)...")
            conn = duckdb.connect(str(sample_db_dest))
            
            for csv_file in csv_files:
                table_name = csv_file.stem  # Use filename without extension as table name
                print(f"   Importing {csv_file.name} as table '{table_name}'...")
                
                try:
                    # Import CSV file with explicit read mode
                    conn.execute(f"""
                        CREATE TABLE {table_name} AS 
                        SELECT * FROM read_csv_auto('{csv_file}')
                    """)
                    
                    # Get row count
                    row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                    print(f"     SUCCESS: {row_count} rows imported")
                    
                except Exception as table_error:
                    print(f"     WARNING: Error importing {csv_file.name}: {table_error}")
                    
            # Close connection
            conn.close()
            print(f"   SUCCESS: Database connection closed successfully")
            
        except Exception as db_error:
            print(f"   WARNING: DuckDB connection error: {db_error}")
            print(f"   Falling back to CSV file distribution...")
            # If DuckDB fails, just copy the CSV files to both locations
            for csv_file in csv_files:
                dest_csv = sample_dir / csv_file.name
                backup_csv = backup_dir / csv_file.name
                shutil.copy2(csv_file, dest_csv)
                shutil.copy2(csv_file, backup_csv)
                print(f"   Copied {csv_file.name} to {dest_csv}")
            return sample_dir  # Return directory instead of DB file
        
        # Verify the copy
        if sample_db_dest.exists():
            size_mb = sample_db_dest.stat().st_size / (1024 * 1024)
            print(f"SUCCESS: Sample database extracted successfully!")
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Location: {sample_db_dest}")
            
            # Also copy to backup location
            backup_db = backup_dir / "sample.duckdb"
            shutil.copy2(sample_db_dest, backup_db)
            print(f"   Backup: {backup_db}")
            
            # Create a readme file
            readme_content = f"""# MCP Visualization Sample Database

This directory contains sample data for the MCP Data Visualization server.

## Files:
- `sample.duckdb`: Sample DuckDB database with multiple tables

## Sample Database Contents:
- **sales_data**: Product sales with categories, regions, and salesperson info (15 rows)
- **customer_data**: Customer demographics and purchase history (10 rows)  
- **monthly_revenue**: Monthly business metrics and trends (12 rows)
- **product_categories**: Category performance and ratings (8 rows)

## How to Use:
1. Configure your MCP server to use this database:
   ```
   {sample_db_dest}
   ```

2. Or load it directly in Claude Desktop:
   - Say: "Load the sample database"
   - Or: "Load database from {sample_db_dest}"

3. Try these visualizations:
   - "Create a bar chart of sales by region"
   - "Show monthly revenue trends"
   - "Compare product categories by profit margin"
   - "Create a scatter plot of customer age vs total purchases"

## Configuration:
Add this to your Claude Desktop config file:

```json
{{
  "mcpServers": {{
    "data-viz-server": {{
      "command": "python",
      "args": ["-m", "mcp_visualization.server"],
      "env": {{
        "DUCKDB_DATABASE_PATH": "{sample_db_dest.as_posix()}"
      }}
    }}
  }}
}}
```

Generated on: {sample_db_dest.stat().st_mtime}
"""
            
            readme_path = sample_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"Created README: {readme_path}")
            return sample_db_dest
            
        else:
            print("ERROR: Failed to copy sample database")
            return None
            
    except Exception as e:
        print(f"ERROR: Error extracting sample database: {e}")
        import traceback
        traceback.print_exc()
        return None

def show_quick_start_guide(sample_db_path):
    """Show quick start instructions to the user"""
    print("\n" + "=" * 50)
    print("QUICK START GUIDE")
    print("=" * 50)
    
    print("\n1. SAMPLE DATABASE READY:")
    print(f"   Location: {sample_db_path}")
    print("   4 tables with sample business data")
    print(f"   Check your Downloads folder: Downloads/mcp-visualization-samples/")
    
    print("\n2. CONFIGURE CLAUDE DESKTOP:")
    print("   Run: mcp-viz configure")
    print("   This will set up the MCP server automatically")
    
    print("\n3. RESTART CLAUDE DESKTOP:")
    print("   Close and reopen Claude Desktop completely")
    
    print("\n4. TRY THESE COMMANDS:")
    print('   "What MCP servers are available?"')
    print('   "Load the sample database"')
    print('   "Show me available tables"')
    print('   "Create a sales chart by region"')
    print('   "Show monthly revenue trends"')
    
    print("\n5. LOAD YOUR OWN DATA:")
    print('   "Browse databases in downloads"')
    print('   "Load database from [your_path]"')
    
    print("\nAVAILABLE CLI COMMANDS:")
    print("   mcp-viz configure      # Configure Claude Desktop integration")
    print("   mcp-viz status         # Show configuration status")
    print("   mcp-viz setup-samples  # Extract sample database")
    print("   mcp-viz find-samples   # Find sample database location")
    print("   mcp-viz list-servers   # List all MCP servers")
    print("   mcp-viz --help         # Show all available commands")
    
    print("\nTROUBLESHOOTING:")
    print("   * Run 'mcp-viz status' to check configuration")
    print("   * Restart Claude Desktop after configuration")
    print("   * Check server logs in Claude Desktop if tools don't appear")
    print("=" * 50)

def print_post_install_instructions(sample_db_path):
    """Show post-installation instructions and next steps"""
    print("\n" + "=" * 60)
    print("INSTALLATION COMPLETE!")
    print("=" * 60)
    
    if sample_db_path:
        print(f"\nSample Database Ready: {sample_db_path}")
    
    print("\nNEXT STEPS:")
    print("1. Choose your database option:")
    print("   a) DuckDB (Local): mcp-viz configure")
    print("   b) Databricks (Enterprise): mcp-viz databricks configure")
    print("\n2. Restart Claude Desktop completely")
    print("\n3. Start chatting with Claude about your data!")
    
    print("\nQUICK START COMMANDS (Run Once):")
    print("   mcp-viz configure              # Setup DuckDB") 
    print("   mcp-viz databricks configure   # Setup Databricks")
    print("   mcp-viz status                 # Check configuration")
    print("   mcp-viz databricks test        # Test Databricks connection")
    
    print("\nONGOING USAGE (Daily):")
    print("   - Just open Claude Desktop and start chatting!")
    print("   - No need to reconfigure unless credentials change")
    print("   - Your credentials are stored securely and auto-loaded")
    
    print("\nSAMPLE DATABASES:")
    print("   Built-in sample data: Already included in your installation")
    print("   More sample databases: https://www.timestored.com/data/sample/duckdb")
    print("   Financial data, NYC taxi, TPC-H benchmarks and more!")
    
    print("\nTRY THESE COMMANDS IN CLAUDE DESKTOP:")
    print('   "What tables are available?"')
    print('   "Create a bar chart of sales by region"')
    print('   "Show me monthly revenue trends"')
    print('   "Load CSV from Downloads/mydata.csv"')
    
    if sample_db_path:
        print(f"\nYour sample database location:")
        print(f"   {sample_db_path}")
    
    print("\nDOCUMENTATION:")
    print("   GitHub: https://github.com/your-username/mcp-visualization-duckdb")
    print("   Help: mcp-viz --help")
    
    print("\n" + "=" * 60)
    print("Happy data visualization with Claude Desktop!")
    print("=" * 60)

def main():
    """Main installation helper"""
    try:
        # Extract sample database
        sample_db_path = extract_sample_database()
        
        if sample_db_path:
            # Show quick start guide
            show_quick_start_guide(sample_db_path)
            
            print_post_install_instructions(sample_db_path)
            return 0
        else:
            print("\nInstallation completed with warnings")
            print("   Sample database extraction failed")
            print_post_install_instructions(None)
            return 1
            
    except Exception as e:
        print(f"\nInstallation helper failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())