#!/usr/bin/env python3
"""Populate returns RMA support normalized schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

# Scale constants
CUSTOMERS = 4000
PRODUCTS = 500
ORDERS = 40000
ITEMS_PER_ORDER = 3
RETURN_RATE = 0.08

# Product catalog
PRODUCT_TEMPLATES = {
    'ELECTRONICS': [
        ('Smartphone', 599, 365),
        ('Laptop', 999, 730),
        ('Headphones', 149, 365),
        ('Tablet', 399, 365),
        ('Smart Watch', 299, 365),
        ('Camera', 799, 730),
        ('Gaming Console', 499, 365),
        ('Monitor', 349, 730)
    ],
    'APPAREL': [
        ('T-Shirt', 29, 90),
        ('Jeans', 79, 90),
        ('Sneakers', 99, 180),
        ('Jacket', 149, 90),
        ('Dress', 89, 90),
        ('Sweater', 69, 90)
    ],
    'HOME': [
        ('Coffee Maker', 89, 365),
        ('Vacuum Cleaner', 199, 730),
        ('Air Purifier', 249, 730),
        ('Blender', 79, 365),
        ('Toaster', 49, 365)
    ],
    'SPORTS': [
        ('Yoga Mat', 39, 180),
        ('Dumbbells', 69, 365),
        ('Running Shoes', 119, 180),
        ('Fitness Tracker', 149, 365)
    ],
    'TOYS': [
        ('Building Blocks', 49, 90),
        ('Board Game', 39, 90),
        ('Remote Control Car', 79, 180),
        ('Puzzle', 29, 90)
    ],
    'BEAUTY': [
        ('Face Cream', 59, 180),
        ('Hair Dryer', 89, 365),
        ('Makeup Set', 79, 180),
        ('Perfume', 99, 365)
    ]
}

def get_return_reason(product_category, days_since_purchase):
    """Determine return reason based on product and timing."""
    if days_since_purchase <= 1:
        reasons = ['WRONG_ITEM', 'DAMAGED', 'NOT_AS_DESCRIBED']
        weights = [0.3, 0.4, 0.3]
    elif days_since_purchase <= 7:
        if product_category == 'ELECTRONICS':
            reasons = ['DEFECTIVE', 'NOT_AS_DESCRIBED', 'CHANGED_MIND']
            weights = [0.4, 0.3, 0.3]
        else:
            reasons = ['NOT_AS_DESCRIBED', 'CHANGED_MIND', 'BETTER_PRICE']
            weights = [0.3, 0.4, 0.3]
    elif days_since_purchase <= 30:
        reasons = ['DEFECTIVE', 'CHANGED_MIND', 'BETTER_PRICE', 'OTHER']
        weights = [0.3, 0.3, 0.2, 0.2]
    else:
        reasons = ['DEFECTIVE', 'OTHER']
        weights = [0.7, 0.3]
    
    return random.choices(reasons, weights=weights)[0]

def get_inspection_result(return_reason, days_since_purchase, product_category):
    """Determine inspection outcome based on return details."""
    if return_reason in ['DEFECTIVE', 'DAMAGED']:
        condition = random.choice(['POOR', 'DAMAGED', 'FAIR'])
        functionality = random.choice(['NOT_WORKING', 'PARTIALLY_WORKING'])
        recommendation = 'FULL_REFUND' if functionality == 'NOT_WORKING' else 'EXCHANGE'
        deduction = 0
    elif return_reason == 'WRONG_ITEM':
        condition = 'NEW'
        functionality = 'NOT_TESTED'
        recommendation = 'FULL_REFUND'
        deduction = 0
    elif return_reason == 'CHANGED_MIND':
        if days_since_purchase <= 14:
            condition = random.choice(['NEW', 'LIKE_NEW'])
            functionality = 'WORKING'
            recommendation = 'FULL_REFUND'
            deduction = 0 if condition == 'NEW' else 10
        else:
            condition = random.choice(['GOOD', 'FAIR'])
            functionality = 'WORKING'
            recommendation = 'PARTIAL_REFUND'
            deduction = random.choice([15, 20, 25])
    else:
        condition = random.choice(['GOOD', 'FAIR', 'POOR'])
        functionality = random.choice(['WORKING', 'PARTIALLY_WORKING'])
        recommendation = random.choice(['PARTIAL_REFUND', 'EXCHANGE', 'REJECT'])
        deduction = random.choice([0, 10, 20, 30])
    
    return condition, functionality, recommendation, deduction

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert customers
    print(f"Inserting {CUSTOMERS} customers...")
    customers_data = []
    tiers = ['BASIC', 'SILVER', 'GOLD', 'PLATINUM']
    tier_weights = [0.50, 0.30, 0.15, 0.05]
    
    for i in range(1, CUSTOMERS + 1):
        tier = rng.choices(tiers, weights=tier_weights)[0]
        # Lifetime value correlates with tier
        ltv_ranges = {
            'BASIC': (100, 1000),
            'SILVER': (1000, 5000),
            'GOLD': (5000, 20000),
            'PLATINUM': (20000, 100000)
        }
        lifetime_value = rng.randint(*ltv_ranges[tier])
        
        customers_data.append((
            i,
            f'customer{i}@example.com',
            f'Customer {i}',
            tier,
            lifetime_value
        ))
    
    for chunk in batch(customers_data, 1000):
        conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", chunk)
    
    # Insert products
    print(f"Inserting products...")
    products_data = []
    product_id = 1
    
    for category, items in PRODUCT_TEMPLATES.items():
        for base_name, base_price, warranty in items:
            # Create variants
            variants = ['Standard', 'Pro', 'Plus', 'Premium'] if category == 'ELECTRONICS' else ['S', 'M', 'L', 'XL']
            for variant in variants[:rng.randint(1, len(variants))]:
                name = f'{base_name} {variant}'
                sku = f'{category[:3]}-{product_id:04d}'
                price = base_price * (1 + rng.uniform(-0.2, 0.3))
                returnable = 0 if rng.random() < 0.05 else 1  # 5% non-returnable
                
                products_data.append((
                    product_id,
                    sku,
                    name,
                    category,
                    round(price, 2),
                    warranty,
                    returnable
                ))
                product_id += 1
    
    conn.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?)", products_data)
    
    # Insert orders and order items
    print(f"Inserting {ORDERS} orders...")
    orders_data = []
    order_items_data = []
    
    order_id = 1
    item_id = 1
    base_date = datetime(2023, 1, 1)
    
    for _ in range(ORDERS):
        customer_id = rng.randint(1, CUSTOMERS)
        order_date = base_date + timedelta(days=rng.randint(0, 365))
        
        # Order status based on age
        days_old = (datetime.now() - order_date).days
        if days_old < 3:
            status = rng.choice(['PENDING', 'SHIPPED'])
        elif days_old < 7:
            status = rng.choice(['SHIPPED', 'DELIVERED'])
        else:
            status = 'DELIVERED'
        
        # Generate order items
        num_items = rng.randint(1, ITEMS_PER_ORDER)
        selected_products = rng.sample(products_data, num_items)
        
        total_amount = 0
        for product in selected_products:
            quantity = rng.randint(1, 3)
            unit_price = product[4]
            discount = rng.choice([0, 0, 0, 5, 10, 15])  # Most items no discount
            discount_amount = unit_price * quantity * discount / 100
            
            order_items_data.append((
                item_id,
                order_id,
                product[0],  # product_id
                quantity,
                unit_price,
                discount_amount
            ))
            
            total_amount += (unit_price * quantity - discount_amount)
            item_id += 1
        
        orders_data.append((
            order_id,
            customer_id,
            order_date.strftime('%Y-%m-%d'),
            round(total_amount, 2),
            f'{rng.randint(100, 9999)} Main St, City {rng.randint(10000, 99999)}',
            status
        ))
        order_id += 1
    
    for chunk in batch(orders_data, 1000):
        conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", chunk)
    
    for chunk in batch(order_items_data, 1000):
        conn.executemany("INSERT INTO order_items VALUES (?,?,?,?,?,?)", chunk)
    
    # Insert RMA requests and inspections
    print("Inserting RMA requests...")
    rma_data = []
    inspection_data = []
    
    rma_id = 1
    inspection_id = 1
    
    # Select items to return based on return rate
    returnable_items = [
        item for item in order_items_data
        if rng.random() < RETURN_RATE
    ]
    
    for item in returnable_items:
        item_id = item[0]
        order_id = item[1]
        product_id = item[2]
        
        # Get order and product details
        order = orders_data[order_id-1]
        product = products_data[product_id-1]
        
        # Skip if order not delivered or product not returnable
        if order[5] != 'DELIVERED' or not product[6]:
            continue
        
        customer_id = order[1]
        order_date = datetime.strptime(order[2], '%Y-%m-%d')
        
        # Return timing
        days_to_return = rng.randint(1, min(90, product[5]))  # Within warranty
        request_date = order_date + timedelta(days=days_to_return)
        
        # Skip future dates
        if request_date > datetime.now():
            continue
        
        return_reason = get_return_reason(product[3], days_to_return)
        
        # RMA workflow status
        if (datetime.now() - request_date).days < 2:
            status = 'PENDING'
        elif (datetime.now() - request_date).days < 4:
            status = rng.choice(['APPROVED', 'REJECTED'])
        elif (datetime.now() - request_date).days < 7:
            status = rng.choice(['SHIPPED', 'RECEIVED'])
        else:
            status = rng.choice(['INSPECTED', 'PROCESSED', 'CLOSED'])
        
        # Return method based on tier
        customer_tier = customers_data[customer_id-1][3]
        if customer_tier in ['GOLD', 'PLATINUM']:
            return_method = rng.choice(['PREPAID_LABEL', 'PICKUP'])
        else:
            return_method = rng.choice(['PREPAID_LABEL', 'CUSTOMER_SHIP', 'DROP_OFF'])
        
        tracking = f'RMA{rma_id:06d}' if status not in ['PENDING', 'REJECTED'] else None
        
        rma_data.append((
            rma_id,
            item_id,
            customer_id,
            request_date.strftime('%Y-%m-%d'),
            return_reason,
            status,
            return_method if status != 'REJECTED' else None,
            tracking,
            f'Return reason: {return_reason}'
        ))
        
        # Create inspection if item was received
        if status in ['INSPECTED', 'PROCESSED', 'CLOSED']:
            inspection_date = request_date + timedelta(days=rng.randint(5, 10))
            condition, functionality, recommendation, deduction = get_inspection_result(
                return_reason, days_to_return, product[3]
            )
            
            inspection_data.append((
                inspection_id,
                rma_id,
                inspection_date.strftime('%Y-%m-%d'),
                f'Inspector_{rng.randint(1, 20)}',
                condition,
                functionality,
                recommendation,
                deduction
            ))
            inspection_id += 1
        
        rma_id += 1
    
    for chunk in batch(rma_data, 1000):
        conn.executemany("INSERT INTO rma_requests VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(inspection_data, 500):
        conn.executemany("INSERT INTO rma_inspections VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_kv (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    conn.commit()
    
    # Create indexes after bulk loading
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(loyalty_tier)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rma_customer ON rma_requests(customer_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rma_status ON rma_requests(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rma_date ON rma_requests(request_date)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()