#!/usr/bin/env python3
"""Populate onboarding customer training denormalized schema with analytical data."""
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
    
    rng = get_rng(42)  # Add missing RNG initialization
    
    norm_conn = sqlite3.connect(args.normalized_db)
    norm_conn.row_factory = sqlite3.Row
    denorm_conn = sqlite3.connect(args.denormalized_db)
    
    print("Building customer training summary...")
    summary_query = """
    WITH customer_stats AS (
        SELECT 
            c.id as customer_id,
            c.name as customer_name,
            c.company_size,
            c.onboarding_tier,
            COUNT(DISTINCT e.id) as total_programs_enrolled,
            COUNT(DISTINCT CASE WHEN e.status = 'COMPLETED' THEN e.id END) as programs_completed,
            COUNT(DISTINCT CASE WHEN e.status = 'IN_PROGRESS' THEN e.id END) as programs_in_progress,
            SUM(CASE WHEN e.status = 'COMPLETED' THEN tp.duration_hours ELSE 0 END) as total_training_hours,
            MAX(e.enrolled_at) as last_activity_date,
            MIN(CASE WHEN e.status = 'COMPLETED' THEN e.completed_at END) as first_completion,
            MIN(e.enrolled_at) as first_enrollment,
            COUNT(DISTINCT CASE WHEN tp.program_type = 'CERTIFICATION' AND e.status = 'COMPLETED' THEN e.id END) as certification_count
        FROM customers c
        LEFT JOIN enrollments e ON c.id = e.customer_id
        LEFT JOIN training_programs tp ON e.program_id = tp.id
        GROUP BY c.id
    ),
    onboarding_check AS (
        SELECT 
            e.customer_id,
            CASE 
                WHEN COUNT(CASE WHEN tp.is_mandatory = 1 AND e.status != 'COMPLETED' THEN 1 END) = 0 
                THEN 'COMPLETED'
                WHEN COUNT(CASE WHEN tp.is_mandatory = 1 AND e.status = 'IN_PROGRESS' THEN 1 END) > 0
                THEN 'IN_PROGRESS'
                ELSE 'PENDING'
            END as onboarding_status
        FROM enrollments e
        JOIN training_programs tp ON e.program_id = tp.id
        WHERE tp.is_mandatory = 1
        GROUP BY e.customer_id
    )
    SELECT 
        cs.*,
        COALESCE(oc.onboarding_status, 'NOT_STARTED') as onboarding_status,
        CASE 
            WHEN cs.first_completion IS NOT NULL THEN
                CAST((julianday(cs.first_completion) - julianday(cs.first_enrollment)) AS INTEGER)
            ELSE NULL
        END as days_to_first_completion
    FROM customer_stats cs
    LEFT JOIN onboarding_check oc ON cs.customer_id = oc.customer_id
    """
    
    summary_data = []
    for row in norm_conn.execute(summary_query):
        completion_rate = row['programs_completed'] / row['total_programs_enrolled'] if row['total_programs_enrolled'] > 0 else 0
        
        summary_data.append((
            row['customer_id'],
            row['customer_name'],
            row['company_size'],
            row['onboarding_tier'],
            row['total_programs_enrolled'] or 0,
            row['programs_completed'] or 0,
            row['programs_in_progress'] or 0,
            completion_rate,
            row['total_training_hours'] or 0,
            row['last_activity_date'],
            row['onboarding_status'],
            row['days_to_first_completion'],
            row['certification_count'] or 0
        ))
    
    for chunk in batch(summary_data, 500):
        denorm_conn.executemany("""
            INSERT INTO customer_training_summary VALUES 
            (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building program effectiveness metrics...")
    effectiveness_query = """
    SELECT 
        tp.id as program_id,
        tp.name as program_name,
        tp.program_type,
        strftime('%Y-%m', e.enrolled_at) as month,
        COUNT(*) as total_enrollments,
        COUNT(CASE WHEN e.status = 'COMPLETED' THEN 1 END) as completions,
        COUNT(CASE WHEN e.status = 'DROPPED' THEN 1 END) as dropouts,
        AVG(CASE 
            WHEN e.completed_at IS NOT NULL THEN
                julianday(e.completed_at) - julianday(e.started_at)
        END) as avg_time_to_complete_days,
        AVG(mp.score) as avg_score
    FROM training_programs tp
    LEFT JOIN enrollments e ON tp.id = e.program_id
    LEFT JOIN modules m ON tp.id = m.program_id AND m.passing_score IS NOT NULL
    LEFT JOIN module_progress mp ON e.id = mp.enrollment_id AND m.id = mp.module_id
    WHERE e.id IS NOT NULL
    GROUP BY tp.id, strftime('%Y-%m', e.enrolled_at)
    """
    
    effectiveness_data = []
    for row in norm_conn.execute(effectiveness_query):
        completion_rate = row['completions'] / row['total_enrollments'] if row['total_enrollments'] > 0 else 0
        dropout_rate = row['dropouts'] / row['total_enrollments'] if row['total_enrollments'] > 0 else 0
        satisfaction = 4.2 + rng.uniform(-0.5, 0.5)  # Simulated satisfaction
        
        effectiveness_data.append((
            row['program_id'],
            row['program_name'],
            row['program_type'],
            row['month'],
            row['total_enrollments'],
            row['completions'],
            completion_rate,
            row['avg_time_to_complete_days'],
            row['avg_score'],
            dropout_rate,
            satisfaction
        ))
    
    denorm_conn.executemany("""
        INSERT INTO program_effectiveness VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, effectiveness_data)
    
    print("Building cohort analysis...")
    cohort_query = """
    WITH cohort_base AS (
        SELECT 
            strftime('%Y-%m', MIN(e.enrolled_at)) as cohort_month,
            c.onboarding_tier,
            c.id as customer_id,
            MIN(e.enrolled_at) as first_activity
        FROM customers c
        JOIN enrollments e ON c.id = e.customer_id
        GROUP BY c.id
    ),
    activity_metrics AS (
        SELECT 
            cb.cohort_month,
            cb.onboarding_tier,
            cb.customer_id,
            MAX(CASE WHEN julianday(e.enrolled_at) - julianday(cb.first_activity) <= 1 THEN 1 ELSE 0 END) as day_1,
            MAX(CASE WHEN julianday(e.enrolled_at) - julianday(cb.first_activity) <= 7 THEN 1 ELSE 0 END) as day_7,
            MAX(CASE WHEN julianday(e.enrolled_at) - julianday(cb.first_activity) <= 30 THEN 1 ELSE 0 END) as day_30,
            MAX(CASE WHEN julianday(e.enrolled_at) - julianday(cb.first_activity) <= 90 THEN 1 ELSE 0 END) as day_90,
            MAX(CASE WHEN tp.program_type = 'ONBOARDING' AND e.status = 'COMPLETED' THEN 1 ELSE 0 END) as onboarded,
            COUNT(CASE WHEN e.status = 'COMPLETED' THEN 1 END) as programs_completed
        FROM cohort_base cb
        LEFT JOIN enrollments e ON cb.customer_id = e.customer_id
        LEFT JOIN training_programs tp ON e.program_id = tp.id
        GROUP BY cb.customer_id
    )
    SELECT 
        cohort_month,
        onboarding_tier,
        COUNT(*) as cohort_size,
        SUM(day_1) as day_1_active,
        SUM(day_7) as day_7_active,
        SUM(day_30) as day_30_active,
        SUM(day_90) as day_90_active,
        SUM(onboarded) as onboarding_completed,
        AVG(programs_completed) as avg_programs_completed
    FROM activity_metrics
    GROUP BY cohort_month, onboarding_tier
    """
    
    cohort_data = []
    for row in norm_conn.execute(cohort_query):
        # Simulate time to value
        time_to_value = {
            'SELF_SERVICE': 14,
            'STANDARD': 10,
            'PREMIUM': 7,
            'WHITE_GLOVE': 3
        }[row['onboarding_tier']] + rng.randint(-2, 2)
        
        cohort_data.append((
            row['cohort_month'],
            row['onboarding_tier'],
            row['cohort_size'],
            row['day_1_active'],
            row['day_7_active'],
            row['day_30_active'],
            row['day_90_active'],
            row['onboarding_completed'],
            row['avg_programs_completed'],
            time_to_value
        ))
    
    denorm_conn.executemany("""
        INSERT INTO cohort_analysis VALUES 
        (?,?,?,?,?,?,?,?,?,?)
    """, cohort_data)
    
    print("Building learning path analytics...")
    # Simplified learning paths - in practice would use graph algorithms
    path_query = """
    SELECT 
        c.id as customer_id,
        GROUP_CONCAT(tp.name, ' -> ') as learning_path,
        COUNT(*) as path_length,
        COUNT(CASE WHEN e.status = 'COMPLETED' THEN 1 END) as current_position
    FROM customers c
    JOIN enrollments e ON c.id = e.customer_id
    JOIN training_programs tp ON e.program_id = tp.id
    WHERE e.status IN ('COMPLETED', 'IN_PROGRESS')
    GROUP BY c.id
    """
    
    import random
    rng = random.Random(42)
    
    path_data = []
    for row in norm_conn.execute(path_query):
        # Estimate completion date
        if row['current_position'] < row['path_length']:
            days_remaining = (row['path_length'] - row['current_position']) * 21
            est_completion = datetime.now() + timedelta(days=days_remaining)
            est_completion_str = est_completion.strftime('%Y-%m-%d')
        else:
            est_completion_str = None
        
        # Mock recommendations
        recommendations = ['Advanced Analytics', 'API Mastery', 'Best Practices']
        blockers = [] if row['current_position'] > 0 else ['Complete Getting Started']
        
        path_data.append((
            row['customer_id'],
            json.dumps(row['learning_path'].split(' -> ')),
            row['path_length'],
            row['current_position'],
            est_completion_str,
            json.dumps(blockers),
            json.dumps(rng.sample(recommendations, 2))
        ))
    
    for chunk in batch(path_data, 500):
        denorm_conn.executemany("""
            INSERT INTO learning_path_analytics VALUES 
            (?,?,?,?,?,?,?)
        """, chunk)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_training_summary_tier ON customer_training_summary(onboarding_tier)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_training_summary_status ON customer_training_summary(onboarding_status)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_program_effectiveness_type ON program_effectiveness(program_type)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_cohort_month ON cohort_analysis(cohort_month)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_path_position ON learning_path_analytics(current_position)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()