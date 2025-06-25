"""Sample database creation utilities"""

import logging
from pathlib import Path
from typing import Optional
import duckdb

logger = logging.getLogger(__name__)


def create_sample_database(db_path: Optional[str] = None) -> str:
    """
    Create a sample database with demo data for testing
    
    Args:
        db_path: Optional path for the database file
        
    Returns:
        Path to the created database
    """
    if db_path is None:
        # Default location in user's home directory
        home_dir = Path.home()
        mcp_dir = home_dir / ".mcp-visualization" 
        mcp_dir.mkdir(exist_ok=True)
        db_path = str(mcp_dir / "data.duckdb")
    
    logger.info(f"Creating sample database at: {db_path}")
    print(f"📍 Database path: {db_path}")
    
    try:
        print(f"🔌 Connecting to database...")
        # Create database and tables
        with duckdb.connect(db_path) as conn:
            print(f"✅ Connected to database successfully")
            print(f"📊 Creating sales_data table...")
            # Sales data table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sales_data (
                    id INTEGER PRIMARY KEY,
                    product_name VARCHAR,
                    category VARCHAR,
                    sales_amount DECIMAL(10,2),
                    quantity INTEGER,
                    sale_date DATE,
                    region VARCHAR
                )
            """)
            
            print(f"📊 Inserting sales data...")
            # Insert sample sales data
            conn.execute("""
                INSERT OR REPLACE INTO sales_data VALUES
                (1, 'Laptop Pro', 'Electronics', 1299.99, 2, '2024-01-15', 'North'),
                (2, 'Wireless Mouse', 'Electronics', 29.99, 5, '2024-01-16', 'South'),
                (3, 'Coffee Maker', 'Appliances', 79.99, 1, '2024-01-17', 'East'),
                (4, 'Smartphone', 'Electronics', 899.99, 3, '2024-01-18', 'West'),
                (5, 'Desk Chair', 'Furniture', 199.99, 2, '2024-01-19', 'North'),
                (6, 'Tablet', 'Electronics', 399.99, 1, '2024-01-20', 'South'),
                (7, 'Microwave', 'Appliances', 149.99, 1, '2024-01-21', 'East'),
                (8, 'Gaming Keyboard', 'Electronics', 129.99, 4, '2024-01-22', 'West'),
                (9, 'Blender', 'Appliances', 89.99, 2, '2024-01-23', 'North'),
                (10, 'Monitor', 'Electronics', 249.99, 3, '2024-01-24', 'South')
            """)
            
            print(f"👥 Creating employee_data table...")
            # Employee data table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS employee_data (
                    employee_id INTEGER PRIMARY KEY,
                    name VARCHAR,
                    department VARCHAR,
                    salary DECIMAL(10,2),
                    hire_date DATE,
                    age INTEGER,
                    performance_score DECIMAL(3,2)
                )
            """)
            
            print(f"👥 Inserting employee data...")
            # Insert sample employee data
            conn.execute("""
                INSERT OR REPLACE INTO employee_data VALUES
                (1, 'Alice Johnson', 'Engineering', 85000.00, '2022-03-15', 28, 4.2),
                (2, 'Bob Smith', 'Marketing', 62000.00, '2021-07-20', 32, 3.8),
                (3, 'Carol Davis', 'Engineering', 92000.00, '2020-11-10', 29, 4.5),
                (4, 'David Wilson', 'Sales', 58000.00, '2023-01-08', 26, 3.9),
                (5, 'Eva Brown', 'HR', 67000.00, '2021-09-12', 31, 4.1),
                (6, 'Frank Miller', 'Engineering', 88000.00, '2022-05-22', 27, 4.3),
                (7, 'Grace Lee', 'Marketing', 64000.00, '2023-02-14', 25, 4.0),
                (8, 'Henry Taylor', 'Sales', 61000.00, '2021-12-03', 33, 3.7)
            """)
            
            print(f"🌤️  Creating weather_data table...")
            # Weather data table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY,
                    city VARCHAR,
                    date DATE,
                    temperature DECIMAL(5,2),
                    humidity INTEGER,
                    precipitation DECIMAL(5,2),
                    wind_speed DECIMAL(5,2)
                )
            """)
            
            print(f"🌤️  Inserting weather data...")
            # Insert sample weather data
            conn.execute("""
                INSERT OR REPLACE INTO weather_data VALUES
                (1, 'New York', '2024-01-01', 2.5, 65, 0.0, 8.3),
                (2, 'New York', '2024-01-02', 4.1, 72, 1.2, 6.7),
                (3, 'Los Angeles', '2024-01-01', 18.9, 45, 0.0, 4.2),
                (4, 'Los Angeles', '2024-01-02', 21.3, 38, 0.0, 5.1),
                (5, 'Chicago', '2024-01-01', -5.2, 78, 2.3, 12.1),
                (6, 'Chicago', '2024-01-02', -2.8, 81, 0.8, 9.4),
                (7, 'Miami', '2024-01-01', 24.7, 85, 0.0, 7.8),
                (8, 'Miami', '2024-01-02', 26.2, 82, 0.5, 6.9)
            """)
            
            print(f"✅ Database creation completed successfully!")
            logger.info("Sample database created successfully with 3 tables:")
            logger.info("- sales_data (10 rows): Product sales with categories and regions")
            logger.info("- employee_data (8 rows): Employee information with performance")
            logger.info("- weather_data (8 rows): Weather measurements for different cities")
            
        print(f"🎉 Sample database ready at: {db_path}")
        return db_path
        
    except Exception as e:
        logger.error(f"Error creating sample database: {e}")
        raise


def get_sample_database_info() -> dict:
    """Get information about the sample database structure"""
    return {
        "tables": {
            "sales_data": {
                "description": "Product sales data with categories and regions",
                "columns": ["id", "product_name", "category", "sales_amount", "quantity", "sale_date", "region"],
                "row_count": 10
            },
            "employee_data": {
                "description": "Employee information with performance metrics",
                "columns": ["employee_id", "name", "department", "salary", "hire_date", "age", "performance_score"],
                "row_count": 8
            },
            "weather_data": {
                "description": "Weather measurements for different cities",
                "columns": ["id", "city", "date", "temperature", "humidity", "precipitation", "wind_speed"],
                "row_count": 8
            }
        }
    }