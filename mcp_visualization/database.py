"""
Database utilities for package installation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def create_sample_database(db_path: str):
    """Create a DuckDB database with sample data"""
    import duckdb
    
    db_path_obj = Path(db_path)
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = duckdb.connect(db_path)
    
    try:
        # Generate sample sales data
        np.random.seed(42)
        start_date = datetime(2023, 1, 1)
        dates = [start_date + timedelta(days=i) for i in range(365)]
        regions = ["North", "South", "East", "West"]
        products = ["Product A", "Product B", "Product C", "Product D"]
        
        sales_data = []
        for i, date in enumerate(dates):
            for region in regions:
                for product in products:
                    sales_data.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "region": region,
                        "product": product,
                        "sales_amount": np.random.normal(1000, 200),
                        "quantity": np.random.poisson(50),
                        "customer_count": np.random.poisson(25),
                    })
        
        sales_df = pd.DataFrame(sales_data)
        conn.execute("CREATE TABLE IF NOT EXISTS sales AS SELECT * FROM sales_df")
        
        # Generate sample customer data
        customer_data = []
        for i in range(1000):
            customer_data.append({
                "customer_id": f"C{i+1:04d}",
                "age": np.random.randint(18, 80),
                "gender": np.random.choice(["M", "F"]),
                "segment": np.random.choice(["Premium", "Standard", "Basic"]),
                "lifetime_value": np.random.exponential(2000),
                "region": np.random.choice(regions),
            })
        
        customers_df = pd.DataFrame(customer_data)
        conn.execute("CREATE TABLE IF NOT EXISTS customers AS SELECT * FROM customers_df")
        
        # Generate sample product data
        categories = ["Electronics", "Clothing", "Home", "Sports"]
        products_data = []
        for i in range(100):
            products_data.append({
                "product_id": f"P{i+1:04d}",
                "product_name": f"Product {i+1}",
                "category": np.random.choice(categories),
                "price": np.random.uniform(10, 1000),
                "cost": np.random.uniform(5, 500),
                "weight": np.random.uniform(0.1, 10),
                "rating": np.random.uniform(1, 5),
            })
        
        products_df = pd.DataFrame(products_data)
        conn.execute("CREATE TABLE IF NOT EXISTS products AS SELECT * FROM products_df")
        
        logger.info(f"Created sample database with 3 tables at {db_path}")
        
    finally:
        conn.close()