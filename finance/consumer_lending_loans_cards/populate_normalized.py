#!/usr/bin/env python3
"""Populate consumer lending normalized schema with synthetic data."""
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
CUSTOMERS = 1500
APPLICATIONS_PER_CUSTOMER = 2
TRANSACTIONS_PER_CARD = 150

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
    emp_statuses = ['EMPLOYED', 'SELF_EMPLOYED', 'UNEMPLOYED', 'RETIRED', 'STUDENT']
    
    for i in range(1, CUSTOMERS + 1):
        credit_score = rng.randint(450, 850)
        income_levels = {
            (450, 580): (20000, 40000),
            (580, 670): (35000, 75000),
            (670, 740): (60000, 120000),
            (740, 800): (90000, 250000),
            (800, 851): (150000, 500000)  # Fixed: 851 instead of 850 to include 850
        }
        matching_ranges = [v for k, v in income_levels.items() if k[0] <= credit_score < k[1]]
        if not matching_ranges:
            # Fallback for edge cases
            matching_ranges = [(50000, 100000)]
        income = rng.uniform(*matching_ranges[0])
        
        customers_data.append((
            i, f'CUST{i:05d}', f'Customer', f'{i}',
            (datetime(2000, 1, 1) - timedelta(days=rng.randint(0, 30*365))).strftime('%Y-%m-%d'),
            f'{i} Main St, City', credit_score, round(income, 2), rng.choice(emp_statuses)
        ))
    
    conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?)", customers_data)
    
    # Insert loan products
    print("Inserting loan products...")
    products_data = [
        (1, 'Personal Loan Plus', 'PERSONAL_LOAN', 660, 50000, json.dumps([5.99, 19.99]), json.dumps([24, 60]), 1),
        (2, 'Auto Loan Express', 'AUTO_LOAN', 620, 75000, json.dumps([3.99, 15.99]), json.dumps([36, 84]), 1),
        (3, 'Cashback Rewards Card', 'CREDIT_CARD', 680, 25000, json.dumps([14.99, 24.99]), json.dumps([0, 0]), 1),
        (4, 'Student Loan Starter', 'STUDENT_LOAN', 600, 100000, json.dumps([2.75, 7.50]), json.dumps([60, 120]), 1),
        (5, 'Low APR Card', 'CREDIT_CARD', 720, 50000, json.dumps([9.99, 18.99]), json.dumps([0, 0]), 1)
    ]
    conn.executemany("INSERT INTO loan_products VALUES (?,?,?,?,?,?,?,?)", products_data)
    
    # Insert loan applications, loans, payments, cards, and card transactions
    print("Generating financial histories...")
    applications_data, loans_data, payments_data, cards_data, card_transactions_data = [], [], [], [], []
    app_id, loan_id, payment_id, card_id, trans_id = 1, 1, 1, 1, 1
    
    for cust in customers_data:
        cust_id, credit_score = cust[0], cust[6]
        
        for _ in range(rng.randint(1, APPLICATIONS_PER_CUSTOMER)):
            eligible_products = [p for p in products_data if p[3] <= credit_score]
            if not eligible_products:
                continue  # Skip if no eligible products for this credit score
            product = rng.choice(eligible_products)
            
            # Application
            status = rng.choices(['APPROVED', 'REJECTED', 'PENDING'], [0.6, 0.3, 0.1])[0]
            req_amt = rng.uniform(1000, product[4])
            
            applications_data.append((
                app_id, cust_id, product[0], (datetime.now() - timedelta(days=rng.randint(10, 730))).strftime('%Y-%m-%d'),
                round(req_amt, 2), rng.choice(json.loads(product[6])), status,
                round(req_amt * 0.9, 2) if status == 'APPROVED' else None,
                rng.uniform(*json.loads(product[5])) if status == 'APPROVED' else None,
                (datetime.now() - timedelta(days=rng.randint(5, 9))).strftime('%Y-%m-%d') if status != 'PENDING' else None,
                f'UW_{rng.randint(1, 10)}'
            ))
            
            if status == 'APPROVED':
                # Loan/Card creation
                if product[2] == 'CREDIT_CARD':
                    # It's a "loan" in our system to track balance
                    loan_status = 'ACTIVE'
                    balance = rng.uniform(0, req_amt * 0.9)
                else:
                    loan_status = rng.choices(['ACTIVE', 'PAID_OFF', 'DEFAULT'], [0.7, 0.2, 0.1])[0]
                    balance = 0 if loan_status == 'PAID_OFF' else rng.uniform(0, req_amt * 0.9)

                origination_date = datetime.strptime(applications_data[-1][9], '%Y-%m-%d')
                term = applications_data[-1][5]
                maturity_date = origination_date + timedelta(days=term*30)
                
                loans_data.append((
                    loan_id, app_id, cust_id, product[0], applications_data[-1][7],
                    applications_data[-1][8], term, origination_date.strftime('%Y-%m-%d'),
                    maturity_date.strftime('%Y-%m-%d'), loan_status,
                    round(balance, 2), rng.randint(0, 90) if loan_status == 'DEFAULT' else 0
                ))
                
                if product[2] == 'CREDIT_CARD':
                    cards_data.append((
                        card_id, loan_id, f'4_..._{card_id:04d}', applications_data[-1][7],
                        applications_data[-1][7] * 0.3, 'REWARDS' if 'Rewards' in product[1] else 'LOW_APR',
                        origination_date.strftime('%Y-%m-%d'), (origination_date + timedelta(days=365*4)).strftime('%Y-%m-%d'),
                        'ACTIVE'
                    ))
                    
                    # Card transactions
                    for _ in range(rng.randint(50, TRANSACTIONS_PER_CARD)):
                        card_transactions_data.append((
                            trans_id, card_id, (origination_date + timedelta(days=rng.randint(1, 365))).strftime('%Y-%m-%d'),
                            f'Merchant_{rng.randint(1, 100)}', 'RETAIL', rng.uniform(10, 500), 'PURCHASE'
                        ))
                        trans_id += 1
                    card_id += 1
                else:
                    # Loan payments
                    num_payments = rng.randint(1, term)
                    for _ in range(num_payments):
                        payment_amount = applications_data[-1][7] / term
                        payments_data.append((
                            payment_id, loan_id, (origination_date + timedelta(days=rng.randint(1, term*30))).strftime('%Y-%m-%d'),
                            payment_amount, payment_amount * 0.7, payment_amount * 0.3, 0, 'AUTO_DEBIT'
                        ))
                        payment_id += 1
                loan_id += 1
            app_id += 1

    # Batch inserts
    conn.executemany("INSERT INTO loan_applications VALUES (?,?,?,?,?,?,?,?,?,?,?)", applications_data)
    conn.executemany("INSERT INTO loans VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", loans_data)
    conn.executemany("INSERT INTO loan_payments VALUES (?,?,?,?,?,?,?,?)", payments_data)
    conn.executemany("INSERT INTO credit_cards VALUES (?,?,?,?,?,?,?,?,?)", cards_data)
    conn.executemany("INSERT INTO card_transactions VALUES (?,?,?,?,?,?,?)", card_transactions_data)
    
    # Create evidence table and indexes
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    conn.commit()
    
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_credit_score ON customers(credit_score)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_loan_applications_status ON loan_applications(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_card_transactions_date ON card_transactions(transaction_date)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
