#!/usr/bin/env python3
"""
Quick test to reproduce the database loading issue
"""
import sys
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from mcp_visualization.database.manager import DatabaseManager
    
    print("Testing database connection...", file=sys.stderr)
    
    # Test the exact path from the logs
    db_path = Path(r"C:\Users\X260\Downloads\duckdb-demo.duckdb")
    
    print(f"Checking if file exists: {db_path.exists()}", file=sys.stderr)
    
    if db_path.exists():
        print("File exists, attempting connection...", file=sys.stderr)
        
        # Try to create database manager
        db_manager = DatabaseManager(db_path)
        
        print("Connection successful!", file=sys.stderr)
        
        # Try to get tables
        tables = db_manager.get_tables()
        print(f"Found {len(tables)} tables", file=sys.stderr)
        
        db_manager.close()
        print("Test completed successfully", file=sys.stderr)
    else:
        print("Database file not found", file=sys.stderr)
        
except Exception as e:
    print(f"Error during test: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)