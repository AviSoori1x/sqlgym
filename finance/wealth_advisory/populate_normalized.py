#!/usr/bin/env python3
"""Populate wealth advisory normalized schema with synthetic data."""
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
CLIENTS = 500
PORTFOLIOS_PER_CLIENT = 2
SECURITIES = 200
TRADES_PER_PORTFOLIO = 50

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert clients
    print(f"Inserting {CLIENTS} wealth management clients...")
    clients_data = []
    
    for i in range(1, CLIENTS + 1):
        net_worth = rng.uniform(1_000_000, 50_000_000)
        
        # Risk tolerance correlates with age and net worth
        age = rng.randint(35, 80)
        if age > 65:
            risk_tolerance = rng.choices(['CONSERVATIVE', 'MODERATE'], weights=[0.7, 0.3])[0]
        elif age > 50:
            risk_tolerance = rng.choices(['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE'], weights=[0.3, 0.5, 0.2])[0]
        else:
            risk_tolerance = rng.choices(['MODERATE', 'AGGRESSIVE', 'VERY_AGGRESSIVE'], weights=[0.4, 0.4, 0.2])[0]
        
        # Investment objective aligns with risk tolerance
        if risk_tolerance == 'CONSERVATIVE':
            objective = rng.choice(['CAPITAL_PRESERVATION', 'INCOME'])
        elif risk_tolerance == 'MODERATE':
            objective = rng.choice(['INCOME', 'GROWTH'])
        else:
            objective = rng.choice(['GROWTH', 'AGGRESSIVE_GROWTH'])
        
        birth_date = (datetime.now() - timedelta(days=age * 365)).strftime('%Y-%m-%d')
        onboarding_date = (datetime.now() - timedelta(days=rng.randint(30, 1095))).strftime('%Y-%m-%d')
        advisor_id = f'ADV{rng.randint(1, 50):03d}'
        
        clients_data.append((
            i, f'WM{i:06d}', f'Client{i}', f'LastName{i}',
            birth_date, round(net_worth, 2), risk_tolerance, objective,
            advisor_id, onboarding_date
        ))
    
    conn.executemany("INSERT INTO clients VALUES (?,?,?,?,?,?,?,?,?,?)", clients_data)
    
    # Insert securities
    print("Inserting securities...")
    securities_data = []
    
    # Stock securities
    for i in range(1, 101):
        securities_data.append((
            i, f'STOCK{i:03d}', f'Company {i} Corp', 'EQUITY', 'STOCK',
            rng.choice(['Technology', 'Healthcare', 'Finance', 'Energy']), 'USD', 1
        ))
    
    # Bond securities
    for i in range(101, 151):
        securities_data.append((
            i, f'BOND{i:03d}', f'Bond {i}', 'FIXED_INCOME', 'BOND',
            'Government', 'USD', 1
        ))
    
    # ETFs and Mutual Funds
    for i in range(151, 201):
        sec_type = 'ETF' if i <= 175 else 'MUTUAL_FUND'
        securities_data.append((
            i, f'{sec_type}{i:03d}', f'{sec_type} {i}', 'EQUITY', sec_type,
            'Diversified', 'USD', 1
        ))
    
    conn.executemany("INSERT INTO securities VALUES (?,?,?,?,?,?,?,?)", securities_data)
    
    # Insert portfolios
    print("Inserting portfolios...")
    portfolios_data = []
    portfolio_id = 1
    
    for client in clients_data:
        client_id = client[0]
        risk_tolerance = client[6]
        
        # Create 1-3 portfolios per client
        num_portfolios = rng.randint(1, min(PORTFOLIOS_PER_CLIENT, 3))
        
        portfolio_types = ['TAXABLE', 'IRA', 'ROTH_IRA', '401K']
        selected_types = rng.sample(portfolio_types, num_portfolios)
        
        for portfolio_type in selected_types:
            inception_date = (datetime.strptime(client[9], '%Y-%m-%d') + 
                            timedelta(days=rng.randint(0, 365))).strftime('%Y-%m-%d')
            
            # Target allocation based on risk tolerance
            if risk_tolerance == 'CONSERVATIVE':
                allocation = {'equity': 0.3, 'fixed_income': 0.6, 'cash': 0.1}
            elif risk_tolerance == 'MODERATE':
                allocation = {'equity': 0.6, 'fixed_income': 0.3, 'cash': 0.1}
            else:
                allocation = {'equity': 0.8, 'fixed_income': 0.15, 'cash': 0.05}
            
            benchmark = 'S&P_500' if allocation['equity'] > 0.5 else 'AGG_BOND'
            current_value = rng.uniform(100000, 5000000)
            
            portfolios_data.append((
                portfolio_id, client_id, f'{portfolio_type}_Portfolio',
                portfolio_type, inception_date, benchmark,
                json.dumps(allocation), round(current_value, 2), 'ACTIVE'
            ))
            portfolio_id += 1
    
    conn.executemany("INSERT INTO portfolios VALUES (?,?,?,?,?,?,?,?,?)", portfolios_data)
    
    # Insert trades and positions
    print("Inserting trades...")
    trades_data = []
    positions_data = []
    trade_id = 1
    position_id = 1
    
    for portfolio in portfolios_data:
        portfolio_id = portfolio[0]
        inception_date = datetime.strptime(portfolio[4], '%Y-%m-%d')
        current_value = portfolio[7]
        
        # Generate trades for this portfolio
        num_trades = rng.randint(10, TRADES_PER_PORTFOLIO)
        
        for _ in range(num_trades):
            security_id = rng.randint(1, SECURITIES)
            trade_date = inception_date + timedelta(days=rng.randint(0, (datetime.now() - inception_date).days))
            settlement_date = trade_date + timedelta(days=rng.randint(1, 3))
            
            trade_type = rng.choice(['BUY', 'SELL'])
            quantity = rng.uniform(1, 1000)
            price = rng.uniform(10, 500)
            gross_amount = quantity * price
            commission = gross_amount * 0.001  # 0.1% commission
            net_amount = gross_amount - commission if trade_type == 'BUY' else gross_amount + commission
            
            trades_data.append((
                trade_id, portfolio_id, security_id,
                trade_date.strftime('%Y-%m-%d'), settlement_date.strftime('%Y-%m-%d'),
                trade_type, quantity, price, gross_amount, commission, net_amount,
                'Portfolio rebalancing'
            ))
            trade_id += 1
    
    for chunk in batch(trades_data, 1000):
        conn.executemany("INSERT INTO trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Create sample positions for each portfolio
    print("Inserting positions...")
    for portfolio in portfolios_data:
        portfolio_id = portfolio[0]
        
        # Create 5-15 positions per portfolio
        num_positions = rng.randint(5, 15)
        selected_securities = rng.sample(range(1, SECURITIES + 1), num_positions)
        
        for security_id in selected_securities:
            quantity = rng.uniform(10, 1000)
            avg_cost = rng.uniform(20, 300)
            current_price = avg_cost * rng.uniform(0.7, 1.5)  # Price movement
            market_value = quantity * current_price
            unrealized_gl = (current_price - avg_cost) * quantity
            
            positions_data.append((
                position_id, portfolio_id, security_id, quantity,
                avg_cost, current_price, market_value, unrealized_gl,
                datetime.now().strftime('%Y-%m-%d')
            ))
            position_id += 1
    
    conn.executemany("INSERT INTO positions VALUES (?,?,?,?,?,?,?,?,?)", positions_data)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_advisor ON clients(advisor_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_portfolios_client ON portfolios(client_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_trades_portfolio ON trades(portfolio_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_positions_portfolio ON positions(portfolio_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()