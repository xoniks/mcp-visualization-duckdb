# scripts/create_sample_db.py

import duckdb
from pathlib import Path
import os
import pandas as pd
import numpy as np  # Used by pandas internally for some operations, good to have it explicit

# Define the base data directory relative to the script's location
# This assumes the script is run from the project root (e.g., C:\Github\mcp-visualization-duckdb)
# and this script is in a 'scripts' subfolder.
BASE_DATA_DIR = Path(__file__).parent.parent / "data"
DATABASE_FILE = "mcp.duckdb"  # This should match the default in your config/settings.py


def create_sample_duckdb():
    """
    Creates a sample DuckDB database with 'sales' and 'customers' tables.
    Data is inserted only if the tables are empty to avoid duplicates on re-runs.
    """
    # Ensure the data directory exists
    # If BASE_DATA_DIR is C:\Github\mcp-visualization-duckdb\data, it will create 'data'
    # if it doesn't exist.
    BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_path = BASE_DATA_DIR / DATABASE_FILE

    print(f"Attempting to create/connect to DuckDB at: {db_path}")

    try:
        # Connect to DuckDB. If the file doesn't exist, it will be created.
        # read_only=False ensures we can write to the database.
        con = duckdb.connect(database=str(db_path), read_only=False)

        # --- Create 'sales' table and insert data ---
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER,
                product_name VARCHAR,
                category VARCHAR,
                sale_date DATE,
                amount DECIMAL(10, 2),
                quantity INTEGER
            );
        """
        )
        print("Table 'sales' created or already exists.")

        # Check if 'sales' table is empty before inserting data
        result = con.execute("SELECT COUNT(*) FROM sales;").fetchone()
        if result[0] == 0:
            print("Inserting sample data into 'sales' table...")
            sales_data = [
                (1, "Laptop", "Electronics", "2024-01-05", 1200.00, 1),
                (2, "Mouse", "Electronics", "2024-01-05", 25.50, 2),
                (3, "Keyboard", "Electronics", "2024-01-06", 75.00, 1),
                (4, "Desk Chair", "Furniture", "2024-01-07", 350.00, 1),
                (5, "Monitor", "Electronics", "2024-01-08", 299.99, 1),
                (6, "Coffee Table", "Furniture", "2024-01-09", 150.00, 1),
                (7, "Headphones", "Electronics", "2024-01-10", 99.99, 1),
                (8, "Notebook", "Office Supplies", "2024-01-11", 5.99, 5),
                (9, "Pen Set", "Office Supplies", "2024-01-12", 12.50, 3),
                (10, "Smartphone", "Electronics", "2024-01-13", 800.00, 1),
                (11, "Desk Lamp", "Furniture", "2024-01-14", 45.00, 1),
                (12, "External SSD", "Electronics", "2024-01-15", 89.99, 1),
                (13, "Printer", "Office Supplies", "2024-01-16", 199.00, 1),
                (14, "Webcam", "Electronics", "2024-01-17", 60.00, 1),
                (15, "Standing Desk", "Furniture", "2024-01-18", 499.00, 1),
            ]
            con.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?)", sales_data)
            print("Sample sales data inserted.")
        else:
            print("Sales table already contains data. Skipping insertion.")

        # --- Create 'customers' table and insert data from Pandas DataFrame ---
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER,
                first_name VARCHAR,
                last_name VARCHAR,
                email VARCHAR,
                registration_date DATE
            );
        """
        )
        print("Table 'customers' created or already exists.")

        # Check if 'customers' table is empty before inserting data
        result_cust = con.execute("SELECT COUNT(*) FROM customers;").fetchone()
        if result_cust[0] == 0:
            print("Inserting sample data into 'customers' table from DataFrame...")
            customer_data = pd.DataFrame(
                {
                    "customer_id": [101, 102, 103, 104, 105],
                    "first_name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                    "last_name": ["Smith", "Johnson", "Brown", "Davis", "Wilson"],
                    "email": [
                        "alice@example.com",
                        "bob@example.com",
                        "charlie@example.com",
                        "david@example.com",
                        "eve@example.com",
                    ],
                    "registration_date": pd.to_datetime(
                        [
                            "2023-10-01",
                            "2023-10-15",
                            "2023-11-01",
                            "2023-11-20",
                            "2023-12-05",
                        ]
                    ),
                }
            )

            # Register the pandas DataFrame as a temporary table/view in DuckDB.
            # This is a common and robust way to load DataFrames into DuckDB tables.
            con.register("temp_customers", customer_data)
            con.execute("INSERT INTO customers SELECT * FROM temp_customers;")
            con.unregister(
                "temp_customers"
            )  # Clean up the registered DataFrame (good practice)

            print("Sample customer data inserted.")
        else:
            print("Customers table already contains data. Skipping insertion.")

        # You can add more tables or data as needed.
        # For example, loading data from a CSV:
        # Assuming you have a 'products.csv' in your 'data' folder:
        # try:
        #     con.execute(f"CREATE TABLE IF NOT EXISTS products AS SELECT * FROM '{BASE_DATA_DIR / 'products.csv'}';")
        #     print("Table 'products' created from CSV.")
        # except duckdb.CatalogException:
        #     print(f"Could not create 'products' table. Ensure '{BASE_DATA_DIR / 'products.csv'}' exists.")
        # except Exception as e:
        #     print(f"An unexpected error occurred while creating 'products' table: {e}")

        # Close the connection to save changes to the DuckDB file
        con.close()
        print(f"Sample DuckDB database '{db_path}' created/updated successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        print(
            "Please ensure you have 'duckdb', 'pandas', and 'numpy' installed (`pip install duckdb pandas numpy`)."
        )
        print("Also verify the permissions for the 'data' directory.")


if __name__ == "__main__":
    create_sample_duckdb()
