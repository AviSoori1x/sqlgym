#!/usr/bin/env python3
"""Populate marketplace sellers compliance denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import batch, get_rng

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized-db", required=True)
    parser.add_argument("--denormalized-db", required=True)
    args = parser.parse_args()
    
    rng = get_rng(42)
    
    norm_conn = sqlite3.connect(args.normalized_db)
    norm_conn.row_factory = sqlite3.Row
    denorm_conn = sqlite3.connect(args.denormalized_db)
    
    print("Building seller compliance summary...")
    compliance_query = """
    SELECT
        s.id as seller_id,
        s.seller_name,
        s.business_type,
        s.verification_status,
        s.performance_rating,
        COUNT(pv.id) as total_violations,
        COUNT(CASE WHEN cp.severity_level = 'CRITICAL' THEN pv.id END) as critical_violations,
        COUNT(CASE WHEN pv.status = 'OPEN' THEN pv.id END) as open_violations,
        MAX(pv.violation_date) as last_violation_date,
        COUNT(ea.id) as enforcement_actions
    FROM sellers s
    LEFT JOIN policy_violations pv ON s.id = pv.seller_id
    LEFT JOIN compliance_policies cp ON pv.policy_id = cp.id
    LEFT JOIN enforcement_actions ea ON s.id = ea.seller_id
    GROUP BY s.id
    """
    
    compliance_data = []
    for row in norm_conn.execute(compliance_query):
        # Calculate compliance score
        violations = row['total_violations'] or 0
        critical_violations = row['critical_violations'] or 0
        rating = row['performance_rating'] or 3.0
        
        compliance_score = max(0, 100 - (violations * 5) - (critical_violations * 15) + (rating - 3) * 10)
        
        # Determine risk level
        if compliance_score < 50 or critical_violations > 2:
            risk_level = 'HIGH'
        elif compliance_score < 70 or violations > 5:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        compliance_data.append((
            row['seller_id'], row['seller_name'], row['business_type'],
            row['verification_status'], rating, violations, critical_violations,
            row['open_violations'] or 0, row['last_violation_date'],
            compliance_score, risk_level, row['enforcement_actions'] or 0
        ))
    
    denorm_conn.executemany("""
        INSERT INTO seller_compliance_summary VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?)
    """, compliance_data)
    
    print("Building daily compliance metrics...")
    daily_query = """
    SELECT
        DATE(pv.violation_date) as date,
        COUNT(pv.id) as new_violations,
        COUNT(CASE WHEN pv.violation_type = 'AUTOMATIC' THEN pv.id END) as auto_detected,
        COUNT(CASE WHEN pv.violation_type = 'REPORTED' THEN pv.id END) as reported
    FROM policy_violations pv
    WHERE pv.violation_date >= DATE('now', '-30 days')
    GROUP BY DATE(pv.violation_date)
    """
    
    daily_data = []
    for row in norm_conn.execute(daily_query):
        resolved_violations = rng.randint(0, row['new_violations'])
        compliance_rate = 1 - (row['new_violations'] / max(100, row['new_violations'] + 100))
        avg_resolution_time = rng.uniform(5, 30)
        
        daily_data.append((
            row['date'], row['new_violations'], resolved_violations,
            row['auto_detected'] or 0, row['reported'] or 0,
            avg_resolution_time, compliance_rate
        ))
    
    denorm_conn.executemany("""
        INSERT INTO daily_compliance_metrics VALUES 
        (?,?,?,?,?,?,?)
    """, daily_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_seller_compliance_risk ON seller_compliance_summary(risk_level)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_compliance_date ON daily_compliance_metrics(date)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()