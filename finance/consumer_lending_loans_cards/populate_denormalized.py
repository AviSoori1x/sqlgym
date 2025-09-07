#!/usr/bin/env python3
"""Populate consumer lending denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
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
    
    print("Building loan portfolio summary...")
    loan_summary_query = """
    SELECT
        l.id as loan_id,
        cu.customer_id,
        cu.credit_score,
        cu.income,
        lp.product_type,
        l.principal_amount,
        l.interest_rate,
        l.term_months,
        l.status as loan_status,
        l.current_balance,
        l.delinquency_days,
        l.origination_date,
        CAST(julianday('now') - julianday(l.origination_date) AS INTEGER) as age_of_loan_days
    FROM loans l
    JOIN customers cu ON l.customer_id = cu.id
    JOIN loan_products lp ON l.loan_product_id = lp.id
    WHERE lp.product_type != 'CREDIT_CARD'
    """
    loan_summary_data = []
    for row in norm_conn.execute(loan_summary_query):
        ltv = rng.uniform(0.7, 1.1) if row['product_type'] == 'AUTO_LOAN' else None
        loan_summary_data.append(tuple(row) + (ltv,))
    denorm_conn.executemany("INSERT INTO loan_portfolio_summary VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", loan_summary_data)

    print("Building credit card portfolio...")
    cc_portfolio_query = """
    SELECT
        cc.id as card_id,
        cu.customer_id,
        cu.credit_score,
        cc.credit_limit,
        l.current_balance,
        cc.status as card_status,
        l.delinquency_days
    FROM credit_cards cc
    JOIN loans l ON cc.loan_id = l.id
    JOIN customers cu ON l.customer_id = cu.id
    """
    cc_portfolio_data = []
    for row in norm_conn.execute(cc_portfolio_query):
        utilization = row['current_balance'] / row['credit_limit'] if row['credit_limit'] > 0 else 0
        cash_balance = row['current_balance'] * rng.uniform(0, 0.2)
        cash_utilization = cash_balance / (row['credit_limit'] * 0.3) if row['credit_limit'] > 0 else 0
        last_payment_date = (datetime.now() - timedelta(days=rng.randint(5, 45))).strftime('%Y-%m-%d')
        days_since_payment = (datetime.now() - datetime.strptime(last_payment_date, '%Y-%m-%d')).days
        
        spending_profile = json.dumps({'RETAIL': 0.6, 'TRAVEL': 0.2, 'GROCERY': 0.2})
        rewards_points = rng.randint(1000, 50000)

        cc_portfolio_data.append(
            tuple(row[:4]) + (row['current_balance'], utilization, cash_balance, cash_utilization, row['card_status'], row['delinquency_days'],
            last_payment_date, days_since_payment, spending_profile, rewards_points)
        )
    denorm_conn.executemany("INSERT INTO credit_card_portfolio VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", cc_portfolio_data)

    print("Building daily lending metrics...")
    daily_metrics_query = """
    SELECT
        DATE(la.application_date) as date,
        lp.product_type,
        COUNT(la.id) as app_count,
        COUNT(CASE WHEN la.status = 'APPROVED' THEN 1 END) as approved_count,
        COUNT(CASE WHEN la.status = 'BOOKED' THEN 1 END) as booked_count,
        SUM(CASE WHEN la.status = 'BOOKED' THEN la.approved_amount ELSE 0 END) as booked_volume,
        AVG(la.interest_rate) as avg_rate,
        AVG(cu.credit_score) as avg_score
    FROM loan_applications la
    JOIN loan_products lp ON la.product_id = lp.id
    JOIN customers cu ON la.customer_id = cu.id
    GROUP BY DATE(la.application_date), lp.product_type
    """
    daily_metrics_data = []
    for row in norm_conn.execute(daily_metrics_query):
        approval_rate = row['approved_count'] / row['app_count'] if row['app_count'] > 0 else 0
        delinquency_rate = rng.uniform(0.01, 0.15)
        charge_off_volume = row['booked_volume'] * rng.uniform(0.001, 0.02)
        daily_metrics_data.append(
            (row['date'], row['product_type'], row['app_count'], row['approved_count'], approval_rate,
             row['booked_count'], row['booked_volume'], row['avg_rate'], row['avg_score'],
             delinquency_rate, charge_off_volume)
        )
    denorm_conn.executemany("INSERT INTO daily_lending_metrics VALUES (?,?,?,?,?,?,?,?,?,?,?)", daily_metrics_data)

    print("Building customer risk profiles...")
    risk_profile_query = """
    SELECT
        c.id as customer_id,
        SUM(CASE WHEN lp.product_type != 'CREDIT_CARD' THEN l.current_balance ELSE 0 END) as total_loan_exposure,
        SUM(CASE WHEN lp.product_type = 'CREDIT_CARD' THEN cc.credit_limit ELSE 0 END) as total_cc_limit,
        SUM(CASE WHEN lp.product_type = 'CREDIT_CARD' THEN l.current_balance ELSE 0 END) as total_cc_balance,
        COUNT(DISTINCT CASE WHEN lp.product_type != 'CREDIT_CARD' THEN l.id END) as active_loans_count,
        COUNT(DISTINCT cc.id) as active_cards_count,
        AVG(l.delinquency_days) as avg_delinquency_days
    FROM customers c
    LEFT JOIN loans l ON c.id = l.customer_id
    LEFT JOIN loan_products lp ON l.loan_product_id = lp.id
    LEFT JOIN credit_cards cc ON l.id = cc.loan_id
    WHERE l.status = 'ACTIVE' OR cc.status = 'ACTIVE'
    GROUP BY c.id
    """
    risk_profile_data = []
    for row in norm_conn.execute(risk_profile_query):
        total_limit = row['total_cc_limit'] or 0
        total_balance = row['total_cc_balance'] or 0
        utilization = total_balance / total_limit if total_limit > 0 else 0
        
        delinquency = row['avg_delinquency_days'] or 0
        if delinquency > 60 or utilization > 0.8:
            risk_segment = 'VERY_HIGH'
        elif delinquency > 30 or utilization > 0.6:
            risk_segment = 'HIGH'
        elif delinquency > 0 or utilization > 0.4:
            risk_segment = 'MEDIUM'
        else:
            risk_segment = 'LOW'

        risk_profile_data.append(
            (row['customer_id'], row['total_loan_exposure'], total_limit, total_balance, utilization,
             row['active_loans_count'], row['active_cards_count'], delinquency, risk_segment,
             datetime.now().strftime('%Y-%m-%d'))
        )
    denorm_conn.executemany("INSERT INTO customer_risk_profile VALUES (?,?,?,?,?,?,?,?,?,?)", risk_profile_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_loan_portfolio_status ON loan_portfolio_summary(loan_status)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_cc_portfolio_utilization ON credit_card_portfolio(utilization_rate DESC)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_lending_metrics(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_risk_profile_segment ON customer_risk_profile(risk_segment)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
