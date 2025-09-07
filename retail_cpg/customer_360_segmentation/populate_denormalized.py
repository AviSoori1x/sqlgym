#!/usr/bin/env python3
"""Populate customer 360 segmentation denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
import json
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
    
    print("Building customer 360 profiles...")
    profile_query = """
    WITH customer_metrics AS (
        SELECT 
            c.id as customer_id,
            c.email,
            c.first_name || ' ' || c.last_name as full_name,
            CAST((julianday('now') - julianday(c.date_of_birth)) / 365 AS INTEGER) as age,
            c.gender,
            c.registration_date,
            c.acquisition_channel,
            julianday('now') - julianday(c.registration_date) as days_since_registration,
            COUNT(DISTINCT t.id) as total_transactions,
            COALESCE(SUM(t.total_amount - t.discount_amount), 0) as total_spent,
            MAX(t.transaction_date) as last_transaction_date,
            GROUP_CONCAT(DISTINCT cp.preference_value) as preferred_categories
        FROM customers c
        LEFT JOIN transactions t ON c.id = t.customer_id
        LEFT JOIN customer_preferences cp ON c.id = cp.customer_id AND cp.preference_type = 'CATEGORY'
        GROUP BY c.id
    ),
    channel_stats AS (
        SELECT 
            customer_id,
            channel,
            COUNT(*) as channel_count
        FROM transactions
        GROUP BY customer_id, channel
    ),
    favorite_channels AS (
        SELECT 
            customer_id,
            channel as favorite_channel
        FROM (
            SELECT 
                customer_id,
                channel,
                ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC) as rn
            FROM channel_stats
            GROUP BY customer_id, channel
        )
        WHERE rn = 1
    ),
    segment_assignments AS (
        SELECT 
            csa.customer_id,
            GROUP_CONCAT(cs.name) as segment_names
        FROM customer_segment_assignments csa
        JOIN customer_segments cs ON csa.segment_id = cs.id
        WHERE csa.expires_date > DATE('now')
        GROUP BY csa.customer_id
    )
    SELECT 
        cm.customer_id,
        cm.email,
        cm.full_name,
        cm.age,
        cm.gender,
        cm.registration_date,
        cm.acquisition_channel,
        CAST(cm.days_since_registration AS INTEGER) as days_since_registration,
        cm.total_transactions,
        cm.total_spent,
        CASE WHEN cm.total_transactions > 0 THEN cm.total_spent / cm.total_transactions ELSE 0 END as avg_order_value,
        cm.last_transaction_date,
        CASE 
            WHEN cm.last_transaction_date IS NOT NULL 
            THEN CAST(julianday('now') - julianday(cm.last_transaction_date) AS INTEGER)
            ELSE NULL 
        END as days_since_last_purchase,
        fc.favorite_channel,
        cm.preferred_categories,
        cm.total_spent * 1.2 as customer_lifetime_value,
        CASE 
            WHEN cm.last_transaction_date IS NULL THEN 0.9
            WHEN julianday('now') - julianday(cm.last_transaction_date) > 180 THEN 0.7
            WHEN julianday('now') - julianday(cm.last_transaction_date) > 90 THEN 0.4
            ELSE 0.1
        END as churn_risk_score,
        sa.segment_names,
        CASE 
            WHEN cm.total_transactions >= 10 THEN 0.9
            WHEN cm.total_transactions >= 5 THEN 0.7
            WHEN cm.total_transactions >= 1 THEN 0.5
            ELSE 0.2
        END as engagement_score
    FROM customer_metrics cm
    LEFT JOIN favorite_channels fc ON cm.customer_id = fc.customer_id
    LEFT JOIN segment_assignments sa ON cm.customer_id = sa.customer_id
    """
    
    profile_data = []
    for row in norm_conn.execute(profile_query):
        profile_data.append(tuple(row))
    
    for chunk in batch(profile_data, 500):
        denorm_conn.executemany("""
            INSERT INTO customer_360_profile VALUES 
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building segment performance metrics...")
    segment_query = """
    SELECT 
        cs.id as segment_id,
        cs.name as segment_name,
        strftime('%Y-%m', t.transaction_date) as month,
        COUNT(DISTINCT csa.customer_id) as customer_count,
        0 as new_customers,
        0 as churned_customers,
        COALESCE(SUM(t.total_amount - t.discount_amount), 0) as total_revenue,
        AVG(t.total_amount - t.discount_amount) as avg_order_value,
        COUNT(t.id) * 1.0 / COUNT(DISTINCT csa.customer_id) as transaction_frequency,
        0.75 as engagement_rate,
        0.85 as retention_rate
    FROM customer_segments cs
    LEFT JOIN customer_segment_assignments csa ON cs.id = csa.segment_id
    LEFT JOIN transactions t ON csa.customer_id = t.customer_id
    WHERE t.transaction_date IS NOT NULL
    GROUP BY cs.id, strftime('%Y-%m', t.transaction_date)
    """
    
    segment_data = []
    for row in norm_conn.execute(segment_query):
        segment_data.append(tuple(row))
    
    denorm_conn.executemany("""
        INSERT INTO segment_performance VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, segment_data)
    
    print("Building channel attribution...")
    attribution_query = """
    SELECT 
        t.customer_id,
        t.channel,
        COUNT(*) as touchpoint_count,
        MIN(t.transaction_date) as first_touch_date,
        MAX(t.transaction_date) as last_touch_date,
        SUM(t.total_amount - t.discount_amount) as attributed_revenue,
        1.0 as conversion_rate
    FROM transactions t
    GROUP BY t.customer_id, t.channel
    """
    
    attribution_data = []
    for row in norm_conn.execute(attribution_query):
        attribution_data.append(tuple(row))
    
    denorm_conn.executemany("""
        INSERT INTO channel_attribution VALUES 
        (?,?,?,?,?,?,?)
    """, attribution_data)
    
    print("Building behavioral cohorts...")
    cohort_query = """
    SELECT 
        strftime('%Y-%m', c.registration_date) as cohort_month,
        c.acquisition_channel,
        COUNT(DISTINCT c.id) as cohort_size,
        COUNT(DISTINCT CASE 
            WHEN EXISTS (
                SELECT 1 FROM transactions t 
                WHERE t.customer_id = c.id 
                AND t.transaction_date <= DATE(c.registration_date, '+1 month')
            ) THEN c.id 
        END) as month_1_active,
        COUNT(DISTINCT CASE 
            WHEN EXISTS (
                SELECT 1 FROM transactions t 
                WHERE t.customer_id = c.id 
                AND t.transaction_date <= DATE(c.registration_date, '+3 months')
            ) THEN c.id 
        END) as month_3_active,
        COUNT(DISTINCT CASE 
            WHEN EXISTS (
                SELECT 1 FROM transactions t 
                WHERE t.customer_id = c.id 
                AND t.transaction_date <= DATE(c.registration_date, '+6 months')
            ) THEN c.id 
        END) as month_6_active,
        COUNT(DISTINCT CASE 
            WHEN EXISTS (
                SELECT 1 FROM transactions t 
                WHERE t.customer_id = c.id 
                AND t.transaction_date <= DATE(c.registration_date, '+12 months')
            ) THEN c.id 
        END) as month_12_active,
        COALESCE(SUM(t.total_amount - t.discount_amount), 0) as cumulative_revenue,
        COALESCE(AVG(t.total_amount - t.discount_amount), 0) as avg_customer_value
    FROM customers c
    LEFT JOIN transactions t ON c.id = t.customer_id
    GROUP BY strftime('%Y-%m', c.registration_date), c.acquisition_channel
    """
    
    cohort_data = []
    for row in norm_conn.execute(cohort_query):
        cohort_data.append(tuple(row))
    
    denorm_conn.executemany("""
        INSERT INTO behavioral_cohorts VALUES 
        (?,?,?,?,?,?,?,?,?)
    """, cohort_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_customer_profile_clv ON customer_360_profile(customer_lifetime_value DESC)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_customer_profile_churn ON customer_360_profile(churn_risk_score DESC)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_segment_performance_month ON segment_performance(month)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_channel_attribution_revenue ON channel_attribution(attributed_revenue DESC)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_cohorts_month ON behavioral_cohorts(cohort_month)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()