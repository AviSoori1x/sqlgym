#!/usr/bin/env python3
"""Populate mortgage servicing normalized schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

# Scale constants
BORROWERS = 2000
PAYMENTS_PER_LOAN = 36

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert borrowers
    print(f"Inserting {BORROWERS} borrowers...")
    borrowers_data = []
    for i in range(1, BORROWERS + 1):
        birth_date = (datetime.now() - timedelta(days=rng.randint(25*365, 70*365))).strftime('%Y-%m-%d')
        ssn_hash = hashlib.md5(f"SSN{i:06d}".encode()).hexdigest()
        
        borrowers_data.append((
            i, f'BOR{i:06d}', f'FirstName{i}', f'LastName{i}',
            birth_date, ssn_hash, f'{i} Main Street', f'555-{i:04d}',
            f'borrower{i}@email.com', rng.choice(['EMPLOYED', 'SELF_EMPLOYED', 'RETIRED'])
        ))
    
    conn.executemany("INSERT INTO borrowers VALUES (?,?,?,?,?,?,?,?,?,?)", borrowers_data)
    
    # Insert properties
    print("Inserting properties...")
    properties_data = []
    states = ['CA', 'TX', 'FL', 'NY', 'PA']
    
    for i in range(1, BORROWERS + 1):
        state = rng.choice(states)
        prop_type = rng.choices(['SINGLE_FAMILY', 'CONDO', 'TOWNHOUSE'], weights=[0.7, 0.2, 0.1])[0]
        
        # Property values vary by state
        if state == 'CA':
            base_value = rng.uniform(500000, 1200000)
        elif state == 'NY':
            base_value = rng.uniform(400000, 900000)
        else:
            base_value = rng.uniform(200000, 600000)
        
        properties_data.append((
            i, f'{i} Property Lane', f'City{i}', state, f'{10000+i}',
            prop_type, rng.randint(1000, 3000), rng.randint(1980, 2020),
            round(base_value, 2), (datetime.now() - timedelta(days=rng.randint(30, 365))).strftime('%Y-%m-%d')
        ))
    
    conn.executemany("INSERT INTO properties VALUES (?,?,?,?,?,?,?,?,?,?)", properties_data)
    
    # Insert mortgage loans
    print("Inserting mortgage loans...")
    loans_data = []
    
    for i in range(1, BORROWERS + 1):
        property_value = properties_data[i-1][8]
        loan_type = rng.choices(['CONVENTIONAL', 'FHA', 'VA'], weights=[0.6, 0.3, 0.1])[0]
        
        # LTV varies by loan type
        if loan_type == 'FHA':
            ltv = rng.uniform(0.85, 0.965)
        elif loan_type == 'VA':
            ltv = rng.uniform(0.90, 1.0)
        else:
            ltv = rng.uniform(0.60, 0.80)
        
        original_amount = property_value * ltv
        interest_rate = rng.uniform(3.0, 7.5)
        term_months = rng.choice([360, 240, 180])
        
        origination_date = datetime.now() - timedelta(days=rng.randint(30, 1095))
        maturity_date = origination_date + timedelta(days=term_months * 30)
        
        # Current balance (simplified)
        months_elapsed = (datetime.now() - origination_date).days // 30
        remaining_balance = original_amount * (1 - (months_elapsed / term_months) * 0.6)
        
        status = rng.choices(['ACTIVE', 'PAID_OFF', 'DEFAULT'], weights=[0.9, 0.08, 0.02])[0]
        if status == 'PAID_OFF':
            remaining_balance = 0
        
        loans_data.append((
            i, f'MTG{i:08d}', i, i, loan_type, 'PURCHASE',
            round(original_amount, 2), round(interest_rate, 4), term_months,
            origination_date.strftime('%Y-%m-%d'), maturity_date.strftime('%Y-%m-%d'),
            round(remaining_balance, 2), status
        ))
    
    conn.executemany("INSERT INTO mortgage_loans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", loans_data)
    
    # Insert escrow accounts for active loans
    print("Inserting escrow accounts...")
    escrow_data = []
    active_loans = [loan for loan in loans_data if loan[12] == 'ACTIVE']
    
    for loan in active_loans:
        loan_id = loan[0]
        property_value = properties_data[loan_id-1][8]
        
        annual_taxes = property_value * rng.uniform(0.01, 0.025)
        annual_insurance = property_value * rng.uniform(0.003, 0.008)
        monthly_escrow = (annual_taxes + annual_insurance) / 12
        current_balance = monthly_escrow * rng.uniform(1, 4)
        
        escrow_data.append((
            loan_id, loan_id, round(current_balance, 2), round(annual_taxes, 2),
            round(annual_insurance, 2), round(monthly_escrow, 2),
            (datetime.now() - timedelta(days=rng.randint(30, 365))).strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=rng.randint(30, 365))).strftime('%Y-%m-%d'),
            round(rng.uniform(-200, 200), 2)
        ))
    
    conn.executemany("INSERT INTO escrow_accounts VALUES (?,?,?,?,?,?,?,?,?)", escrow_data)
    
    # Insert some payments for active loans
    print("Inserting mortgage payments...")
    payments_data = []
    payment_id = 1
    
    for loan in active_loans[:500]:  # Limit for performance
        loan_id = loan[0]
        original_amount = loan[6]
        
        # Generate 12 months of payments
        for month in range(12):
            payment_date = (datetime.now() - timedelta(days=(11-month)*30)).strftime('%Y-%m-%d')
            monthly_payment = original_amount * 0.005  # Simplified calculation
            
            payments_data.append((
                payment_id, loan_id, payment_date, monthly_payment, monthly_payment,
                monthly_payment * 0.2, monthly_payment * 0.6, monthly_payment * 0.2,
                0, 'AUTO_DEBIT', 0
            ))
            payment_id += 1
    
    conn.executemany("INSERT INTO mortgage_payments VALUES (?,?,?,?,?,?,?,?,?,?,?)", payments_data)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_borrowers_ssn ON borrowers(ssn_hash)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mortgage_loans_status ON mortgage_loans(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mortgage_payments_date ON mortgage_payments(payment_date)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
