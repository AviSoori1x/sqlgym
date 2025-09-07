#!/usr/bin/env python3
"""Populate workforce management denormalized schema with analytical data."""
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
    
    print("Building agent performance summary...")
    summary_query = """
    SELECT 
        a.id as agent_id,
        a.employee_id,
        a.name,
        a.department,
        a.skill_level,
        COUNT(DISTINCT s.id) as total_shifts_scheduled,
        COUNT(DISTINCT CASE WHEN s.status = 'COMPLETED' THEN s.id END) as shifts_completed,
        AVG(s.overtime_minutes) as avg_overtime_minutes,
        COUNT(DISTINCT tor.id) as time_off_requests,
        COUNT(DISTINCT ask.skill_id) as skill_count,
        AVG(ask.proficiency_level) as avg_skill_proficiency,
        MAX(sh.shift_date) as last_shift_date
    FROM agents a
    LEFT JOIN schedules s ON a.id = s.agent_id
    LEFT JOIN shifts sh ON s.shift_id = sh.id
    LEFT JOIN agent_skills ask ON a.id = ask.agent_id
    LEFT JOIN time_off_requests tor ON a.id = tor.agent_id AND tor.status = 'APPROVED'
    GROUP BY a.id
    """
    
    summary_data = []
    for row in norm_conn.execute(summary_query):
        attendance_rate = row['shifts_completed'] / row['total_shifts_scheduled'] if row['total_shifts_scheduled'] > 0 else 0
        time_off_days = row['time_off_requests'] * 3  # Simplified calculation
        
        summary_data.append((
            row['agent_id'],
            row['employee_id'],
            row['name'],
            row['department'],
            row['skill_level'],
            row['total_shifts_scheduled'] or 0,
            row['shifts_completed'] or 0,
            attendance_rate,
            row['avg_overtime_minutes'] or 0,
            time_off_days,
            row['skill_count'] or 0,
            row['avg_skill_proficiency'] or 0,
            row['last_shift_date']
        ))
    
    denorm_conn.executemany("""
        INSERT INTO agent_performance_summary VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, summary_data)
    
    print("Building daily staffing metrics...")
    staffing_query = """
    SELECT 
        sh.shift_date as date,
        a.department,
        COUNT(DISTINCT s.agent_id) as scheduled_agents,
        COUNT(DISTINCT CASE WHEN s.status IN ('COMPLETED', 'LATE') THEN s.agent_id END) as actual_agents,
        SUM(sh.required_agents) / COUNT(DISTINCT sh.id) as required_agents,
        SUM(CASE 
            WHEN s.check_out_time IS NOT NULL AND s.check_in_time IS NOT NULL THEN
                (julianday(s.check_out_time) - julianday(s.check_in_time)) * 24
            ELSE 8
        END) as total_hours,
        SUM(s.overtime_minutes) / 60.0 as overtime_hours
    FROM shifts sh
    LEFT JOIN schedules s ON sh.id = s.shift_id
    LEFT JOIN agents a ON s.agent_id = a.id
    GROUP BY sh.shift_date, a.department
    """
    
    staffing_data = []
    for row in norm_conn.execute(staffing_query):
        variance = (row['actual_agents'] or 0) - (row['required_agents'] or 0)
        understaffed = max(0, -variance) * 8  # Hours understaffed
        utilization = (row['actual_agents'] or 0) / (row['required_agents'] or 1) * 100
        
        staffing_data.append((
            row['date'],
            row['department'] or 'UNKNOWN',
            row['scheduled_agents'] or 0,
            row['actual_agents'] or 0,
            int(row['required_agents'] or 0),
            variance,
            row['total_hours'] or 0,
            row['overtime_hours'] or 0,
            understaffed,
            utilization
        ))
    
    denorm_conn.executemany("""
        INSERT INTO daily_staffing_metrics VALUES 
        (?,?,?,?,?,?,?,?,?,?)
    """, staffing_data)
    
    print("Building shift coverage analysis...")
    coverage_query = """
    SELECT 
        sh.shift_date,
        sh.shift_type,
        sh.required_agents,
        COUNT(DISTINCT s.agent_id) as scheduled_agents,
        COUNT(DISTINCT CASE WHEN s.status = 'CONFIRMED' THEN s.agent_id END) as confirmed_agents,
        AVG(julianday('now') - julianday(a.hire_date)) as avg_experience_days
    FROM shifts sh
    LEFT JOIN schedules s ON sh.id = s.shift_id
    LEFT JOIN agents a ON s.agent_id = a.id
    GROUP BY sh.shift_date, sh.shift_type
    """
    
    coverage_data = []
    for row in norm_conn.execute(coverage_query):
        coverage_pct = (row['scheduled_agents'] or 0) / (row['required_agents'] or 1) * 100
        skill_score = 80 + (row['avg_experience_days'] or 0) / 100  # Simplified
        
        coverage_data.append((
            row['shift_date'],
            row['shift_type'],
            row['required_agents'],
            row['scheduled_agents'] or 0,
            row['confirmed_agents'] or 0,
            coverage_pct,
            min(100, skill_score),
            int(row['avg_experience_days'] or 0)
        ))
    
    denorm_conn.executemany("""
        INSERT INTO shift_coverage_analysis VALUES 
        (?,?,?,?,?,?,?,?)
    """, coverage_data)
    
    print("Building skill demand forecast...")
    forecast_query = """
    SELECT 
        s.name as skill_name,
        strftime('%Y-%W', 'now') as week_start,
        COUNT(DISTINCT ask.agent_id) as current_certified,
        COUNT(DISTINCT CASE 
            WHEN ask.expiry_date < DATE('now', '+30 days') THEN ask.agent_id 
        END) as expiring_soon
    FROM skills s
    LEFT JOIN agent_skills ask ON s.id = ask.skill_id
    WHERE s.requires_certification = 1
    GROUP BY s.name
    """
    
    forecast_data = []
    for row in norm_conn.execute(forecast_query):
        # Simplified demand projection
        projected_demand = (row['current_certified'] or 0) + 5
        gap = projected_demand - (row['current_certified'] or 0) + (row['expiring_soon'] or 0)
        priority = min(100, gap * 10)
        
        forecast_data.append((
            row['skill_name'],
            row['week_start'],
            row['current_certified'] or 0,
            row['expiring_soon'] or 0,
            projected_demand,
            gap,
            priority
        ))
    
    denorm_conn.executemany("""
        INSERT INTO skill_demand_forecast VALUES 
        (?,?,?,?,?,?,?)
    """, forecast_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_performance_department ON agent_performance_summary(department)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_staffing_date ON daily_staffing_metrics(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_coverage_date ON shift_coverage_analysis(shift_date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_skill_forecast_week ON skill_demand_forecast(week_start)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()