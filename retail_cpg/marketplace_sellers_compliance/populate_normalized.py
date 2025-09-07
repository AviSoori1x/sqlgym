#!/usr/bin/env python3
"""Populate marketplace sellers compliance normalized schema with synthetic data."""
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
SELLERS = 2000
POLICIES = 15
VIOLATIONS_PER_SELLER = 2
METRICS_DAYS = 90

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert compliance policies
    print("Inserting compliance policies...")
    policies_data = [
        (1, 'Product Description Accuracy', 'PRODUCT_QUALITY', 'Products must match descriptions', 'MEDIUM', 1, '2024-01-01', 1),
        (2, 'Counterfeit Products', 'PRODUCT_QUALITY', 'No counterfeit items allowed', 'CRITICAL', 1, '2024-01-01', 1),
        (3, 'Shipping Time Compliance', 'SHIPPING', 'Ship within promised timeframe', 'HIGH', 1, '2024-01-01', 1),
        (4, 'Return Policy Adherence', 'RETURNS', 'Honor stated return policies', 'MEDIUM', 0, '2024-01-01', 1),
        (5, 'Customer Service Response', 'CUSTOMER_SERVICE', 'Respond within 24 hours', 'MEDIUM', 1, '2024-01-01', 1),
        (6, 'Prohibited Items', 'LEGAL', 'No restricted or illegal items', 'CRITICAL', 1, '2024-01-01', 1),
        (7, 'Review Manipulation', 'PRODUCT_QUALITY', 'No fake reviews or incentivized feedback', 'HIGH', 1, '2024-01-01', 1),
        (8, 'Price Accuracy', 'PRODUCT_QUALITY', 'Accurate pricing and no hidden fees', 'MEDIUM', 0, '2024-01-01', 1)
    ]
    conn.executemany("INSERT INTO compliance_policies VALUES (?,?,?,?,?,?,?,?)", policies_data)
    
    # Insert sellers
    print(f"Inserting {SELLERS} sellers...")
    sellers_data = []
    countries = ['US', 'UK', 'DE', 'FR', 'CA', 'AU', 'JP', 'CN', 'IN', 'BR']
    
    for i in range(1, SELLERS + 1):
        business_type = rng.choices(['INDIVIDUAL', 'BUSINESS', 'ENTERPRISE'], weights=[0.4, 0.5, 0.1])[0]
        reg_date = (datetime.now() - timedelta(days=rng.randint(30, 1095))).strftime('%Y-%m-%d')
        country = rng.choice(countries)
        
        # Verification status based on business type and age
        if business_type == 'ENTERPRISE':
            verification = rng.choices(['VERIFIED', 'PENDING'], weights=[0.9, 0.1])[0]
        else:
            verification = rng.choices(['VERIFIED', 'PENDING', 'REJECTED'], weights=[0.7, 0.2, 0.1])[0]
        
        rating = rng.uniform(2.5, 5.0) if verification == 'VERIFIED' else rng.uniform(1.0, 4.0)
        total_sales = rng.uniform(1000, 500000) if verification == 'VERIFIED' else rng.uniform(0, 10000)
        active_listings = rng.randint(5, 1000) if verification == 'VERIFIED' else rng.randint(0, 50)
        
        sellers_data.append((
            i, f'Seller_{i}', business_type, reg_date, country,
            verification, round(rating, 2), round(total_sales, 2), active_listings
        ))
    
    for chunk in batch(sellers_data, 1000):
        conn.executemany("INSERT INTO sellers VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert policy violations
    print("Inserting policy violations...")
    violations_data = []
    violation_id = 1
    
    for seller_id in range(1, SELLERS + 1):
        seller = sellers_data[seller_id - 1]
        
        # Higher-rated sellers have fewer violations
        if seller[6] > 4.0:  # rating
            violation_chance = 0.2
        elif seller[6] > 3.0:
            violation_chance = 0.4
        else:
            violation_chance = 0.7
        
        if rng.random() < violation_chance:
            num_violations = rng.randint(1, VIOLATIONS_PER_SELLER)
            
            for _ in range(num_violations):
                policy_id = rng.randint(1, len(policies_data))
                policy = policies_data[policy_id - 1]
                
                violation_date = (datetime.now() - timedelta(days=rng.randint(0, 365))).strftime('%Y-%m-%d')
                violation_type = rng.choices(['AUTOMATIC', 'REPORTED', 'AUDIT_FOUND'], weights=[0.5, 0.3, 0.2])[0]
                
                evidence = {
                    'source': violation_type.lower(),
                    'severity': policy[4],
                    'details': f'Violation of {policy[1]}'
                }
                
                status = rng.choices(['RESOLVED', 'CLOSED', 'OPEN'], weights=[0.6, 0.3, 0.1])[0]
                resolution_date = (datetime.fromisoformat(violation_date) + timedelta(days=rng.randint(1, 30))).strftime('%Y-%m-%d') if status != 'OPEN' else None
                
                penalty = None
                if policy[4] in ['HIGH', 'CRITICAL'] and status == 'RESOLVED':
                    penalty = rng.choice(['WARNING', 'LISTING_REMOVAL', 'FINE'])
                
                violations_data.append((
                    violation_id, seller_id, policy_id, violation_date, violation_type,
                    f'Violation: {policy[1]}', json.dumps(evidence), status,
                    resolution_date, penalty
                ))
                violation_id += 1
    
    for chunk in batch(violations_data, 1000):
        conn.executemany("INSERT INTO policy_violations VALUES (?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert seller metrics
    print("Inserting seller metrics...")
    metrics_data = []
    metric_id = 1
    
    for seller_id in range(1, SELLERS + 1):
        seller = sellers_data[seller_id - 1]
        
        # Generate daily metrics for last 90 days
        for days_ago in range(METRICS_DAYS):
            metric_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            # Metrics vary by seller performance
            if seller[6] > 4.0:  # High-rated seller
                orders = rng.randint(0, 50)
                cancel_rate = rng.uniform(0, 0.05)
                return_rate = rng.uniform(0, 0.10)
                late_ship_rate = rng.uniform(0, 0.05)
                satisfaction = rng.uniform(4.0, 5.0)
            else:  # Lower-rated seller
                orders = rng.randint(0, 20)
                cancel_rate = rng.uniform(0, 0.20)
                return_rate = rng.uniform(0, 0.30)
                late_ship_rate = rng.uniform(0, 0.25)
                satisfaction = rng.uniform(2.0, 4.0)
            
            response_time = rng.uniform(1, 48)
            
            metrics_data.append((
                metric_id, seller_id, metric_date, orders,
                round(cancel_rate, 4), round(return_rate, 4), round(late_ship_rate, 4),
                round(satisfaction, 2), round(response_time, 1)
            ))
            metric_id += 1
    
    for chunk in batch(metrics_data, 1000):
        conn.executemany("INSERT INTO seller_metrics VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert audit logs
    print("Inserting audit logs...")
    audit_data = []
    audit_id = 1
    
    for seller_id in range(1, SELLERS + 1):
        if rng.random() < 0.3:  # 30% of sellers audited
            audit_type = rng.choice(['ACCOUNT_REVIEW', 'PRODUCT_AUDIT', 'PERFORMANCE_CHECK', 'COMPLIANCE_SCAN'])
            audit_date = (datetime.now() - timedelta(days=rng.randint(0, 180))).strftime('%Y-%m-%d')
            auditor_id = f'auditor_{rng.randint(1, 20)}'
            
            findings = {
                'audit_type': audit_type,
                'issues_found': rng.randint(0, 5),
                'recommendations': ['Improve response time', 'Update policies']
            }
            
            risk_score = rng.randint(10, 90)
            follow_up = risk_score > 60
            
            audit_data.append((
                audit_id, seller_id, audit_type, audit_date, auditor_id,
                json.dumps(findings), risk_score, follow_up
            ))
            audit_id += 1
    
    for chunk in batch(audit_data, 500):
        conn.executemany("INSERT INTO audit_logs VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    # Insert enforcement actions
    print("Inserting enforcement actions...")
    actions_data = []
    action_id = 1
    
    # Create actions for critical violations
    for violation in violations_data:
        if violation[9] and violation[9] != 'WARNING':  # Has penalty
            action_type = violation[9]
            action_date = violation[3]  # Same as violation date
            reason = f'Policy violation: {violation[5]}'
            
            duration = rng.randint(7, 30) if action_type == 'ACCOUNT_SUSPENSION' else None
            penalty = rng.uniform(100, 1000) if action_type == 'FINE' else None
            appeal_deadline = (datetime.fromisoformat(action_date) + timedelta(days=14)).strftime('%Y-%m-%d')
            status = rng.choices(['ACTIVE', 'EXPIRED'], weights=[0.7, 0.3])[0]
            
            actions_data.append((
                action_id, violation[1], action_type, action_date, reason,
                duration, penalty, appeal_deadline, status
            ))
            action_id += 1
    
    for chunk in batch(actions_data, 500):
        conn.executemany("INSERT INTO enforcement_actions VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sellers_verification ON sellers(verification_status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_policy_violations_seller ON policy_violations(seller_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_seller_metrics_seller_date ON seller_metrics(seller_id, metric_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_seller ON audit_logs(seller_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()