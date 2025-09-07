#!/usr/bin/env python3
"""Populate corporate banking cash management denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized-db", required=True)
    parser.add_argument("--denormalized-db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    
    rng = get_rng(args.seed)
    
    norm_conn = sqlite3.connect(args.normalized_db)
    norm_conn.row_factory = sqlite3.Row
    denorm_conn = sqlite3.connect(args.denormalized_db)
    
    print("Building client cash position summary...")
    client_position_query = """
    SELECT 
        cc.id as client_id,
        cc.client_code,
        cc.company_name,
        cc.risk_rating,
        COUNT(DISTINCT a.id) as total_accounts,
        SUM(a.current_balance) as total_balance,
        SUM(a.available_balance) as available_balance,
        COUNT(DISTINCT cps.id) as sweep_pool_count,
        MAX(se.execution_date) as last_sweep_date
    FROM corporate_clients cc
    LEFT JOIN accounts a ON cc.id = a.client_id AND a.status = 'ACTIVE'
    LEFT JOIN cash_pool_structures cps ON cc.id = cps.client_id AND cps.is_active = 1
    LEFT JOIN sweep_executions se ON cps.id = se.pool_id
    GROUP BY cc.id
    """
    
    client_position_data = []
    for row in norm_conn.execute(client_position_query):
        # Calculate derived metrics
        total_balance = row['total_balance'] or 0
        avg_daily_balance = total_balance * rng.uniform(0.8, 1.2)
        interest_earned = total_balance * 0.02 / 12  # 2% annual rate
        fees_paid = rng.uniform(100, 2000)
        
        # Liquidity score based on balance and volatility
        liquidity_score = min(100, (total_balance / 1000000) * 50 + rng.uniform(20, 50))
        
        # Concentration risk based on account diversity
        account_count = row['total_accounts'] or 1
        concentration_risk = max(0, 100 - (account_count * 10))
        
        client_position_data.append((
            row['client_id'], row['client_code'], row['company_name'], row['risk_rating'],
            row['total_accounts'] or 0, total_balance, row['available_balance'] or 0,
            row['sweep_pool_count'] or 0, avg_daily_balance, interest_earned, fees_paid,
            row['last_sweep_date'], liquidity_score, concentration_risk
        ))
    
    denorm_conn.executemany("""
        INSERT INTO client_cash_position VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, client_position_data)
    
    print("Building daily liquidity metrics...")
    daily_metrics_query = """
    SELECT 
        DATE(t.transaction_date) as date,
        a.client_id,
        SUM(CASE WHEN t.transaction_type IN ('CREDIT', 'SWEEP_IN') THEN t.amount ELSE 0 END) as credits,
        SUM(CASE WHEN t.transaction_type IN ('DEBIT', 'SWEEP_OUT') THEN ABS(t.amount) ELSE 0 END) as debits,
        SUM(CASE WHEN t.transaction_type IN ('SWEEP_IN', 'SWEEP_OUT') THEN ABS(t.amount) ELSE 0 END) as sweep_volume,
        SUM(CASE WHEN t.transaction_type = 'INTEREST' THEN t.amount ELSE 0 END) as interest_earned
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE t.transaction_date >= DATE('now', '-90 days')
    GROUP BY DATE(t.transaction_date), a.client_id
    """
    
    daily_metrics_data = []
    for row in norm_conn.execute(daily_metrics_query):
        credits = row['credits'] or 0
        debits = row['debits'] or 0
        
        # Simulate intraday positions
        peak_position = credits * rng.uniform(1.1, 1.5)
        trough_position = max(0, credits - debits * rng.uniform(0.8, 1.2))
        
        volatility = abs(peak_position - trough_position) / max(peak_position, 1) * 100
        overdraft = max(0, -trough_position) if trough_position < 0 else 0
        
        daily_metrics_data.append((
            row['date'], row['client_id'], credits, peak_position, trough_position,
            volatility, row['sweep_volume'] or 0, row['interest_earned'] or 0, overdraft
        ))
    
    denorm_conn.executemany("""
        INSERT INTO daily_liquidity_metrics VALUES 
        (?,?,?,?,?,?,?,?,?)
    """, daily_metrics_data)
    
    print("Building pool performance summary...")
    pool_performance_query = """
    SELECT 
        cps.id as pool_id,
        cps.pool_name,
        cc.client_code,
        cps.pool_type,
        COUNT(DISTINCT pp.account_id) as participant_accounts,
        AVG(se.total_amount_swept) as avg_sweep_amount,
        SUM(se.total_amount_swept) as total_sweep_volume_mtd,
        MAX(se.execution_date) as last_execution_date
    FROM cash_pool_structures cps
    JOIN corporate_clients cc ON cps.client_id = cc.id
    LEFT JOIN pool_participants pp ON cps.id = pp.pool_id
    LEFT JOIN sweep_executions se ON cps.id = se.pool_id 
        AND se.execution_date >= DATE('now', '-30 days')
    GROUP BY cps.id
    """
    
    pool_performance_data = []
    for row in norm_conn.execute(pool_performance_query):
        # Calculate performance metrics
        participant_count = row['participant_accounts'] or 0
        avg_balance = (row['avg_sweep_amount'] or 0) * participant_count
        
        # Efficiency score based on sweep frequency and volume
        efficiency_score = min(100, (row['total_sweep_volume_mtd'] or 0) / 1000000 * 20 + 
                              participant_count * 10 + rng.uniform(30, 50))
        
        # Cost savings estimate
        cost_savings = (row['total_sweep_volume_mtd'] or 0) * 0.001  # 0.1% savings
        
        # Actual vs configured frequency (simplified)
        frequency_actual = rng.uniform(0.8, 1.2)
        
        pool_performance_data.append((
            row['pool_id'], row['pool_name'], row['client_code'], row['pool_type'],
            participant_count, avg_balance, row['total_sweep_volume_mtd'] or 0,
            frequency_actual, efficiency_score, cost_savings, row['last_execution_date']
        ))
    
    denorm_conn.executemany("""
        INSERT INTO pool_performance_summary VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, pool_performance_data)
    
    print("Building account utilization analysis...")
    utilization_query = """
    WITH account_stats AS (
        SELECT 
            a.id as account_id,
            a.account_number,
            cc.client_code,
            at.category as account_category,
            a.current_balance,
            COUNT(t.id) as transaction_count_30d,
            MAX(t.transaction_date) as last_transaction_date
        FROM accounts a
        JOIN corporate_clients cc ON a.client_id = cc.id
        JOIN account_types at ON a.account_type_id = at.id
        LEFT JOIN transactions t ON a.id = t.account_id 
            AND t.transaction_date >= DATE('now', '-30 days')
        WHERE a.status = 'ACTIVE'
        GROUP BY a.id
    )
    SELECT 
        account_id,
        account_number,
        client_code,
        account_category,
        current_balance,
        current_balance as avg_balance_30d,
        current_balance * 0.5 as min_balance_30d,
        current_balance * 1.5 as max_balance_30d,
        transaction_count_30d,
        CASE 
            WHEN last_transaction_date IS NULL THEN 999
            ELSE CAST(julianday('now') - julianday(last_transaction_date) AS INTEGER)
        END as dormancy_days
    FROM account_stats
    """
    
    utilization_data = []
    for row in norm_conn.execute(utilization_query):
        dormancy_days = row['dormancy_days']
        transaction_count = row['transaction_count_30d'] or 0
        
        # Categorize utilization
        if dormancy_days > 90:
            utilization_category = 'DORMANT'
        elif transaction_count >= 20:
            utilization_category = 'HIGH'
        elif transaction_count >= 5:
            utilization_category = 'MEDIUM'
        else:
            utilization_category = 'LOW'
        
        utilization_data.append(tuple(row) + (utilization_category,))
    
    denorm_conn.executemany("""
        INSERT INTO account_utilization_analysis VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, utilization_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_client_position_risk ON client_cash_position(risk_rating)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_client_position_balance ON client_cash_position(total_balance DESC)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_liquidity_metrics(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_pool_performance_efficiency ON pool_performance_summary(efficiency_score DESC)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_account_utilization_category ON account_utilization_analysis(utilization_category)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()