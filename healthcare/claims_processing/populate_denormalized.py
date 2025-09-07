#!/usr/bin/env python3
"""Populate claims processing denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import batch

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized-db", required=True)
    parser.add_argument("--denormalized-db", required=True)
    args = parser.parse_args()
    
    norm_conn = sqlite3.connect(args.normalized_db)
    norm_conn.row_factory = sqlite3.Row
    denorm_conn = sqlite3.connect(args.denormalized_db)
    
    print("Building claims analytics...")
    analytics_query = """
    SELECT
        mc.id as claim_id,
        mc.claim_number,
        m.member_id,
        m.first_name || ' ' || m.last_name as member_name,
        ip.plan_code,
        ip.plan_type,
        p.npi as provider_npi,
        p.provider_name,
        p.specialty as provider_specialty,
        mc.service_date,
        mc.submission_date,
        mc.claim_type,
        mc.place_of_service,
        mc.total_charged_amount,
        SUM(cli.allowed_amount) as total_allowed_amount,
        SUM(cli.paid_amount) as total_paid_amount,
        SUM(cli.copay_amount + cli.deductible_amount + cli.coinsurance_amount) as member_responsibility,
        julianday(ca.adjudication_date) - julianday(mc.submission_date) as processing_days,
        mc.status as claim_status,
        COUNT(DISTINCT cd.id) as denial_count,
        0 as appeal_count,
        ca.auto_adjudicated
    FROM medical_claims mc
    JOIN members m ON mc.member_id = m.id
    JOIN insurance_plans ip ON mc.plan_id = ip.id
    JOIN providers p ON mc.provider_id = p.id
    LEFT JOIN claim_line_items cli ON mc.id = cli.claim_id
    LEFT JOIN claim_adjudications ca ON mc.id = ca.claim_id
    LEFT JOIN claim_denials cd ON mc.id = cd.claim_id
    GROUP BY mc.id
    """
    
    analytics_data = []
    for row in norm_conn.execute(analytics_query):
        analytics_data.append(tuple(row))
    
    for chunk in batch(analytics_data, 500):
        denorm_conn.executemany("""
            INSERT INTO claims_analytics VALUES 
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building daily metrics...")
    daily_query = """
    SELECT
        DATE(mc.submission_date) as date,
        ip.plan_type,
        COUNT(mc.id) as claims_received,
        COUNT(CASE WHEN ca.id IS NOT NULL THEN mc.id END) as claims_processed,
        COUNT(CASE WHEN ca.decision = 'APPROVED' THEN mc.id END) as claims_approved,
        COUNT(CASE WHEN ca.decision = 'DENIED' THEN mc.id END) as claims_denied,
        SUM(mc.total_charged_amount) as total_charged_amount,
        SUM(cli.paid_amount) as total_paid_amount,
        AVG(ca.processing_time_hours) as avg_processing_time_hours,
        AVG(CASE WHEN ca.auto_adjudicated = 1 THEN 1.0 ELSE 0.0 END) as auto_adjudication_rate
    FROM medical_claims mc
    JOIN insurance_plans ip ON mc.plan_id = ip.id
    LEFT JOIN claim_adjudications ca ON mc.id = ca.claim_id
    LEFT JOIN claim_line_items cli ON mc.id = cli.claim_id
    GROUP BY DATE(mc.submission_date), ip.plan_type
    """
    
    daily_data = []
    for row in norm_conn.execute(daily_query):
        denial_rate = row['claims_denied'] / row['claims_received'] if row['claims_received'] > 0 else 0
        daily_data.append(tuple(row) + (denial_rate,))
    
    denorm_conn.executemany("""
        INSERT INTO daily_claims_metrics VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, daily_data)
    
    print("Building provider performance...")
    provider_query = """
    SELECT
        p.id as provider_id,
        p.npi,
        p.provider_name,
        p.specialty,
        strftime('%Y-%m', mc.service_date) as month,
        COUNT(mc.id) as claims_submitted,
        COUNT(CASE WHEN ca.decision = 'APPROVED' THEN mc.id END) as claims_approved,
        COUNT(CASE WHEN ca.decision = 'DENIED' THEN mc.id END) as claims_denied,
        SUM(mc.total_charged_amount) as total_charged,
        SUM(cli.paid_amount) as total_paid,
        AVG(ca.processing_time_hours / 24.0) as avg_approval_time_days
    FROM providers p
    LEFT JOIN medical_claims mc ON p.id = mc.provider_id
    LEFT JOIN claim_adjudications ca ON mc.id = ca.claim_id
    LEFT JOIN claim_line_items cli ON mc.id = cli.claim_id
    WHERE mc.id IS NOT NULL
    GROUP BY p.id, strftime('%Y-%m', mc.service_date)
    """
    
    provider_data = []
    for row in norm_conn.execute(provider_query):
        denial_rate = row['claims_denied'] / row['claims_submitted'] if row['claims_submitted'] > 0 else 0
        clean_claim_rate = 1 - denial_rate
        
        provider_data.append(tuple(row) + (denial_rate, clean_claim_rate))
    
    denorm_conn.executemany("""
        INSERT INTO provider_performance VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, provider_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_claims_analytics_member ON claims_analytics(member_id)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_claims_metrics(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_provider_performance_month ON provider_performance(month)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()