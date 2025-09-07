#!/usr/bin/env python3
"""Populate chatbot deflection denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import batch

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized-db", required=True)
    parser.add_argument("--denormalized-db", required=True)
    args = parser.parse_args()
    
    # Connect to both databases
    norm_conn = sqlite3.connect(args.normalized_db)
    norm_conn.row_factory = sqlite3.Row
    denorm_conn = sqlite3.connect(args.denormalized_db)
    
    print("Building conversation analytics...")
    # Build conversation_analytics table
    conv_query = """
    SELECT 
        c.id as conversation_id,
        cu.email as customer_email,
        c.channel,
        c.started_at,
        c.ended_at,
        CASE 
            WHEN c.ended_at IS NOT NULL THEN 
                CAST((julianday(c.ended_at) - julianday(c.started_at)) * 86400 AS INTEGER)
            ELSE NULL 
        END as duration_seconds,
        c.status,
        ic.name as primary_intent,
        COUNT(DISTINCT m.id) as message_count,
        COUNT(DISTINCT CASE WHEN m.sender_type = 'BOT' THEN m.id END) as bot_message_count,
        COUNT(DISTINCT CASE WHEN m.sender_type = 'CUSTOMER' THEN m.id END) as customer_message_count,
        AVG(m.confidence_score) as avg_confidence_score,
        CASE WHEN e.id IS NOT NULL THEN 1 ELSE 0 END as was_escalated,
        e.reason as escalation_reason,
        c.satisfaction_score,
        CASE 
            WHEN c.status = 'RESOLVED' AND e.id IS NULL THEN 'BOT_DEFLECTED'
            WHEN c.status = 'ESCALATED' THEN 'AGENT_RESOLVED'
            WHEN c.status = 'ABANDONED' THEN 'ABANDONED'
            ELSE 'OTHER'
        END as resolution_type
    FROM conversations c
    JOIN customers cu ON c.customer_id = cu.id
    LEFT JOIN intent_categories ic ON c.primary_intent_id = ic.id
    LEFT JOIN messages m ON c.id = m.conversation_id
    LEFT JOIN escalations e ON c.id = e.conversation_id
    GROUP BY c.id
    """
    
    conv_data = []
    for row in norm_conn.execute(conv_query):
        conv_data.append(tuple(row))
    
    # Insert in batches
    for chunk in batch(conv_data, 1000):
        denorm_conn.executemany("""
            INSERT INTO conversation_analytics VALUES 
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building daily deflection metrics...")
    # Build daily_deflection_metrics
    daily_query = """
    SELECT 
        DATE(c.started_at) as date,
        c.channel,
        COUNT(*) as total_conversations,
        COUNT(CASE WHEN c.status = 'RESOLVED' AND e.id IS NULL THEN 1 END) as deflected_count,
        COUNT(CASE WHEN c.status = 'ESCALATED' THEN 1 END) as escalated_count,
        COUNT(CASE WHEN c.status = 'ABANDONED' THEN 1 END) as abandoned_count,
        AVG(c.satisfaction_score) as avg_satisfaction,
        AVG(CASE 
            WHEN c.ended_at IS NOT NULL THEN 
                CAST((julianday(c.ended_at) - julianday(c.started_at)) * 86400 AS INTEGER)
            ELSE NULL 
        END) as avg_duration_seconds,
        CAST(COUNT(CASE WHEN c.status = 'RESOLVED' AND e.id IS NULL THEN 1 END) AS REAL) / 
            COUNT(*) as deflection_rate
    FROM conversations c
    LEFT JOIN escalations e ON c.id = e.conversation_id
    GROUP BY DATE(c.started_at), c.channel
    """
    
    daily_data = []
    for row in norm_conn.execute(daily_query):
        daily_data.append(tuple(row))
    
    denorm_conn.executemany("""
        INSERT INTO daily_deflection_metrics VALUES 
        (?,?,?,?,?,?,?,?,?)
    """, daily_data)
    
    print("Building intent performance metrics...")
    # Build intent_performance
    intent_query = """
    SELECT 
        ic.name as intent_name,
        strftime('%Y-%m', c.started_at) as month,
        COUNT(*) as total_occurrences,
        COUNT(CASE WHEN c.status = 'RESOLVED' AND e.id IS NULL THEN 1 END) as successful_deflections,
        COUNT(CASE WHEN e.id IS NOT NULL THEN 1 END) as escalations,
        AVG(m.confidence_score) as avg_confidence,
        CAST(COUNT(CASE WHEN c.status = 'RESOLVED' AND e.id IS NULL THEN 1 END) AS REAL) / 
            COUNT(*) as deflection_success_rate
    FROM conversations c
    JOIN intent_categories ic ON c.primary_intent_id = ic.id
    LEFT JOIN messages m ON c.id = m.conversation_id AND m.sender_type = 'BOT'
    LEFT JOIN escalations e ON c.id = e.conversation_id
    GROUP BY ic.name, strftime('%Y-%m', c.started_at)
    """
    
    intent_data = []
    for row in norm_conn.execute(intent_query):
        intent_data.append(tuple(row))
    
    denorm_conn.executemany("""
        INSERT INTO intent_performance VALUES 
        (?,?,?,?,?,?,?)
    """, intent_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_analytics_status ON conversation_analytics(status)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_analytics_date ON conversation_analytics(started_at)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_analytics_intent ON conversation_analytics(primary_intent)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_deflection_metrics(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_intent_perf_month ON intent_performance(month)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
