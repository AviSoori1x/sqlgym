#!/usr/bin/env python3
"""Populate ecommerce funnel A/B test denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
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
    
    print("Building experiment results...")
    results_query = """
    SELECT 
        us.experiment_id,
        us.variant_id,
        DATE(us.start_timestamp) as date,
        COUNT(*) as sessions,
        COUNT(CASE WHEN us.converted = 1 THEN 1 END) as conversions,
        AVG(CASE WHEN us.converted = 1 THEN us.conversion_value END) as avg_order_value,
        SUM(us.conversion_value) as total_revenue
    FROM user_sessions us
    WHERE us.experiment_id IS NOT NULL
    GROUP BY us.experiment_id, us.variant_id, DATE(us.start_timestamp)
    """
    
    results_data = []
    for row in norm_conn.execute(results_query):
        conversion_rate = row['conversions'] / row['sessions'] if row['sessions'] > 0 else 0
        
        # Simplified statistical significance calculation
        significance = 0.95 if row['conversions'] > 30 else 0.80
        ci_lower = max(0, conversion_rate - 0.02)
        ci_upper = min(1, conversion_rate + 0.02)
        
        results_data.append((
            row['experiment_id'], row['variant_id'], row['date'],
            row['sessions'], row['conversions'], conversion_rate,
            row['total_revenue'] or 0, row['avg_order_value'] or 0,
            significance, ci_lower, ci_upper
        ))
    
    denorm_conn.executemany("""
        INSERT INTO experiment_results VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, results_data)
    
    print("Building funnel analysis...")
    funnel_query = """
    SELECT 
        DATE(fe.timestamp) as date,
        us.experiment_id,
        us.variant_id,
        fs.id as funnel_step_id,
        fs.name as step_name,
        fs.step_order,
        COUNT(DISTINCT fe.session_id) as sessions_entered,
        AVG(fe.time_on_step) as avg_time_on_step
    FROM funnel_events fe
    JOIN funnel_steps fs ON fe.funnel_step_id = fs.id
    LEFT JOIN user_sessions us ON fe.session_id = us.session_id
    GROUP BY DATE(fe.timestamp), us.experiment_id, us.variant_id, fs.id
    """
    
    funnel_data = []
    for row in norm_conn.execute(funnel_query):
        # Calculate completion rate (simplified)
        sessions_completed = int(row['sessions_entered'] * 0.85)  # Simplified
        completion_rate = sessions_completed / row['sessions_entered'] if row['sessions_entered'] > 0 else 0
        drop_off_rate = 1 - completion_rate
        
        funnel_data.append((
            row['date'], row['experiment_id'], row['variant_id'],
            row['funnel_step_id'], row['step_name'], row['step_order'],
            row['sessions_entered'], sessions_completed, completion_rate,
            int(row['avg_time_on_step'] or 0), drop_off_rate
        ))
    
    denorm_conn.executemany("""
        INSERT INTO funnel_analysis VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, funnel_data)
    
    print("Building cohort funnel performance...")
    cohort_query = """
    SELECT 
        DATE(us.start_timestamp) as cohort_date,
        us.traffic_source,
        us.device_type,
        fs.id as funnel_step_id,
        COUNT(DISTINCT us.id) as cohort_size,
        COUNT(DISTINCT fe.session_id) as step_completions,
        AVG(julianday(fe.timestamp) - julianday(us.start_timestamp)) as avg_days_to_complete
    FROM user_sessions us
    LEFT JOIN funnel_events fe ON us.session_id = fe.session_id
    LEFT JOIN funnel_steps fs ON fe.funnel_step_id = fs.id
    WHERE fs.id IS NOT NULL
    GROUP BY DATE(us.start_timestamp), us.traffic_source, us.device_type, fs.id
    """
    
    cohort_data = []
    for row in norm_conn.execute(cohort_query):
        completion_rate = row['step_completions'] / row['cohort_size'] if row['cohort_size'] > 0 else 0
        
        cohort_data.append((
            row['cohort_date'], row['traffic_source'], row['device_type'],
            row['funnel_step_id'], row['cohort_size'], row['step_completions'],
            completion_rate, row['avg_days_to_complete'] or 0
        ))
    
    denorm_conn.executemany("""
        INSERT INTO cohort_funnel_performance VALUES 
        (?,?,?,?,?,?,?,?)
    """, cohort_data)
    
    print("Building A/B test summaries...")
    summary_query = """
    SELECT 
        e.id as experiment_id,
        e.name as experiment_name,
        e.status,
        COUNT(DISTINCT us.id) as total_sessions,
        AVG(CASE WHEN v.variant_type = 'CONTROL' AND us.converted = 1 THEN 1.0 ELSE 0.0 END) as control_conversion_rate,
        AVG(CASE WHEN v.variant_type = 'TREATMENT' AND us.converted = 1 THEN 1.0 ELSE 0.0 END) as treatment_conversion_rate,
        SUM(us.conversion_value) as revenue_impact,
        e.start_date,
        e.end_date
    FROM experiments e
    LEFT JOIN user_sessions us ON e.id = us.experiment_id
    LEFT JOIN variants v ON us.variant_id = v.id
    GROUP BY e.id
    """
    
    summary_data = []
    for row in norm_conn.execute(summary_query):
        control_rate = row['control_conversion_rate'] or 0
        treatment_rate = row['treatment_conversion_rate'] or 0
        
        if control_rate > 0:
            lift_percentage = ((treatment_rate - control_rate) / control_rate) * 100
        else:
            lift_percentage = 0
        
        significance = 0.95 if row['total_sessions'] > 1000 else 0.80
        winner_variant = 2 if treatment_rate > control_rate else 1  # Simplified
        
        summary_data.append((
            row['experiment_id'], row['experiment_name'], row['status'],
            row['total_sessions'] or 0, control_rate, treatment_rate,
            lift_percentage, significance, winner_variant,
            row['revenue_impact'] or 0, row['start_date'], row['end_date']
        ))
    
    denorm_conn.executemany("""
        INSERT INTO ab_test_summary VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?)
    """, summary_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_experiment_results_date ON experiment_results(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_funnel_analysis_date ON funnel_analysis(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_cohort_performance_date ON cohort_funnel_performance(cohort_date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_ab_summary_status ON ab_test_summary(status)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()