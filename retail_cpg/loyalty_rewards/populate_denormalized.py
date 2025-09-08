#!/usr/bin/env python3
"""Populate loyalty rewards denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
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
    
    print("Building member analytics...")
    member_query = """
    SELECT
        m.id as member_id,
        m.customer_id,
        t.name as tier_name,
        m.enrollment_date,
        m.total_points_earned,
        m.current_points_balance,
        m.lifetime_spend,
        COUNT(DISTINCT r.id) as total_redemptions,
        SUM(r.points_redeemed) as total_redeemed_points,
        AVG(rc.monetary_value) as avg_redemption_value
    FROM members m
    JOIN tiers t ON m.tier_id = t.id
    LEFT JOIN redemptions r ON m.id = r.member_id AND r.status = 'PROCESSED'
    LEFT JOIN rewards_catalog rc ON r.reward_id = rc.id
    GROUP BY m.id
    """
    
    member_analytics_data = []
    for row in norm_conn.execute(member_query):
        enrollment_date = datetime.strptime(row['enrollment_date'], '%Y-%m-%d')
        tier_tenure = (datetime.now() - enrollment_date).days
        
        # Simulate last activity and engagement
        last_activity = (datetime.now() - timedelta(days=rng.randint(1, 90))).strftime('%Y-%m-%d')
        days_since_activity = (datetime.now() - datetime.strptime(last_activity, '%Y-%m-%d')).days
        
        # Calculate engagement score
        redemptions = row['total_redemptions'] or 0
        points_earned = row['total_points_earned'] or 0
        
        engagement_score = min(10, (redemptions * 2) + (points_earned / 1000) + (5 if days_since_activity < 30 else 0))
        
        member_analytics_data.append((
            row['member_id'], row['customer_id'], row['tier_name'], row['enrollment_date'],
            points_earned, row['current_points_balance'] or 0, row['lifetime_spend'] or 0,
            redemptions, row['total_redeemed_points'] or 0, row['avg_redemption_value'] or 0,
            last_activity, days_since_activity, tier_tenure, engagement_score
        ))
    
    denorm_conn.executemany("""
        INSERT INTO member_analytics VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, member_analytics_data)
    
    print("Building tier performance...")
    tier_query = """
    SELECT
        t.id as tier_id,
        strftime('%Y-%m', pt.transaction_date) as month,
        COUNT(DISTINCT m.id) as member_count,
        SUM(CASE WHEN pt.transaction_type = 'EARN' THEN pt.points_amount ELSE 0 END) as points_earned,
        SUM(CASE WHEN pt.transaction_type = 'REDEEM' THEN ABS(pt.points_amount) ELSE 0 END) as points_redeemed,
        AVG(m.lifetime_spend) as avg_spend
    FROM tiers t
    LEFT JOIN members m ON t.id = m.tier_id
    LEFT JOIN point_transactions pt ON m.id = pt.member_id
    WHERE pt.transaction_date IS NOT NULL
    GROUP BY t.id, strftime('%Y-%m', pt.transaction_date)
    """
    
    tier_performance_data = []
    for row in norm_conn.execute(tier_query):
        redemption_rate = (row['points_redeemed'] or 0) / max(row['points_earned'] or 1, 1)
        retention_rate = 0.85 + rng.uniform(-0.1, 0.1)  # Simulated
        
        tier_performance_data.append((
            row['tier_id'], row['month'], row['member_count'] or 0,
            0, 0,  # new_members, churned_members (simplified)
            row['points_earned'] or 0, row['points_redeemed'] or 0,
            row['avg_spend'] or 0, redemption_rate, retention_rate
        ))
    
    denorm_conn.executemany("""
        INSERT INTO tier_performance VALUES 
        (?,?,?,?,?,?,?,?,?,?)
    """, tier_performance_data)
    
    print("Building reward popularity...")
    reward_query = """
    SELECT
        rc.id as reward_id,
        strftime('%Y-%m', r.redemption_date) as month,
        COUNT(r.id) as redemption_count,
        SUM(r.points_redeemed) as total_points,
        COUNT(DISTINCT r.member_id) as unique_redeemers
    FROM rewards_catalog rc
    LEFT JOIN redemptions r ON rc.id = r.reward_id AND r.status = 'PROCESSED'
    WHERE r.redemption_date IS NOT NULL
    GROUP BY rc.id, strftime('%Y-%m', r.redemption_date)
    """
    
    reward_data = []
    for row in norm_conn.execute(reward_query):
        avg_days_to_redeem = rng.uniform(5, 30)  # Simulated
        tier_dist = json.dumps({'Bronze': 0.4, 'Silver': 0.3, 'Gold': 0.2, 'Platinum': 0.1})
        
        reward_data.append((
            row['reward_id'], row['month'], row['redemption_count'] or 0,
            row['total_points'] or 0, row['unique_redeemers'] or 0,
            avg_days_to_redeem, tier_dist
        ))
    
    denorm_conn.executemany("""
        INSERT INTO reward_popularity VALUES 
        (?,?,?,?,?,?,?)
    """, reward_data)
    
    print("Building points economy summary...")
    economy_query = """
    SELECT
        DATE(pt.transaction_date) as date,
        SUM(CASE WHEN pt.transaction_type = 'EARN' THEN pt.points_amount ELSE 0 END) as points_issued,
        SUM(CASE WHEN pt.transaction_type = 'REDEEM' THEN ABS(pt.points_amount) ELSE 0 END) as points_redeemed,
        COUNT(DISTINCT CASE WHEN m.current_points_balance > 0 THEN m.id END) as active_members
    FROM point_transactions pt
    LEFT JOIN members m ON pt.member_id = m.id
    GROUP BY DATE(pt.transaction_date)
    """
    
    economy_data = []
    for row in norm_conn.execute(economy_query):
        points_liability = (row['points_issued'] or 0) * 0.01  # $0.01 per point
        breakage_rate = 0.15 + rng.uniform(-0.05, 0.05)  # 15% +/- 5%
        avg_points_per_transaction = (row['points_issued'] or 0) / max(1, row['active_members'] or 1)
        
        economy_data.append((
            row['date'], row['points_issued'] or 0, row['points_redeemed'] or 0,
            points_liability, breakage_rate, avg_points_per_transaction,
            row['active_members'] or 0
        ))
    
    denorm_conn.executemany("""
        INSERT INTO points_economy_summary VALUES 
        (?,?,?,?,?,?,?)
    """, economy_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_member_analytics_tier ON member_analytics(tier_name)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_tier_performance_month ON tier_performance(month)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_reward_popularity_month ON reward_popularity(month)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()