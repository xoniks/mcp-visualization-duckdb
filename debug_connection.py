#!/usr/bin/env python3
"""
Debug script to test DuckDB connection issues
"""
import sys
import os
from pathlib import Path

def test_basic_duckdb():
    """Test basic DuckDB functionality"""
    print("Testing basic DuckDB import...", file=sys.stderr)
    try:
        import duckdb
        print("✓ DuckDB import successful", file=sys.stderr)
        return True
    except Exception as e:
        print(f"✗ DuckDB import failed: {e}", file=sys.stderr)
        return False

def test_memory_connection():
    """Test in-memory DuckDB connection"""
    print("Testing in-memory DuckDB connection...", file=sys.stderr)
    try:
        import duckdb
        conn = duckdb.connect(":memory:")
        conn.execute("CREATE TABLE test (id INTEGER, name VARCHAR)")
        conn.execute("INSERT INTO test VALUES (1, 'test')")
        result = conn.execute("SELECT * FROM test").fetchall()
        conn.close()
        print(f"✓ In-memory connection successful: {result}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"✗ In-memory connection failed: {e}", file=sys.stderr)
        return False

def test_file_exists():
    """Test if the target file exists"""
    db_path = Path(r"C:\Users\X260\Downloads\duckdb-demo.duckdb")
    print(f"Testing file existence: {db_path}", file=sys.stderr)
    
    if db_path.exists():
        print(f"✓ File exists", file=sys.stderr)
        print(f"  Size: {db_path.stat().st_size} bytes", file=sys.stderr)
        print(f"  Is file: {db_path.is_file()}", file=sys.stderr)
        print(f"  Readable: {os.access(db_path, os.R_OK)}", file=sys.stderr)
        return True
    else:
        print(f"✗ File does not exist", file=sys.stderr)
        # Try to list the downloads directory
        downloads_dir = db_path.parent
        if downloads_dir.exists():
            print(f"Downloads directory contents:", file=sys.stderr)
            for item in downloads_dir.iterdir():
                if item.name.endswith(('.duckdb', '.db', '.csv')):
                    print(f"  - {item.name}", file=sys.stderr)
        return False

def test_file_connection():
    """Test connection to the actual file"""
    db_path = Path(r"C:\Users\X260\Downloads\duckdb-demo.duckdb")
    if not db_path.exists():
        print("Skipping file connection test - file doesn't exist", file=sys.stderr)
        return False
        
    print(f"Testing file connection to: {db_path}", file=sys.stderr)
    try:
        import duckdb
        conn = duckdb.connect(str(db_path))
        tables = conn.execute("SHOW TABLES").fetchall()
        conn.close()
        print(f"✓ File connection successful, tables: {tables}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"✗ File connection failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

if __name__ == "__main__":
    print("=== DuckDB Connection Debug ===", file=sys.stderr)
    
    tests = [
        ("Basic DuckDB Import", test_basic_duckdb),
        ("In-Memory Connection", test_memory_connection),
        ("File Existence Check", test_file_exists),
        ("File Connection", test_file_connection),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n--- {name} ---", file=sys.stderr)
        if test_func():
            passed += 1
    
    print(f"\n=== Results: {passed}/{len(tests)} tests passed ===", file=sys.stderr)