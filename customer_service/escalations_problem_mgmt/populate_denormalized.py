#!/usr/bin/env python3
"""Populate escalations problem management denormalized schema with analytical data."""
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
    
    # Connect to both databases
    norm_conn = sqlite3.connect(args.normalized_db)
    norm_conn.row_factory = sqlite3.Row
    denorm_conn = sqlite3.connect(args.denormalized_db)
    
    print("Building issue analytics...")
    # Build issue_analytics table with escalation chain
    analytics_query = """
    WITH escalation_chains AS (
        SELECT 
            e.issue_id,
            GROUP_CONCAT(a.name || ' (' || a.skill_level || ')', ' -> ') as chain,
            COUNT(*) as escalation_count
        FROM escalations e
        JOIN agents a ON e.to_agent_id = a.id
        GROUP BY e.issue_id
    ),
    final_resolvers AS (
        SELECT 
            i.id as issue_id,
            a.name as resolver_name,
            a.skill_level as resolver_level
        FROM issues i
        JOIN agents a ON a.id = (
            SELECT COALESCE(
                (SELECT to_agent_id FROM escalations WHERE issue_id = i.id ORDER BY escalated_at DESC LIMIT 1),
                i.created_by_agent_id
            )
        )
    )
    SELECT 
        i.id as issue_id,
        c.name as customer_name,
        c.tier as customer_tier,
        c.account_value,
        i.category,
        i.severity,
        i.status,
        i.created_at,
        i.resolved_at,
        CASE 
            WHEN i.resolved_at IS NOT NULL THEN 
                CAST((julianday(i.resolved_at) - julianday(i.created_at)) * 24 AS INTEGER)
            ELSE NULL 
        END as resolution_hours,
        COALESCE(ec.escalation_count, 0) as total_escalations,
        ec.chain as escalation_chain,
        fr.resolver_name as final_resolver_name,
        fr.resolver_level as final_resolver_level,
        CASE WHEN pr.id IS NOT NULL THEN 1 ELSE 0 END as has_problem_record,
        pr.affected_customers
    FROM issues i
    JOIN customers c ON i.customer_id = c.id
    LEFT JOIN escalation_chains ec ON i.id = ec.issue_id
    LEFT JOIN final_resolvers fr ON i.id = fr.issue_id
    LEFT JOIN problem_records pr ON i.id = pr.root_issue_id
    """
    
    analytics_data = []
    for row in norm_conn.execute(analytics_query):
        analytics_data.append(tuple(row))
    
    # Insert in batches
    for chunk in batch(analytics_data, 1000):
        denorm_conn.executemany("""
            INSERT INTO issue_analytics VALUES 
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building daily escalation metrics...")
    # Build daily_escalation_metrics
    daily_query = """
    WITH daily_issues AS (
        SELECT 
            DATE(i.created_at) as date,
            a.department,
            COUNT(DISTINCT i.id) as total_issues,
            COUNT(DISTINCT CASE WHEN e.id IS NOT NULL THEN i.id END) as escalated_issues,
            COUNT(DISTINCT CASE WHEN i.severity = 'CRITICAL' THEN i.id END) as critical_issues,
            COUNT(DISTINCT CASE 
                WHEN i.severity = 'CRITICAL' AND i.resolved_at IS NULL 
                    OR (julianday(i.resolved_at) - julianday(i.created_at)) * 24 > 4
                THEN i.id 
            END) as sla_breaches,
            COUNT(e.id) as total_escalations
        FROM issues i
        JOIN agents a ON i.created_by_agent_id = a.id
        LEFT JOIN escalations e ON i.id = e.issue_id
        GROUP BY DATE(i.created_at), a.department
    )
    SELECT 
        date,
        department,
        total_issues,
        escalated_issues,
        CAST(escalated_issues AS REAL) / total_issues as escalation_rate,
        CAST(total_escalations AS REAL) / NULLIF(escalated_issues, 0) as avg_escalations_per_issue,
        critical_issues,
        sla_breaches
    FROM daily_issues
    """
    
    daily_data = []
    for row in norm_conn.execute(daily_query):
        daily_data.append((
            row['date'],
            row['department'],
            row['total_issues'],
            row['escalated_issues'],
            row['escalation_rate'],
            row['avg_escalations_per_issue'],
            row['critical_issues'],
            row['sla_breaches']
        ))
    
    denorm_conn.executemany("""
        INSERT INTO daily_escalation_metrics VALUES 
        (?,?,?,?,?,?,?,?)
    """, daily_data)
    
    print("Building agent performance metrics...")
    # Build agent_performance
    agent_query = """
    WITH agent_metrics AS (
        SELECT 
            a.id as agent_id,
            strftime('%Y-%m', i.created_at) as month,
            a.skill_level,
            COUNT(DISTINCT i.id) as issues_handled,
            COUNT(DISTINCT CASE WHEN i.status IN ('RESOLVED', 'CLOSED') THEN i.id END) as issues_resolved,
            COUNT(DISTINCT e_out.issue_id) as issues_escalated_up,
            COUNT(DISTINCT e_in.issue_id) as issues_received_from_escalation,
            AVG(CASE 
                WHEN i.resolved_at IS NOT NULL THEN 
                    (julianday(i.resolved_at) - julianday(i.created_at)) * 24
            END) as avg_resolution_hours
        FROM agents a
        LEFT JOIN issues i ON a.id = i.created_by_agent_id OR a.id IN (
            SELECT to_agent_id FROM escalations WHERE issue_id = i.id
        )
        LEFT JOIN escalations e_out ON a.id = e_out.from_agent_id
        LEFT JOIN escalations e_in ON a.id = e_in.to_agent_id
        GROUP BY a.id, strftime('%Y-%m', i.created_at), a.skill_level
    ),
    tier_distribution AS (
        SELECT 
            a.id as agent_id,
            strftime('%Y-%m', i.created_at) as month,
            c.tier,
            COUNT(*) as count
        FROM agents a
        JOIN issues i ON a.id = i.created_by_agent_id OR a.id IN (
            SELECT to_agent_id FROM escalations WHERE issue_id = i.id
        )
        JOIN customers c ON i.customer_id = c.id
        GROUP BY a.id, strftime('%Y-%m', i.created_at), c.tier
    )
    SELECT 
        am.agent_id,
        am.month,
        am.skill_level,
        am.issues_handled,
        am.issues_resolved,
        am.issues_escalated_up,
        am.issues_received_from_escalation,
        CAST(am.issues_resolved AS REAL) / NULLIF(am.issues_handled, 0) as resolution_rate,
        am.avg_resolution_hours,
        json_group_object(td.tier, td.count) as customer_tier_distribution
    FROM agent_metrics am
    LEFT JOIN tier_distribution td ON am.agent_id = td.agent_id AND am.month = td.month
    WHERE am.issues_handled > 0
    GROUP BY am.agent_id, am.month
    """
    
    agent_data = []
    for row in norm_conn.execute(agent_query):
        agent_data.append((
            row['agent_id'],
            row['month'],
            row['skill_level'],
            row['issues_handled'],
            row['issues_resolved'],
            row['issues_escalated_up'],
            row['issues_received_from_escalation'],
            row['resolution_rate'],
            row['avg_resolution_hours'],
            row['customer_tier_distribution']
        ))
    
    for chunk in batch(agent_data, 500):
        denorm_conn.executemany("""
            INSERT INTO agent_performance VALUES 
            (?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building problem impact summary...")
    # Build problem_impact_summary
    problem_query = """
    SELECT 
        pr.id as problem_id,
        pr.problem_statement,
        i.category,
        pr.root_cause,
        pr.affected_customers as total_affected_customers,
        COUNT(DISTINCT ri.id) as total_related_issues,
        AVG(CASE 
            WHEN ri.resolved_at IS NOT NULL THEN 
                (julianday(ri.resolved_at) - julianday(ri.created_at)) * 24
        END) as avg_resolution_hours,
        SUM(c.account_value * 0.1) as revenue_at_risk,
        pr.created_at,
        CASE 
            WHEN pr.root_cause IS NOT NULL AND pr.root_cause != 'Under investigation' THEN
                CAST((julianday(pr.created_at) - julianday(i.created_at)) * 24 AS INTEGER) + 48
            ELSE NULL
        END as time_to_root_cause_hours,
        CASE 
            WHEN pr.closed_at IS NOT NULL THEN
                CAST((julianday(pr.closed_at) - julianday(pr.created_at)) * 24 AS INTEGER)
            ELSE NULL
        END as time_to_resolution_hours
    FROM problem_records pr
    JOIN issues i ON pr.root_issue_id = i.id
    JOIN customers c ON i.customer_id = c.id
    LEFT JOIN issues ri ON ri.category = i.category 
        AND ri.created_at >= pr.created_at 
        AND ri.created_at <= COALESCE(pr.closed_at, datetime('now'))
    GROUP BY pr.id
    """
    
    problem_data = []
    for row in norm_conn.execute(problem_query):
        problem_data.append(tuple(row))
    
    denorm_conn.executemany("""
        INSERT INTO problem_impact_summary VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, problem_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_issue_analytics_date ON issue_analytics(created_at)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_issue_analytics_tier ON issue_analytics(customer_tier)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_escalation_metrics(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_performance_month ON agent_performance(month)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_problem_impact_customers ON problem_impact_summary(total_affected_customers DESC)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()