#!/usr/bin/env python3
"""Populate field service dispatch denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
import json
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
    
    print("Building daily technician schedules...")
    schedule_query = """
    SELECT 
        t.id as technician_id,
        t.name as technician_name,
        a.scheduled_date as schedule_date,
        COUNT(a.id) as total_appointments,
        SUM(a.travel_distance_km) as total_travel_km,
        SUM(CASE 
            WHEN a.actual_end_time IS NOT NULL AND a.actual_start_time IS NOT NULL THEN
                (CAST(substr(a.actual_end_time, 1, 2) AS REAL) + CAST(substr(a.actual_end_time, 4, 2) AS REAL)/60) -
                (CAST(substr(a.actual_start_time, 1, 2) AS REAL) + CAST(substr(a.actual_start_time, 4, 2) AS REAL)/60)
            ELSE
                (CAST(substr(a.scheduled_end_time, 1, 2) AS REAL) + CAST(substr(a.scheduled_end_time, 4, 2) AS REAL)/60) -
                (CAST(substr(a.scheduled_start_time, 1, 2) AS REAL) + CAST(substr(a.scheduled_start_time, 4, 2) AS REAL)/60)
        END) as total_service_hours,
        MIN(a.scheduled_start_time) as first_appointment_time,
        MAX(a.scheduled_end_time) as last_appointment_time,
        GROUP_CONCAT(DISTINCT sr.request_type) as service_types,
        COUNT(CASE WHEN a.status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*) as completion_rate,
        t.max_daily_jobs
    FROM technicians t
    JOIN appointments a ON t.id = a.technician_id
    JOIN service_requests sr ON a.service_request_id = sr.id
    GROUP BY t.id, a.scheduled_date
    """
    
    schedule_data = []
    for row in norm_conn.execute(schedule_query):
        utilization = min(100, (row['total_appointments'] / row['max_daily_jobs']) * 100)
        avg_travel = row['total_travel_km'] / row['total_appointments'] if row['total_appointments'] > 1 else 0
        
        schedule_data.append((
            row['technician_id'],
            row['technician_name'],
            row['schedule_date'],
            row['total_appointments'],
            row['total_travel_km'],
            row['total_service_hours'],
            utilization,
            row['first_appointment_time'],
            row['last_appointment_time'],
            json.dumps(row['service_types'].split(',')),
            row['completion_rate'],
            avg_travel
        ))
    
    for chunk in batch(schedule_data, 500):
        denorm_conn.executemany("""
            INSERT INTO daily_technician_schedule VALUES 
            (?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building service metrics...")
    metrics_query = """
    SELECT 
        DATE(sr.created_at) as date,
        sr.request_type,
        COUNT(*) as total_requests,
        COUNT(CASE WHEN sr.status = 'SCHEDULED' THEN 1 END) as scheduled_count,
        COUNT(CASE WHEN a.status = 'COMPLETED' THEN 1 END) as completed_count,
        COUNT(CASE WHEN sr.status = 'CANCELLED' THEN 1 END) as cancelled_count,
        AVG(CASE 
            WHEN a.scheduled_date IS NOT NULL THEN
                (julianday(a.scheduled_date) - julianday(sr.created_at)) * 24
        END) as avg_wait_time_hours,
        AVG(CASE 
            WHEN a.actual_end_time IS NOT NULL AND a.actual_start_time IS NOT NULL THEN
                (CAST(substr(a.actual_end_time, 1, 2) AS REAL) - CAST(substr(a.actual_start_time, 1, 2) AS REAL))
        END) as avg_completion_time_hours,
        COUNT(CASE WHEN a.actual_start_time <= a.scheduled_start_time THEN 1 END) * 100.0 / 
            NULLIF(COUNT(a.id), 0) as on_time_rate
    FROM service_requests sr
    LEFT JOIN appointments a ON sr.id = a.service_request_id
    GROUP BY DATE(sr.created_at), sr.request_type
    """
    
    metrics_data = []
    for row in norm_conn.execute(metrics_query):
        # Simulate first-time fix rate
        ftf_rate = 85 if row['request_type'] in ['MAINTENANCE', 'INSPECTION'] else 70
        
        metrics_data.append((
            row['date'],
            row['request_type'],
            row['total_requests'],
            row['scheduled_count'],
            row['completed_count'],
            row['cancelled_count'],
            row['avg_wait_time_hours'],
            row['avg_completion_time_hours'],
            row['on_time_rate'] or 0,
            ftf_rate
        ))
    
    denorm_conn.executemany("""
        INSERT INTO service_metrics VALUES 
        (?,?,?,?,?,?,?,?,?,?)
    """, metrics_data)
    
    print("Building geographic demand...")
    geo_query = """
    SELECT 
        ROUND(c.latitude, 1) as grid_latitude,
        ROUND(c.longitude, 1) as grid_longitude,
        strftime('%Y-%m-%d', sr.created_at, 'weekday 0', '-6 days') as week_start,
        COUNT(*) as total_requests,
        COUNT(CASE WHEN sr.priority = 'EMERGENCY' THEN 1 END) as emergency_requests,
        AVG(CASE 
            WHEN a.scheduled_date IS NOT NULL THEN
                (julianday(a.scheduled_date) - julianday(sr.created_at)) * 24
        END) as avg_response_time_hours
    FROM service_requests sr
    JOIN customers c ON sr.customer_id = c.id
    LEFT JOIN appointments a ON sr.id = a.service_request_id
    GROUP BY ROUND(c.latitude, 1), ROUND(c.longitude, 1), 
             strftime('%Y-%m-%d', sr.created_at, 'weekday 0', '-6 days')
    """
    
    geo_data = []
    for row in norm_conn.execute(geo_query):
        # Calculate underserved score based on response time
        underserved = min(10, int((row['avg_response_time_hours'] or 24) / 24 * 5))
        
        geo_data.append((
            row['grid_latitude'],
            row['grid_longitude'],
            row['week_start'],
            row['total_requests'],
            row['emergency_requests'],
            row['avg_response_time_hours'],
            15.0,  # Simulated average distance
            underserved
        ))
    
    denorm_conn.executemany("""
        INSERT INTO geographic_demand VALUES 
        (?,?,?,?,?,?,?,?)
    """, geo_data)
    
    print("Building technician performance...")
    perf_query = """
    SELECT 
        t.id as technician_id,
        strftime('%Y-%m', a.scheduled_date) as month,
        COUNT(CASE WHEN a.status = 'COMPLETED' THEN 1 END) as jobs_completed,
        COUNT(a.id) as jobs_assigned,
        SUM(a.travel_distance_km) as total_distance,
        AVG(CASE 
            WHEN a.actual_end_time IS NOT NULL AND a.actual_start_time IS NOT NULL THEN
                (CAST(substr(a.actual_end_time, 1, 2) AS REAL) - CAST(substr(a.actual_start_time, 1, 2) AS REAL))
        END) as avg_job_duration,
        COUNT(CASE WHEN a.actual_start_time <= a.scheduled_start_time THEN 1 END) * 100.0 / 
            NULLIF(COUNT(a.id), 0) as on_time_rate,
        GROUP_CONCAT(sr.request_type) as job_types
    FROM technicians t
    LEFT JOIN appointments a ON t.id = a.technician_id
    LEFT JOIN service_requests sr ON a.service_request_id = sr.id
    WHERE a.id IS NOT NULL
    GROUP BY t.id, strftime('%Y-%m', a.scheduled_date)
    """
    
    perf_data = []
    for row in norm_conn.execute(perf_query):
        completion_rate = (row['jobs_completed'] / row['jobs_assigned']) * 100 if row['jobs_assigned'] > 0 else 0
        
        # Count skills used
        skills_used = {}
        if row['job_types']:
            for job_type in row['job_types'].split(','):
                skills_used[job_type] = skills_used.get(job_type, 0) + 1
        
        # Simulate revenue
        revenue = row['jobs_completed'] * 150
        
        perf_data.append((
            row['technician_id'],
            row['month'],
            row['jobs_completed'],
            row['jobs_assigned'],
            completion_rate,
            row['avg_job_duration'],
            row['total_distance'],
            4.5,  # Simulated rating
            row['on_time_rate'] or 0,
            json.dumps(skills_used),
            revenue
        ))
    
    for chunk in batch(perf_data, 500):
        denorm_conn.executemany("""
            INSERT INTO technician_performance VALUES 
            (?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_schedule_date ON daily_technician_schedule(schedule_date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_service_metrics_date ON service_metrics(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_geographic_week ON geographic_demand(week_start)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_tech_performance_month ON technician_performance(month)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()