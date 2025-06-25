#!/usr/bin/env python3
"""
Script to create sample CSV files that can be imported into DuckDB
"""
import csv
from pathlib import Path

def create_sample_csvs():
    """Create sample CSV files for the package"""
    
    data_dir = Path("mcp_visualization/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating sample CSV files...")
    
    # Sales data
    sales_data = [
        ["id", "product_name", "category", "sales_amount", "quantity", "sale_date", "region", "salesperson"],
        [1, "Laptop Pro", "Electronics", 1299.99, 2, "2024-01-15", "North", "Alice Johnson"],
        [2, "Wireless Mouse", "Electronics", 29.99, 15, "2024-01-16", "South", "Bob Smith"],
        [3, "Coffee Maker", "Appliances", 79.99, 8, "2024-01-17", "East", "Carol Davis"],
        [4, "Smartphone", "Electronics", 899.99, 12, "2024-01-18", "West", "David Wilson"],
        [5, "Desk Chair", "Furniture", 199.99, 5, "2024-01-19", "North", "Alice Johnson"],
        [6, "Monitor", "Electronics", 349.99, 7, "2024-01-20", "South", "Eve Brown"],
        [7, "Kitchen Blender", "Appliances", 89.99, 4, "2024-01-21", "East", "Frank Miller"],
        [8, "Bookshelf", "Furniture", 159.99, 3, "2024-01-22", "West", "Grace Taylor"],
        [9, "Tablet", "Electronics", 449.99, 9, "2024-01-23", "North", "Henry Lee"],
        [10, "Microwave", "Appliances", 129.99, 6, "2024-01-24", "South", "Ivy Chen"],
        [11, "Gaming Keyboard", "Electronics", 79.99, 11, "2024-01-25", "East", "Jack White"],
        [12, "Office Desk", "Furniture", 299.99, 4, "2024-01-26", "West", "Kate Green"],
        [13, "Smart Watch", "Electronics", 249.99, 8, "2024-01-27", "North", "Liam Black"],
        [14, "Air Fryer", "Appliances", 119.99, 7, "2024-01-28", "South", "Mia Gray"],
        [15, "Sofa", "Furniture", 799.99, 2, "2024-01-29", "East", "Noah Blue"]
    ]
    
    with open(data_dir / "sales_data.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(sales_data)
    
    # Customer data
    customer_data = [
        ["customer_id", "customer_name", "email", "age", "gender", "city", "state", "signup_date", "total_purchases", "loyalty_tier"],
        [1, "John Doe", "john.doe@email.com", 32, "Male", "New York", "NY", "2023-03-15", 2459.97, "Gold"],
        [2, "Jane Smith", "jane.smith@email.com", 28, "Female", "Los Angeles", "CA", "2023-05-20", 1879.94, "Silver"],
        [3, "Mike Johnson", "mike.j@email.com", 45, "Male", "Chicago", "IL", "2023-01-10", 3299.95, "Platinum"],
        [4, "Sarah Wilson", "sarah.w@email.com", 35, "Female", "Houston", "TX", "2023-07-08", 1599.98, "Silver"],
        [5, "David Brown", "david.b@email.com", 52, "Male", "Phoenix", "AZ", "2023-02-14", 1049.99, "Bronze"],
        [6, "Lisa Davis", "lisa.d@email.com", 29, "Female", "Philadelphia", "PA", "2023-06-25", 2199.96, "Gold"],
        [7, "Chris Miller", "chris.m@email.com", 38, "Male", "San Antonio", "TX", "2023-04-12", 899.99, "Bronze"],
        [8, "Amy Taylor", "amy.t@email.com", 41, "Female", "San Diego", "CA", "2023-08-30", 1749.97, "Silver"],
        [9, "Tom Anderson", "tom.a@email.com", 33, "Male", "Dallas", "TX", "2023-03-22", 1299.99, "Bronze"],
        [10, "Emma White", "emma.w@email.com", 26, "Female", "San Jose", "CA", "2023-09-15", 1949.98, "Gold"]
    ]
    
    with open(data_dir / "customer_data.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(customer_data)
    
    # Monthly revenue
    monthly_revenue = [
        ["month", "total_revenue", "orders_count", "avg_order_value", "new_customers", "returning_customers"],
        ["2023-01-01", 45000.00, 150, 300.00, 45, 105],
        ["2023-02-01", 52000.00, 173, 300.58, 38, 135],
        ["2023-03-01", 48000.00, 160, 300.00, 42, 118],
        ["2023-04-01", 61000.00, 203, 300.49, 55, 148],
        ["2023-05-01", 58000.00, 193, 300.52, 48, 145],
        ["2023-06-01", 65000.00, 217, 299.54, 62, 155],
        ["2023-07-01", 71000.00, 237, 299.58, 68, 169],
        ["2023-08-01", 69000.00, 230, 300.00, 59, 171],
        ["2023-09-01", 74000.00, 247, 299.59, 71, 176],
        ["2023-10-01", 78000.00, 260, 300.00, 75, 185],
        ["2023-11-01", 85000.00, 283, 300.35, 82, 201],
        ["2023-12-01", 92000.00, 307, 299.67, 89, 218]
    ]
    
    with open(data_dir / "monthly_revenue.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(monthly_revenue)
    
    # Product categories
    product_categories = [
        ["category", "total_sales", "units_sold", "avg_price", "profit_margin", "customer_rating"],
        ["Electronics", 234599.88, 1250, 187.68, 22.5, 4.2],
        ["Furniture", 189799.92, 485, 391.34, 35.2, 4.1],
        ["Appliances", 145699.95, 823, 177.06, 28.7, 4.3],
        ["Clothing", 98750.00, 1875, 52.67, 45.3, 3.9],
        ["Sports", 76890.50, 967, 79.51, 32.1, 4.0],
        ["Books", 45230.75, 2011, 22.50, 40.8, 4.4],
        ["Beauty", 67890.25, 1534, 44.26, 55.2, 4.1],
        ["Toys", 34567.80, 891, 38.79, 38.9, 4.2]
    ]
    
    with open(data_dir / "product_categories.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(product_categories)
    
    print("✅ Sample CSV files created:")
    for csv_file in data_dir.glob("*.csv"):
        print(f"   - {csv_file}")
    
    return True

if __name__ == "__main__":
    create_sample_csvs()
    print("\n🎉 Sample data creation complete!")
    print("📁 Files are ready for package distribution")