#!/usr/bin/env python3
"""Populate merchandising planograms normalized schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

# Scale constants
STORES = 50
CATEGORIES = 20
PRODUCTS = 500
PLANOGRAMS = 100
SALES_DAYS = 90

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert stores
    print(f"Inserting {STORES} stores...")
    stores_data = []
    formats = ['SUPERMARKET', 'CONVENIENCE', 'HYPERMARKET', 'SPECIALTY', 'DISCOUNT']
    
    for i in range(1, STORES + 1):
        store_format = rng.choice(formats)
        
        # Store size varies by format
        size_ranges = {
            'CONVENIENCE': (1000, 3000),
            'SPECIALTY': (2000, 8000), 
            'DISCOUNT': (5000, 15000),
            'SUPERMARKET': (15000, 40000),
            'HYPERMARKET': (50000, 120000)
        }
        
        square_footage = rng.randint(*size_ranges[store_format])
        opened_date = (datetime.now() - timedelta(days=rng.randint(365, 3650))).strftime('%Y-%m-%d')
        
        stores_data.append((
            i, f'ST{i:03d}', f'Store {i}', store_format,
            f'City {i}, State', square_footage, opened_date
        ))
    
    conn.executemany("INSERT INTO stores VALUES (?,?,?,?,?,?,?)", stores_data)
    
    # Insert product categories
    print("Inserting product categories...")
    categories_data = [
        (1, 'Food & Beverage', None, 1, 60.0),
        (2, 'Fresh Foods', 1, 2, 25.0),
        (3, 'Packaged Foods', 1, 2, 20.0),
        (4, 'Beverages', 1, 2, 15.0),
        (5, 'Dairy', 2, 3, 8.0),
        (6, 'Meat & Seafood', 2, 3, 10.0),
        (7, 'Produce', 2, 3, 7.0),
        (8, 'Snacks', 3, 3, 8.0),
        (9, 'Cereal', 3, 3, 5.0),
        (10, 'Canned Goods', 3, 3, 7.0),
        (11, 'Health & Beauty', None, 1, 15.0),
        (12, 'Personal Care', 11, 2, 8.0),
        (13, 'Pharmacy', 11, 2, 7.0),
        (14, 'Household', None, 1, 12.0),
        (15, 'Cleaning Supplies', 14, 2, 6.0),
        (16, 'Paper Products', 14, 2, 6.0),
        (17, 'General Merchandise', None, 1, 13.0),
        (18, 'Electronics', 17, 2, 5.0),
        (19, 'Clothing', 17, 2, 4.0),
        (20, 'Home Goods', 17, 2, 4.0)
    ]
    
    conn.executemany("INSERT INTO product_categories VALUES (?,?,?,?,?)", categories_data)
    
    # Insert products
    print(f"Inserting {PRODUCTS} products...")
    products_data = []
    brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE', 'Generic', 'Premium', 'Store Brand']
    
    for i in range(1, PRODUCTS + 1):
        # Assign to leaf categories (level 3)
        leaf_categories = [c[0] for c in categories_data if c[2] is not None and c[3] == 3]
        category_id = rng.choice(leaf_categories)
        
        brand = rng.choice(brands)
        unit_cost = rng.uniform(0.50, 20.00)
        retail_price = unit_cost * rng.uniform(1.5, 3.0)
        
        dimensions = {
            'length': rng.uniform(2, 12),
            'width': rng.uniform(2, 8), 
            'height': rng.uniform(1, 6)
        }
        
        velocity = rng.choices(['A', 'B', 'C', 'D'], weights=[0.2, 0.3, 0.3, 0.2])[0]
        
        products_data.append((
            i, f'SKU{i:06d}', f'Product {i}', category_id, brand,
            round(unit_cost, 2), round(retail_price, 2),
            json.dumps(dimensions), velocity
        ))
    
    for chunk in batch(products_data, 1000):
        conn.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert planograms
    print(f"Inserting {PLANOGRAMS} planograms...")
    planograms_data = []
    
    for i in range(1, PLANOGRAMS + 1):
        store_id = rng.randint(1, STORES)
        # Focus on leaf categories
        leaf_categories = [c[0] for c in categories_data if c[2] is not None and c[3] == 3]
        category_id = rng.choice(leaf_categories)
        
        effective_date = (datetime.now() - timedelta(days=rng.randint(0, 180))).strftime('%Y-%m-%d')
        expiry_date = (datetime.now() + timedelta(days=rng.randint(30, 365))).strftime('%Y-%m-%d')
        
        total_facings = rng.randint(20, 200)
        shelf_count = rng.randint(3, 8)
        status = rng.choices(['ACTIVE', 'APPROVED', 'DRAFT'], weights=[0.7, 0.2, 0.1])[0]
        
        planograms_data.append((
            i, f'Planogram_{i}', store_id, category_id, effective_date,
            expiry_date, total_facings, shelf_count, status
        ))
    
    conn.executemany("INSERT INTO planograms VALUES (?,?,?,?,?,?,?,?,?)", planograms_data)
    
    # Insert product placements
    print("Inserting product placements...")
    placements_data = []
    placement_id = 1
    
    for planogram in planograms_data:
        planogram_id = planogram[0]
        category_id = planogram[3]
        total_facings = planogram[6]
        shelf_count = planogram[7]
        
        # Get products in this category
        category_products = [p for p in products_data if p[3] == category_id]
        
        if not category_products:
            continue
        
        # Select subset of products for this planogram
        num_products = min(rng.randint(5, 20), len(category_products))
        selected_products = rng.sample(category_products, num_products)
        
        # Allocate facings
        facings_per_product = max(1, total_facings // len(selected_products))
        current_position = 1
        
        for product in selected_products:
            product_id = product[0]
            velocity = product[8]
            
            # A/B velocity products get more facings and better positions
            if velocity == 'A':
                facings = facings_per_product * 2
                eye_level = rng.random() < 0.6
            elif velocity == 'B':
                facings = facings_per_product
                eye_level = rng.random() < 0.4
            else:
                facings = max(1, facings_per_product // 2)
                eye_level = rng.random() < 0.2
            
            shelf_num = rng.randint(1, shelf_count)
            end_cap = rng.random() < 0.1  # 10% chance
            
            placements_data.append((
                placement_id, planogram_id, product_id, shelf_num,
                current_position, current_position + facings - 1,
                facings, eye_level, end_cap
            ))
            
            current_position += facings
            placement_id += 1
    
    for chunk in batch(placements_data, 1000):
        conn.executemany("INSERT INTO product_placements VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert sales performance
    print("Inserting sales performance...")
    sales_data = []
    sales_id = 1
    
    # Generate sales for each store-product-day combination
    for store_id in range(1, STORES + 1):
        # Get products placed in this store's planograms
        store_planograms = [p[0] for p in planograms_data if p[2] == store_id]
        store_products = set()
        
        for placement in placements_data:
            if placement[1] in store_planograms:  # planogram_id
                store_products.add(placement[2])  # product_id
        
        # Generate daily sales for last 90 days
        for days_ago in range(SALES_DAYS):
            date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            for product_id in list(store_products)[:100]:  # Limit for performance
                product = products_data[product_id - 1]
                velocity = product[8]
                retail_price = product[6]
                
                # Sales vary by velocity
                if velocity == 'A':
                    units_sold = rng.randint(5, 50)
                elif velocity == 'B':
                    units_sold = rng.randint(2, 20)
                elif velocity == 'C':
                    units_sold = rng.randint(0, 10)
                else:  # D
                    units_sold = rng.randint(0, 3)
                
                revenue = units_sold * retail_price
                inventory = rng.randint(0, 100)
                out_of_stock = rng.randint(0, 4) if inventory == 0 else 0
                
                sales_data.append((
                    sales_id, store_id, product_id, date, units_sold,
                    round(revenue, 2), inventory, out_of_stock
                ))
                sales_id += 1
    
    for chunk in batch(sales_data, 1000):
        conn.executemany("INSERT INTO sales_performance VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_kv (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_stores_format ON stores(store_format)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_products_velocity ON products(velocity_rank)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_planograms_store ON planograms(store_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_product_placements_planogram ON product_placements(planogram_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_performance_store_date ON sales_performance(store_id, date)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()