#!/usr/bin/env python3
"""Populate mortgage servicing denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized-db", required=True)
    parser.add_argument("--denormalized-db", required=True)
    args = parser.parse_args()
    
    norm_conn = sqlite3.connect(args.normalized_db)
    norm_conn.row_factory = sqlite3.Row
    denorm_conn = sqlite3.connect(args.denormalized_db)
    
    print("Building loan servicing summary...")
    servicing_query = """
    SELECT
        ml.id as loan_id,
        ml.loan_number,
        b.first_name || ' ' || b.last_name as borrower_name,
        p.property_address,
        ml.loan_type,
        ml.original_amount,
        ml.current_balance,
        ml.interest_rate,
        ml.status as loan_status,
        ml.origination_date,
        CAST((julianday('now') - julianday(ml.origination_date)) / 30 AS INTEGER) as loan_age_months,
        ml.term_months - CAST((julianday('now') - julianday(ml.origination_date)) / 30 AS INTEGER) as remaining_term_months,
        ml.current_balance / p.appraised_value as current_ltv,
        MAX(mp.payment_date) as last_payment_date,
        DATE(ml.origination_date, '+' || CAST((julianday('now') - julianday(ml.origination_date)) / 30 + 1 AS INTEGER) || ' months') as next_payment_due_date,
        ea.current_balance as escrow_balance
    FROM mortgage_loans ml
    JOIN borrowers b ON ml.borrower_id = b.id
    JOIN properties p ON ml.property_id = p.id
    LEFT JOIN mortgage_payments mp ON ml.id = mp.loan_id
    LEFT JOIN escrow_accounts ea ON ml.id = ea.loan_id
    GROUP BY ml.id
    """
    
    servicing_data = []
    for row in norm_conn.execute(servicing_query):
        # Determine payment status
        last_payment = row['last_payment_date']
        if last_payment:
            days_since_payment = (datetime.now() - datetime.strptime(last_payment, '%Y-%m-%d')).days
            if days_since_payment <= 30:
                payment_status = 'CURRENT'
                days_delinquent = 0
            elif days_since_payment <= 60:
                payment_status = 'DELINQUENT_30'
                days_delinquent = days_since_payment - 30
            elif days_since_payment <= 90:
                payment_status = 'DELINQUENT_60'
                days_delinquent = days_since_payment - 30
            else:
                payment_status = 'DELINQUENT_90_PLUS'
                days_delinquent = days_since_payment - 30
        else:
            payment_status = 'CURRENT'
            days_delinquent = 0
        
        servicing_data.append(tuple(row) + (payment_status, days_delinquent))
    
    denorm_conn.executemany("""
        INSERT INTO loan_servicing_summary VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, servicing_data)
    
    print("Building portfolio performance metrics...")
    portfolio_query = """
    SELECT
        DATE('now', '-' || (row_number() OVER (ORDER BY ml.id) % 30) || ' days') as date,
        ml.loan_type,
        COUNT(*) as total_loans,
        SUM(ml.current_balance) as total_upb,
        SUM(mp.actual_payment_amount) as total_payments,
        SUM(mp.escrow_component) as escrow_collections,
        SUM(mp.late_fees) as late_fees_collected
    FROM mortgage_loans ml
    LEFT JOIN mortgage_payments mp ON ml.id = mp.loan_id 
        AND mp.payment_date >= DATE('now', '-30 days')
    WHERE ml.status = 'ACTIVE'
    GROUP BY date, ml.loan_type
    """
    
    portfolio_data = []
    for row in norm_conn.execute(portfolio_query):
        # Simulate delinquency counts
        total_loans = row['total_loans']
        delinq_30 = int(total_loans * 0.05)  # 5% delinquent 30+
        delinq_60 = int(total_loans * 0.02)  # 2% delinquent 60+
        delinq_90 = int(total_loans * 0.01)  # 1% delinquent 90+
        foreclosure = int(total_loans * 0.002)  # 0.2% in foreclosure
        
        portfolio_data.append((
            row['date'], row['loan_type'], total_loans, row['total_upb'] or 0,
            delinq_30, delinq_60, delinq_90, foreclosure,
            row['total_payments'] or 0, row['escrow_collections'] or 0,
            row['late_fees_collected'] or 0
        ))
    
    denorm_conn.executemany("""
        INSERT INTO portfolio_performance_daily VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, portfolio_data)
    
    print("Building escrow analysis...")
    escrow_query = """
    SELECT
        ea.id as escrow_account_id,
        ml.loan_number,
        b.first_name || ' ' || b.last_name as borrower_name,
        ea.current_balance,
        ea.annual_tax_amount + ea.annual_insurance_amount as annual_disbursement_estimate,
        ea.monthly_escrow_payment,
        ea.shortage_amount,
        ea.last_analysis_date
    FROM escrow_accounts ea
    JOIN mortgage_loans ml ON ea.loan_id = ml.id
    JOIN borrowers b ON ml.borrower_id = b.id
    """
    
    escrow_analysis_data = []
    for row in norm_conn.execute(escrow_query):
        current_balance = row['current_balance']
        annual_estimate = row['annual_disbursement_estimate']
        
        # Calculate projected shortage/surplus
        monthly_collection = row['monthly_escrow_payment']
        projected_12_month_collections = monthly_collection * 12
        projected_shortage = max(0, annual_estimate - projected_12_month_collections - current_balance)
        projected_surplus = max(0, projected_12_month_collections + current_balance - annual_estimate)
        
        cushion = monthly_collection * 2  # 2-month cushion
        
        if projected_shortage > 0:
            analysis_status = 'SHORTAGE'
        elif projected_surplus > cushion:
            analysis_status = 'SURPLUS'
        else:
            analysis_status = 'CURRENT'
        
        escrow_analysis_data.append((
            row['escrow_account_id'], row['loan_number'], row['borrower_name'],
            current_balance, annual_estimate, monthly_collection,
            projected_shortage if projected_shortage > 0 else None,
            projected_surplus if projected_surplus > 0 else None,
            row['last_analysis_date'], cushion, analysis_status
        ))
    
    denorm_conn.executemany("""
        INSERT INTO escrow_analysis_summary VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, escrow_analysis_data)
    
    print("Building delinquency roll rates...")
    # Simplified roll rate calculation
    roll_rates_data = []
    for month_offset in range(12):
        analysis_month = (datetime.now() - timedelta(days=month_offset * 30)).strftime('%Y-%m')
        
        for loan_type in ['CONVENTIONAL', 'FHA', 'VA']:
            # Simulate roll rates
            current_30 = 50 + month_offset * 2
            roll_to_60 = int(current_30 * 0.4)
            roll_to_90 = int(current_30 * 0.2)
            roll_to_foreclosure = int(current_30 * 0.05)
            cure_to_current = int(current_30 * 0.35)
            
            roll_rate_60 = roll_to_60 / current_30 if current_30 > 0 else 0
            roll_rate_90 = roll_to_90 / current_30 if current_30 > 0 else 0
            cure_rate = cure_to_current / current_30 if current_30 > 0 else 0
            
            roll_rates_data.append((
                analysis_month, loan_type, current_30, roll_to_60, roll_to_90,
                roll_to_foreclosure, cure_to_current, roll_rate_60, roll_rate_90, cure_rate
            ))
    
    denorm_conn.executemany("""
        INSERT INTO delinquency_roll_rates VALUES 
        (?,?,?,?,?,?,?,?,?,?)
    """, roll_rates_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_servicing_summary_status ON loan_servicing_summary(payment_status)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_daily_date ON portfolio_performance_daily(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_escrow_analysis_status ON escrow_analysis_summary(analysis_status)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()