#!/usr/bin/env python3
"""
Build script to create sample DuckDB database for package distribution
"""
import os
import sys
from pathlib import Path
import duckdb
import shutil

def create_sample_database(output_path: Path):
    """Create a comprehensive sample database with multiple tables"""
    print(f"Creating sample database at: {output_path}")
    
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing database if it exists
    if output_path.exists():
        output_path.unlink()
    
    try:
        with duckdb.connect(str(output_path)) as conn:
            print("Creating sales_data table...")
            # Sales data table
            conn.execute("""
                CREATE TABLE sales_data (
                    id INTEGER PRIMARY KEY,
                    product_name VARCHAR,
                    category VARCHAR,
                    sales_amount DECIMAL(10,2),
                    quantity INTEGER,
                    sale_date DATE,
                    region VARCHAR,
                    salesperson VARCHAR
                )
            """)
            
            # Insert comprehensive sales data
            conn.execute("""
                INSERT INTO sales_data VALUES
                (1, 'Laptop Pro', 'Electronics', 1299.99, 2, '2024-01-15', 'North', 'Alice Johnson'),
                (2, 'Wireless Mouse', 'Electronics', 29.99, 15, '2024-01-16', 'South', 'Bob Smith'),
                (3, 'Coffee Maker', 'Appliances', 79.99, 8, '2024-01-17', 'East', 'Carol Davis'),
                (4, 'Smartphone', 'Electronics', 899.99, 12, '2024-01-18', 'West', 'David Wilson'),
                (5, 'Desk Chair', 'Furniture', 199.99, 5, '2024-01-19', 'North', 'Alice Johnson'),
                (6, 'Monitor', 'Electronics', 349.99, 7, '2024-01-20', 'South', 'Eve Brown'),
                (7, 'Kitchen Blender', 'Appliances', 89.99, 4, '2024-01-21', 'East', 'Frank Miller'),
                (8, 'Bookshelf', 'Furniture', 159.99, 3, '2024-01-22', 'West', 'Grace Taylor'),
                (9, 'Tablet', 'Electronics', 449.99, 9, '2024-01-23', 'North', 'Henry Lee'),
                (10, 'Microwave', 'Appliances', 129.99, 6, '2024-01-24', 'South', 'Ivy Chen'),
                (11, 'Gaming Keyboard', 'Electronics', 79.99, 11, '2024-01-25', 'East', 'Jack White'),
                (12, 'Office Desk', 'Furniture', 299.99, 4, '2024-01-26', 'West', 'Kate Green'),
                (13, 'Smart Watch', 'Electronics', 249.99, 8, '2024-01-27', 'North', 'Liam Black'),
                (14, 'Air Fryer', 'Appliances', 119.99, 7, '2024-01-28', 'South', 'Mia Gray'),
                (15, 'Sofa', 'Furniture', 799.99, 2, '2024-01-29', 'East', 'Noah Blue')
            """)
            
            print("Creating customer_data table...")
            # Customer data table
            conn.execute("""
                CREATE TABLE customer_data (
                    customer_id INTEGER PRIMARY KEY,
                    customer_name VARCHAR,
                    email VARCHAR,
                    age INTEGER,
                    gender VARCHAR,
                    city VARCHAR,
                    state VARCHAR,
                    signup_date DATE,
                    total_purchases DECIMAL(10,2),
                    loyalty_tier VARCHAR
                )
            """)
            
            conn.execute("""
                INSERT INTO customer_data VALUES
                (1, 'John Doe', 'john.doe@email.com', 32, 'Male', 'New York', 'NY', '2023-03-15', 2459.97, 'Gold'),
                (2, 'Jane Smith', 'jane.smith@email.com', 28, 'Female', 'Los Angeles', 'CA', '2023-05-20', 1879.94, 'Silver'),
                (3, 'Mike Johnson', 'mike.j@email.com', 45, 'Male', 'Chicago', 'IL', '2023-01-10', 3299.95, 'Platinum'),
                (4, 'Sarah Wilson', 'sarah.w@email.com', 35, 'Female', 'Houston', 'TX', '2023-07-08', 1599.98, 'Silver'),
                (5, 'David Brown', 'david.b@email.com', 52, 'Male', 'Phoenix', 'AZ', '2023-02-14', 1049.99, 'Bronze'),
                (6, 'Lisa Davis', 'lisa.d@email.com', 29, 'Female', 'Philadelphia', 'PA', '2023-06-25', 2199.96, 'Gold'),
                (7, 'Chris Miller', 'chris.m@email.com', 38, 'Male', 'San Antonio', 'TX', '2023-04-12', 899.99, 'Bronze'),
                (8, 'Amy Taylor', 'amy.t@email.com', 41, 'Female', 'San Diego', 'CA', '2023-08-30', 1749.97, 'Silver'),
                (9, 'Tom Anderson', 'tom.a@email.com', 33, 'Male', 'Dallas', 'TX', '2023-03-22', 1299.99, 'Bronze'),
                (10, 'Emma White', 'emma.w@email.com', 26, 'Female', 'San Jose', 'CA', '2023-09-15', 1949.98, 'Gold')
            """)
            
            print("Creating monthly_revenue table...")
            # Monthly revenue table
            conn.execute("""
                CREATE TABLE monthly_revenue (
                    month DATE,
                    total_revenue DECIMAL(12,2),
                    orders_count INTEGER,
                    avg_order_value DECIMAL(8,2),
                    new_customers INTEGER,
                    returning_customers INTEGER
                )
            """)
            
            conn.execute("""
                INSERT INTO monthly_revenue VALUES
                ('2023-01-01', 45000.00, 150, 300.00, 45, 105),
                ('2023-02-01', 52000.00, 173, 300.58, 38, 135),
                ('2023-03-01', 48000.00, 160, 300.00, 42, 118),
                ('2023-04-01', 61000.00, 203, 300.49, 55, 148),
                ('2023-05-01', 58000.00, 193, 300.52, 48, 145),
                ('2023-06-01', 65000.00, 217, 299.54, 62, 155),
                ('2023-07-01', 71000.00, 237, 299.58, 68, 169),
                ('2023-08-01', 69000.00, 230, 300.00, 59, 171),
                ('2023-09-01', 74000.00, 247, 299.59, 71, 176),
                ('2023-10-01', 78000.00, 260, 300.00, 75, 185),
                ('2023-11-01', 85000.00, 283, 300.35, 82, 201),
                ('2023-12-01', 92000.00, 307, 299.67, 89, 218)
            """)
            
            print("Creating product_categories table...")
            # Product categories performance
            conn.execute("""
                CREATE TABLE product_categories (
                    category VARCHAR,
                    total_sales DECIMAL(12,2),
                    units_sold INTEGER,
                    avg_price DECIMAL(8,2),
                    profit_margin DECIMAL(5,2),
                    customer_rating DECIMAL(3,2)
                )
            """)
            
            conn.execute("""
                INSERT INTO product_categories VALUES
                ('Electronics', 234599.88, 1250, 187.68, 22.5, 4.2),
                ('Furniture', 189799.92, 485, 391.34, 35.2, 4.1),
                ('Appliances', 145699.95, 823, 177.06, 28.7, 4.3),
                ('Clothing', 98750.00, 1875, 52.67, 45.3, 3.9),
                ('Sports', 76890.50, 967, 79.51, 32.1, 4.0),
                ('Books', 45230.75, 2011, 22.50, 40.8, 4.4),
                ('Beauty', 67890.25, 1534, 44.26, 55.2, 4.1),
                ('Toys', 34567.80, 891, 38.79, 38.9, 4.2)
            """)
            
            print("Sample database created successfully!")
            print(f"Database size: {output_path.stat().st_size / 1024:.1f} KB")
            
            # Verify the database by listing tables
            tables = conn.execute("SHOW TABLES").fetchall()
            print(f"Created {len(tables)} tables:")
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                print(f"  - {table[0]}: {count} rows")
                
        return True
        
    except Exception as e:
        print(f"Error creating sample database: {e}")
        return False

def main():
    """Main build script"""
    print("MCP Visualization DuckDB - Sample Database Builder")
    print("=" * 50)
    
    # Define paths
    script_dir = Path(__file__).parent
    package_dir = script_dir / "mcp_visualization"
    data_dir = package_dir / "data"
    sample_db_path = data_dir / "sample.duckdb"
    
    print(f"Script directory: {script_dir}")
    print(f"Package directory: {package_dir}")
    print(f"Data directory: {data_dir}")
    print(f"Sample database path: {sample_db_path}")
    
    # Create sample database
    success = create_sample_database(sample_db_path)
    
    if success:
        print("\n✅ Build completed successfully!")
        print(f"📁 Sample database created at: {sample_db_path}")
        print(f"📊 Ready for package distribution")
        return 0
    else:
        print("\n❌ Build failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())