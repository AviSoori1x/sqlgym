#!/usr/bin/env python3
"""Populate corporate banking cash management normalized schema with synthetic data."""
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
CORPORATE_CLIENTS = 200
ACCOUNTS_PER_CLIENT = 8
TRANSACTIONS_PER_ACCOUNT = 400
SWEEP_EXECUTIONS_PER_POOL = 90

# Industry classifications
INDUSTRIES = [
    'Technology', 'Healthcare', 'Manufacturing', 'Retail', 'Finance',
    'Energy', 'Real Estate', 'Transportation', 'Media', 'Government'
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
    
    # Insert account types
    print("Inserting account types...")
    account_types_data = [
        (1, 'Operating Checking', 'CHECKING', 0, 10000, json.dumps({'monthly_fee': 25, 'per_transaction': 0.15}), 1),
        (2, 'High-Yield Savings', 'SAVINGS', 1, 50000, json.dumps({'monthly_fee': 0, 'min_balance_fee': 15}), 1),
        (3, 'Money Market', 'MONEY_MARKET', 1, 100000, json.dumps({'monthly_fee': 50, 'tiered_rates': True}), 1),
        (4, 'Certificate of Deposit', 'CD', 1, 1000, json.dumps({'early_withdrawal_penalty': 0.01}), 1),
        (5, 'Sweep Account', 'SWEEP', 1, 0, json.dumps({'sweep_fee': 5}), 1),
        (6, 'Concentration Account', 'CONCENTRATION', 0, 0, json.dumps({'management_fee': 100}), 1)
    ]
    conn.executemany("INSERT INTO account_types VALUES (?,?,?,?,?,?,?)", account_types_data)
    
    # Insert corporate clients
    print(f"Inserting {CORPORATE_CLIENTS} corporate clients...")
    clients_data = []
    
    for i in range(1, CORPORATE_CLIENTS + 1):
        industry = rng.choice(INDUSTRIES)
        
        # Company size affects revenue and risk
        size_tier = rng.choices(['SMALL', 'MEDIUM', 'LARGE'], weights=[0.5, 0.3, 0.2])[0]
        
        if size_tier == 'SMALL':
            revenue = rng.uniform(1_000_000, 50_000_000)
            employees = rng.randint(10, 500)
            risk = rng.choices(['LOW', 'MEDIUM'], weights=[0.7, 0.3])[0]
        elif size_tier == 'MEDIUM':
            revenue = rng.uniform(50_000_000, 500_000_000)
            employees = rng.randint(500, 5000)
            risk = rng.choices(['LOW', 'MEDIUM', 'HIGH'], weights=[0.5, 0.4, 0.1])[0]
        else:  # LARGE
            revenue = rng.uniform(500_000_000, 50_000_000_000)
            employees = rng.randint(5000, 100000)
            risk = rng.choices(['LOW', 'MEDIUM'], weights=[0.8, 0.2])[0]
        
        relationship_start = (datetime.now() - timedelta(days=rng.randint(30, 2555))).strftime('%Y-%m-%d')
        kyc_status = rng.choices(['APPROVED', 'PENDING', 'EXPIRED'], weights=[0.85, 0.10, 0.05])[0]
        
        clients_data.append((
            i, f'CORP{i:04d}', f'Company {i} Corp',
            industry, round(revenue, 2), employees,
            relationship_start, risk, kyc_status
        ))
    
    conn.executemany("INSERT INTO corporate_clients VALUES (?,?,?,?,?,?,?,?,?)", clients_data)
    
    # Insert accounts
    print("Inserting accounts...")
    accounts_data = []
    account_id = 1
    
    for client in clients_data:
        client_id = client[0]
        revenue = client[4]
        
        # Number of accounts based on company size
        if revenue < 50_000_000:
            num_accounts = rng.randint(2, 5)
        elif revenue < 500_000_000:
            num_accounts = rng.randint(4, 8)
        else:
            num_accounts = rng.randint(6, 12)
        
        # Always have at least one operating account
        account_types_to_use = [1]  # Operating Checking
        
        # Add other account types
        if num_accounts > 1:
            additional_types = rng.sample([2, 3, 4, 5], min(num_accounts - 1, 4))
            account_types_to_use.extend(additional_types)
        
        for acc_type_id in account_types_to_use[:num_accounts]:
            opening_date = (datetime.strptime(client[6], '%Y-%m-%d') + 
                          timedelta(days=rng.randint(0, 365))).strftime('%Y-%m-%d')
            
            # Balance varies by account type and company size
            if acc_type_id == 1:  # Operating
                balance = revenue / 365 * rng.uniform(5, 30)  # 5-30 days of daily revenue
            elif acc_type_id in [2, 3]:  # Savings/MM
                balance = revenue * rng.uniform(0.05, 0.20)  # 5-20% of annual revenue
            elif acc_type_id == 4:  # CD
                balance = revenue * rng.uniform(0.10, 0.50)
            else:  # Sweep/Concentration
                balance = rng.uniform(0, 100000)
            
            available_balance = balance * rng.uniform(0.8, 1.0)
            status = rng.choices(['ACTIVE', 'DORMANT'], weights=[0.9, 0.1])[0]
            
            accounts_data.append((
                account_id, f'ACC{account_id:08d}', client_id, acc_type_id,
                'USD', opening_date, round(balance, 2), round(available_balance, 2),
                status, None  # parent_account_id
            ))
            account_id += 1
    
    conn.executemany("INSERT INTO accounts VALUES (?,?,?,?,?,?,?,?,?,?)", accounts_data)
    
    # Insert cash pool structures
    print("Inserting cash pool structures...")
    pool_structures_data = []
    pool_participants_data = []
    pool_id = 1
    participant_id = 1
    
    # About 60% of clients have cash pooling
    clients_with_pools = rng.sample(range(1, CORPORATE_CLIENTS + 1), int(CORPORATE_CLIENTS * 0.6))
    
    for client_id in clients_with_pools:
        client_accounts = [a for a in accounts_data if a[2] == client_id]
        
        if len(client_accounts) >= 3:  # Need multiple accounts for pooling
            pool_type = rng.choice(['ZERO_BALANCE', 'TARGET_BALANCE', 'THRESHOLD_SWEEP'])
            sweep_freq = rng.choice(['DAILY', 'WEEKLY'])
            
            # Master account is typically concentration account
            master_account = rng.choice(client_accounts)
            master_account_id = master_account[0]
            
            target_balance = rng.uniform(50000, 500000) if pool_type == 'TARGET_BALANCE' else 0
            threshold = rng.uniform(10000, 100000) if pool_type == 'THRESHOLD_SWEEP' else 0
            
            pool_structures_data.append((
                pool_id, f'Pool_{client_id}', client_id, master_account_id,
                pool_type, sweep_freq, target_balance, threshold, 1
            ))
            
            # Add participant accounts (excluding master)
            participant_accounts = [a for a in client_accounts if a[0] != master_account_id]
            
            for participant_account in participant_accounts[:5]:  # Max 5 participants
                participation_type = rng.choice(['CONTRIBUTOR', 'BENEFICIARY', 'BOTH'])
                priority = rng.randint(1, 3)
                
                pool_participants_data.append((
                    participant_id, pool_id, participant_account[0],
                    participation_type, priority, None, None
                ))
                participant_id += 1
            
            pool_id += 1
    
    conn.executemany("INSERT INTO cash_pool_structures VALUES (?,?,?,?,?,?,?,?,?)", pool_structures_data)
    conn.executemany("INSERT INTO pool_participants VALUES (?,?,?,?,?,?,?)", pool_participants_data)
    
    # Insert transactions
    print("Inserting transactions...")
    transactions_data = []
    transaction_id = 1
    
    for account in accounts_data:
        account_id = account[0]
        opening_date = datetime.strptime(account[5], '%Y-%m-%d')
        
        # Generate transactions for last 90 days
        num_transactions = rng.randint(50, TRANSACTIONS_PER_ACCOUNT)
        
        for _ in range(num_transactions):
            trans_date = opening_date + timedelta(days=rng.randint(0, 
                min(90, (datetime.now() - opening_date).days)))
            
            if trans_date > datetime.now():
                continue
            
            value_date = trans_date + timedelta(days=rng.randint(0, 2))
            
            # Transaction types and amounts
            trans_type = rng.choices(['CREDIT', 'DEBIT', 'SWEEP_IN', 'SWEEP_OUT', 'INTEREST', 'FEE'],
                                   weights=[0.3, 0.4, 0.1, 0.1, 0.05, 0.05])[0]
            
            if trans_type in ['CREDIT', 'SWEEP_IN']:
                amount = rng.uniform(1000, 500000)
            elif trans_type in ['DEBIT', 'SWEEP_OUT']:
                amount = -rng.uniform(1000, 300000)
            elif trans_type == 'INTEREST':
                amount = rng.uniform(10, 5000)
            else:  # FEE
                amount = -rng.uniform(25, 500)
            
            description = f'{trans_type} transaction'
            ref_number = f'REF{transaction_id:08d}'
            
            transactions_data.append((
                transaction_id, account_id, trans_date.strftime('%Y-%m-%d %H:%M:%S'),
                value_date.strftime('%Y-%m-%d'), trans_type, round(amount, 2),
                description, ref_number, None, None
            ))
            transaction_id += 1
    
    for chunk in batch(transactions_data, 1000):
        conn.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert sweep executions
    print("Inserting sweep executions...")
    sweep_executions_data = []
    execution_id = 1
    
    for pool in pool_structures_data:
        pool_id = pool[0]
        sweep_freq = pool[5]
        
        # Generate sweep executions based on frequency
        if sweep_freq == 'DAILY':
            num_executions = 90
        elif sweep_freq == 'WEEKLY':
            num_executions = 13
        else:
            num_executions = 3
        
        for i in range(num_executions):
            if sweep_freq == 'DAILY':
                exec_date = datetime.now() - timedelta(days=90-i)
            elif sweep_freq == 'WEEKLY':
                exec_date = datetime.now() - timedelta(weeks=13-i)
            else:
                exec_date = datetime.now() - timedelta(days=30*i)
            
            # Sweep amounts vary
            total_swept = rng.uniform(10000, 2000000)
            participant_count = len([p for p in pool_participants_data if p[1] == pool_id])
            
            status = rng.choices(['COMPLETED', 'FAILED', 'PARTIAL'], weights=[0.85, 0.05, 0.10])[0]
            
            execution_details = {
                'swept_accounts': participant_count,
                'total_amount': total_swept,
                'execution_time': '14:30:00'
            }
            
            sweep_executions_data.append((
                execution_id, pool_id, exec_date.strftime('%Y-%m-%d'),
                round(total_swept, 2), participant_count, status,
                json.dumps(execution_details)
            ))
            execution_id += 1
    
    for chunk in batch(sweep_executions_data, 500):
        conn.executemany("INSERT INTO sweep_executions VALUES (?,?,?,?,?,?,?)", chunk)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_corporate_clients_risk ON corporate_clients(risk_rating)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_client ON accounts(client_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pool_structures_client ON cash_pool_structures(client_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sweep_executions_pool ON sweep_executions(pool_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sweep_executions_date ON sweep_executions(execution_date)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()