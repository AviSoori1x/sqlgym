#!/usr/bin/env python3
"""Populate returns RMA support denormalized schema with analytical data."""
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
    
    print("Building return analytics...")
    analytics_query = """
    SELECT 
        r.id as rma_id,
        c.email as customer_email,
        c.loyalty_tier,
        p.sku as product_sku,
        p.name as product_name,
        p.category as product_category,
        o.order_date,
        r.request_date as return_request_date,
        julianday(r.request_date) - julianday(o.order_date) as days_since_purchase,
        r.reason as return_reason,
        r.status as current_status,
        i.recommendation as inspection_result,
        CASE 
            WHEN i.recommendation = 'FULL_REFUND' THEN oi.unit_price * oi.quantity - oi.discount_amount
            WHEN i.recommendation = 'PARTIAL_REFUND' THEN 
                (oi.unit_price * oi.quantity - oi.discount_amount) * (100 - i.deduction_percentage) / 100
            ELSE 0
        END as refund_amount,
        oi.unit_price * oi.quantity - oi.discount_amount as original_amount,
        CASE 
            WHEN r.status = 'CLOSED' THEN
                julianday(DATE('now')) - julianday(r.request_date)
            ELSE NULL
        END as processing_days,
        CASE 
            WHEN julianday(r.request_date) - julianday(o.order_date) <= p.warranty_days 
            THEN 1 ELSE 0 
        END as is_warranty_return
    FROM rma_requests r
    JOIN order_items oi ON r.order_item_id = oi.id
    JOIN orders o ON oi.order_id = o.id
    JOIN customers c ON r.customer_id = c.id
    JOIN products p ON oi.product_id = p.id
    LEFT JOIN rma_inspections i ON r.id = i.rma_id
    """
    
    analytics_data = []
    for row in norm_conn.execute(analytics_query):
        analytics_data.append(tuple(row))
    
    for chunk in batch(analytics_data, 500):
        denorm_conn.executemany("""
            INSERT INTO return_analytics VALUES 
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building daily return metrics...")
    daily_query = """
    WITH daily_stats AS (
        SELECT 
            DATE(r.request_date) as date,
            COUNT(*) as total_requests,
            COUNT(CASE WHEN r.status IN ('APPROVED', 'SHIPPED', 'RECEIVED', 'INSPECTED', 'PROCESSED', 'CLOSED') THEN 1 END) as approved_count,
            COUNT(CASE WHEN r.status = 'REJECTED' THEN 1 END) as rejected_count,
            COUNT(CASE WHEN r.status = 'PENDING' THEN 1 END) as pending_count,
            SUM(CASE 
                WHEN i.recommendation = 'FULL_REFUND' THEN oi.unit_price * oi.quantity - oi.discount_amount
                WHEN i.recommendation = 'PARTIAL_REFUND' THEN 
                    (oi.unit_price * oi.quantity - oi.discount_amount) * (100 - i.deduction_percentage) / 100
                ELSE 0
            END) as total_refund_amount,
            AVG(CASE 
                WHEN r.status IN ('PROCESSED', 'CLOSED') THEN
                    julianday(DATE('now')) - julianday(r.request_date)
            END) as avg_processing_days
        FROM rma_requests r
        JOIN order_items oi ON r.order_item_id = oi.id
        LEFT JOIN rma_inspections i ON r.id = i.rma_id
        GROUP BY DATE(r.request_date)
    ),
    order_stats AS (
        SELECT 
            DATE(order_date) as date,
            COUNT(DISTINCT id) as daily_orders
        FROM orders
        WHERE status = 'DELIVERED'
        GROUP BY DATE(order_date)
    )
    SELECT 
        ds.date,
        ds.total_requests,
        ds.approved_count,
        ds.rejected_count,
        ds.pending_count,
        COALESCE(ds.total_refund_amount, 0) as total_refund_amount,
        ds.avg_processing_days,
        COALESCE(ds.total_requests * 1.0 / os.daily_orders, 0) as return_rate
    FROM daily_stats ds
    LEFT JOIN order_stats os ON DATE(ds.date, '-30 days') = os.date
    """
    
    daily_data = []
    for row in norm_conn.execute(daily_query):
        daily_data.append((
            row['date'],
            row['total_requests'],
            row['approved_count'],
            row['rejected_count'],
            row['pending_count'],
            row['total_refund_amount'] or 0,
            row['avg_processing_days'],
            row['return_rate'] or 0
        ))
    
    denorm_conn.executemany("""
        INSERT INTO daily_return_metrics VALUES 
        (?,?,?,?,?,?,?,?)
    """, daily_data)
    
    print("Building product return analysis...")
    product_query = """
    WITH monthly_sales AS (
        SELECT 
            p.sku as product_sku,
            strftime('%Y-%m', o.order_date) as month,
            SUM(oi.quantity) as units_sold
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status = 'DELIVERED'
        GROUP BY p.sku, strftime('%Y-%m', o.order_date)
    ),
    monthly_returns AS (
        SELECT 
            p.sku as product_sku,
            strftime('%Y-%m', r.request_date) as month,
            COUNT(*) as units_returned,
            'DEFECTIVE' as primary_return_reason,  -- Simplified: most common reason
            AVG(julianday(r.request_date) - julianday(o.order_date)) as avg_days_to_return,
            SUM(CASE 
                WHEN i.recommendation IN ('FULL_REFUND', 'PARTIAL_REFUND') THEN
                    oi.unit_price * oi.quantity - oi.discount_amount
                ELSE 0
            END) as total_loss
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        JOIN rma_requests r ON oi.id = r.order_item_id
        JOIN orders o ON oi.order_id = o.id
        LEFT JOIN rma_inspections i ON r.id = i.rma_id
        GROUP BY p.sku, strftime('%Y-%m', r.request_date)
    )
    SELECT 
        ms.product_sku,
        ms.month,
        ms.units_sold,
        COALESCE(mr.units_returned, 0) as units_returned,
        COALESCE(mr.units_returned * 1.0 / ms.units_sold, 0) as return_rate,
        mr.primary_return_reason,
        mr.avg_days_to_return,
        COALESCE(mr.total_loss, 0) as total_loss,
        CASE 
            WHEN COALESCE(mr.units_returned * 1.0 / ms.units_sold, 0) < 0.05 THEN 9.0
            WHEN COALESCE(mr.units_returned * 1.0 / ms.units_sold, 0) < 0.10 THEN 7.0
            WHEN COALESCE(mr.units_returned * 1.0 / ms.units_sold, 0) < 0.20 THEN 5.0
            ELSE 3.0
        END as quality_score
    FROM monthly_sales ms
    LEFT JOIN monthly_returns mr ON ms.product_sku = mr.product_sku AND ms.month = mr.month
    """
    
    product_data = []
    for row in norm_conn.execute(product_query):
        product_data.append(tuple(row))
    
    for chunk in batch(product_data, 500):
        denorm_conn.executemany("""
            INSERT INTO product_return_analysis VALUES 
            (?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building customer return behavior...")
    behavior_query = """
    WITH customer_stats AS (
        SELECT 
            c.id as customer_id,
            c.email as customer_email,
            c.loyalty_tier,
            COUNT(DISTINCT o.id) as total_orders,
            COUNT(DISTINCT r.id) as total_returns,
            AVG(oi.unit_price * oi.quantity - oi.discount_amount) as avg_return_value,
            'PREPAID_LABEL' as preferred_return_method,  -- Simplified: most common method
            MAX(r.request_date) as last_return_date
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        LEFT JOIN rma_requests r ON c.id = r.customer_id
        LEFT JOIN order_items oi ON r.order_item_id = oi.id
        WHERE o.status = 'DELIVERED'
        GROUP BY c.id
    )
    SELECT 
        customer_id,
        customer_email,
        loyalty_tier,
        total_orders,
        total_returns,
        COALESCE(total_returns * 1.0 / total_orders, 0) as return_rate,
        avg_return_value,
        preferred_return_method,
        CASE 
            WHEN COALESCE(total_returns * 1.0 / total_orders, 0) > 0.5 THEN 80
            WHEN COALESCE(total_returns * 1.0 / total_orders, 0) > 0.3 THEN 60
            WHEN COALESCE(total_returns * 1.0 / total_orders, 0) > 0.2 THEN 40
            WHEN COALESCE(total_returns * 1.0 / total_orders, 0) > 0.1 THEN 20
            ELSE 10
        END as fraud_risk_score,
        last_return_date
    FROM customer_stats
    WHERE total_orders > 0
    """
    
    behavior_data = []
    for row in norm_conn.execute(behavior_query):
        behavior_data.append(tuple(row))
    
    for chunk in batch(behavior_data, 500):
        denorm_conn.executemany("""
            INSERT INTO customer_return_behavior VALUES 
            (?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_return_analytics_date ON return_analytics(return_request_date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_return_analytics_category ON return_analytics(product_category)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_return_analytics_reason ON return_analytics(return_reason)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_return_metrics(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_product_analysis_rate ON product_return_analysis(return_rate DESC)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()