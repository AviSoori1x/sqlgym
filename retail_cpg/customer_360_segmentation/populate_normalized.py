#!/usr/bin/env python3
"""Populate customer 360 segmentation normalized schema with synthetic data."""
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
CUSTOMERS = 5000
TRANSACTIONS_PER_CUSTOMER = 12
INTERACTIONS_PER_CUSTOMER = 25

# Customer segments
SEGMENT_DEFINITIONS = [
    ('Young Professionals', 'DEMOGRAPHIC', {'age_min': 25, 'age_max': 35}, 8),
    ('High Value', 'VALUE', {'lifetime_value_min': 5000}, 10),
    ('Frequent Buyers', 'VALUE', {'transactions_per_month_min': 3}, 8),
    ('Omnichannel', 'BEHAVIORAL', {'channels_used_min': 3}, 9),
    ('New Customers', 'LIFECYCLE', {'days_since_registration_max': 90}, 8),
    ('At Risk', 'LIFECYCLE', {'days_since_last_purchase_min': 180}, 9),
    ('Champions', 'LIFECYCLE', {'recency_score_min': 8}, 10),
]

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
    channels = ['ORGANIC', 'PAID_SEARCH', 'SOCIAL', 'EMAIL', 'REFERRAL', 'DIRECT']
    
    for i in range(1, CUSTOMERS + 1):
        age = rng.randint(18, 80)
        birth_date = (datetime.now() - timedelta(days=age * 365)).strftime('%Y-%m-%d')
        reg_days_ago = rng.randint(1, 1095)
        reg_date = (datetime.now() - timedelta(days=reg_days_ago)).strftime('%Y-%m-%d')
        
        customers_data.append((
            i, f'customer{i}@example.com', f'Customer{i}', f'User{i}',
            birth_date, rng.choice(['M', 'F', 'OTHER']), reg_date,
            rng.choice(channels), rng.randint(1, 100),
            rng.choices(['ACTIVE', 'INACTIVE', 'CHURNED'], weights=[0.75, 0.20, 0.05])[0]
        ))
    
    conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?,?)", customers_data)
    
    # Insert segments
    print("Inserting segments...")
    segments_data = []
    for i, (name, seg_type, criteria, priority) in enumerate(SEGMENT_DEFINITIONS, 1):
        segments_data.append((i, name, seg_type, json.dumps(criteria), priority))
    
    conn.executemany("INSERT INTO customer_segments VALUES (?,?,?,?,?)", segments_data)
    
    # Insert transactions
    print("Inserting transactions...")
    transactions_data = []
    transaction_id = 1
    
    for customer_id in range(1, CUSTOMERS + 1):
        customer = customers_data[customer_id - 1]
        reg_date = datetime.strptime(customer[6], '%Y-%m-%d')
        
        num_transactions = rng.randint(1, TRANSACTIONS_PER_CUSTOMER)
        for _ in range(num_transactions):
            days_offset = rng.randint(0, min(365, (datetime.now() - reg_date).days))
            trans_date = reg_date + timedelta(days=days_offset)
            
            if trans_date <= datetime.now():
                channel = rng.choice(['STORE', 'ONLINE', 'MOBILE_APP', 'PHONE'])
                amount = rng.uniform(25, 500)
                discount = rng.uniform(0, amount * 0.2) if rng.random() < 0.3 else 0
                
                transactions_data.append((
                    transaction_id, customer_id, trans_date.strftime('%Y-%m-%d %H:%M:%S'),
                    channel, rng.randint(1, 50) if channel == 'STORE' else None,
                    round(amount, 2), round(discount, 2),
                    rng.choice(['CASH', 'CREDIT', 'DEBIT', 'DIGITAL_WALLET'])
                ))
                transaction_id += 1
    
    for chunk in batch(transactions_data, 1000):
        conn.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    # Insert interactions
    print("Inserting interactions...")
    interactions_data = []
    interaction_id = 1
    
    for customer_id in range(1, CUSTOMERS + 1):
        customer = customers_data[customer_id - 1]
        reg_date = datetime.strptime(customer[6], '%Y-%m-%d')
        
        num_interactions = rng.randint(5, INTERACTIONS_PER_CUSTOMER)
        for _ in range(num_interactions):
            days_offset = rng.randint(0, (datetime.now() - reg_date).days)
            interaction_date = reg_date + timedelta(days=days_offset)
            
            if interaction_date <= datetime.now():
                int_type = rng.choice(['PURCHASE', 'BROWSE', 'SUPPORT', 'REVIEW', 'EMAIL_OPEN'])
                channel = rng.choice(['WEB', 'MOBILE', 'STORE', 'EMAIL', 'SOCIAL'])
                
                interactions_data.append((
                    interaction_id, customer_id, interaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                    int_type, channel, json.dumps({'value': rng.randint(1, 100)}),
                    f'sess_{customer_id}_{interaction_id}' if rng.random() < 0.7 else None
                ))
                interaction_id += 1
    
    for chunk in batch(interactions_data, 1000):
        conn.executemany("INSERT INTO customer_interactions VALUES (?,?,?,?,?,?,?)", chunk)
    
    # Insert preferences
    print("Inserting preferences...")
    preferences_data = []
    pref_id = 1
    
    categories = ['Electronics', 'Clothing', 'Home', 'Sports']
    for customer_id in range(1, CUSTOMERS + 1):
        # 1-2 category preferences per customer
        for category in rng.sample(categories, rng.randint(1, 2)):
            preferences_data.append((
                pref_id, customer_id, 'CATEGORY', category,
                rng.uniform(0.5, 1.0),
                (datetime.now() - timedelta(days=rng.randint(1, 365))).strftime('%Y-%m-%d')
            ))
            pref_id += 1
        
        # Communication preference
        preferences_data.append((
            pref_id, customer_id, 'COMMUNICATION',
            rng.choice(['EMAIL', 'SMS', 'PUSH']),
            rng.uniform(0.7, 1.0),
            (datetime.now() - timedelta(days=rng.randint(1, 90))).strftime('%Y-%m-%d')
        ))
        pref_id += 1
    
    for chunk in batch(preferences_data, 1000):
        conn.executemany("INSERT INTO customer_preferences VALUES (?,?,?,?,?,?)", chunk)
    
    # Assign segments
    print("Assigning segments...")
    assignments_data = []
    assignment_id = 1
    
    for customer_id in range(1, CUSTOMERS + 1):
        # Assign to 1-2 segments randomly
        num_segments = rng.randint(1, 2)
        selected_segments = rng.sample(range(1, len(SEGMENT_DEFINITIONS) + 1), num_segments)
        
        for segment_id in selected_segments:
            assigned_date = (datetime.now() - timedelta(days=rng.randint(1, 90))).strftime('%Y-%m-%d')
            expires_date = (datetime.now() + timedelta(days=rng.randint(90, 365))).strftime('%Y-%m-%d')
            
            assignments_data.append((
                assignment_id, customer_id, segment_id, assigned_date,
                rng.uniform(0.5, 1.0), expires_date
            ))
            assignment_id += 1
    
    for chunk in batch(assignments_data, 1000):
        conn.executemany("INSERT INTO customer_segment_assignments VALUES (?,?,?,?,?,?)", chunk)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_registration ON customers(registration_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_segment_assignments_customer ON customer_segment_assignments(customer_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_customer_date ON customer_interactions(customer_id, interaction_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_preferences_customer ON customer_preferences(customer_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
