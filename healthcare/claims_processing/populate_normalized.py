#!/usr/bin/env python3
"""Populate claims processing normalized schema with synthetic data."""
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
MEMBERS = 5000
PROVIDERS = 800
CLAIMS_PER_MEMBER = 8

# Medical codes
ICD10_CODES = ['Z00.00', 'Z01.419', 'M25.50', 'E11.9', 'I10', 'J44.1', 'K21.9']
CPT_CODES = ['99213', '99214', '99215', '85025', '80053', '93000', '71020']
SPECIALTIES = ['Family Medicine', 'Internal Medicine', 'Cardiology', 'Orthopedics']

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert members
    print(f"Inserting {MEMBERS} members...")
    members_data = []
    for i in range(1, MEMBERS + 1):
        birth_date = (datetime.now() - timedelta(days=rng.randint(18*365, 80*365))).strftime('%Y-%m-%d')
        enrollment_date = (datetime.now() - timedelta(days=rng.randint(30, 1095))).strftime('%Y-%m-%d')
        
        members_data.append((
            i, f'MBR{i:07d}', f'First{i}', f'Last{i}', birth_date,
            rng.choice(['M', 'F']), f'{i} Health St', f'555-{i:04d}',
            f'member{i}@health.com', enrollment_date, 'ACTIVE'
        ))
    
    conn.executemany("INSERT INTO members VALUES (?,?,?,?,?,?,?,?,?,?,?)", members_data)
    
    # Insert insurance plans
    plans_data = [
        (1, 'HMO_BASIC', 'Basic HMO', 'HMO', 'INDIVIDUAL', 1000, 5000, 20, 40, 1),
        (2, 'PPO_PREMIUM', 'Premium PPO', 'PPO', 'FAMILY', 2500, 8000, 30, 60, 1),
        (3, 'MEDICARE_SUPP', 'Medicare Supplement', 'MEDICARE', 'INDIVIDUAL', 500, 3000, 15, 30, 1)
    ]
    conn.executemany("INSERT INTO insurance_plans VALUES (?,?,?,?,?,?,?,?,?,?)", plans_data)
    
    # Insert providers
    print(f"Inserting {PROVIDERS} providers...")
    providers_data = []
    for i in range(1, PROVIDERS + 1):
        specialty = rng.choice(SPECIALTIES)
        npi = f'{1000000000 + i}'
        
        providers_data.append((
            i, npi, f'Dr. Provider {i}', specialty, 'PHYSICIAN',
            f'{10000000 + i}', f'{i} Medical Plaza', 'IN_NETWORK'
        ))
    
    conn.executemany("INSERT INTO providers VALUES (?,?,?,?,?,?,?,?)", providers_data)
    
    # Insert claims
    print("Inserting medical claims...")
    claims_data = []
    line_items_data = []
    adjudications_data = []
    
    claim_id = 1
    line_id = 1
    adj_id = 1
    
    for member_id in range(1, MEMBERS + 1):
        num_claims = rng.randint(2, CLAIMS_PER_MEMBER)
        
        for _ in range(num_claims):
            provider_id = rng.randint(1, PROVIDERS)
            plan_id = rng.randint(1, 3)
            
            service_date = (datetime.now() - timedelta(days=rng.randint(1, 365))).strftime('%Y-%m-%d')
            submission_date = (datetime.strptime(service_date, '%Y-%m-%d') + timedelta(days=rng.randint(1, 30))).strftime('%Y-%m-%d')
            
            diagnosis_codes = rng.sample(ICD10_CODES, rng.randint(1, 2))
            status = rng.choices(['APPROVED', 'DENIED', 'PAID'], weights=[0.4, 0.2, 0.4])[0]
            
            # Create claim
            total_charged = rng.uniform(100, 1500)
            
            claims_data.append((
                claim_id, f'CLM{claim_id:09d}', member_id, plan_id, provider_id,
                service_date, submission_date, 'PROFESSIONAL', 'OFFICE',
                json.dumps(diagnosis_codes), round(total_charged, 2), status, 'ROUTINE'
            ))
            
            # Create line items
            for line_num in range(1, rng.randint(1, 3) + 1):
                procedure_code = rng.choice(CPT_CODES)
                charged_amount = total_charged / 2
                
                if status == 'APPROVED' or status == 'PAID':
                    allowed = charged_amount * 0.85
                    paid = allowed * 0.9
                    denied = 0
                else:
                    allowed = paid = 0
                    denied = charged_amount
                
                line_items_data.append((
                    line_id, claim_id, line_num, procedure_code, None, 1,
                    round(charged_amount, 2), round(allowed, 2), round(paid, 2),
                    round(denied, 2), 20, 0, 0
                ))
                line_id += 1
            
            # Create adjudication
            if status != 'PENDING':
                adj_date = (datetime.strptime(submission_date, '%Y-%m-%d') + timedelta(days=rng.randint(1, 10))).strftime('%Y-%m-%d')
                decision = 'APPROVED' if status in ['APPROVED', 'PAID'] else 'DENIED'
                
                adjudications_data.append((
                    adj_id, claim_id, adj_date, f'ADJ_{rng.randint(1, 20)}',
                    decision, round(total_charged * 0.85, 2) if decision == 'APPROVED' else 0,
                    round(total_charged, 2) if decision == 'DENIED' else 0,
                    json.dumps(['00'] if decision == 'APPROVED' else ['16']),
                    rng.uniform(2, 48), rng.random() < 0.6
                ))
                adj_id += 1
            
            claim_id += 1
    
    # Batch inserts
    for chunk in batch(claims_data, 1000):
        conn.executemany("INSERT INTO medical_claims VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(line_items_data, 1000):
        conn.executemany("INSERT INTO claim_line_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(adjudications_data, 1000):
        conn.executemany("INSERT INTO claim_adjudications VALUES (?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_members_member_id ON members(member_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_medical_claims_member ON medical_claims(member_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_medical_claims_status ON medical_claims(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_claim_line_items_claim ON claim_line_items(claim_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
