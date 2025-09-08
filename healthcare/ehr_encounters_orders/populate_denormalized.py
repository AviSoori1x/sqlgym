#!/usr/bin/env python3
"""Populate EHR encounters and orders denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime
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
    
    print("Building encounter summary...")
    encounter_query = """
    SELECT
        e.id as encounter_id,
        p.first_name || ' ' || p.last_name as patient_name,
        pr.first_name || ' ' || pr.last_name as provider_name,
        pr.specialty as provider_specialty,
        e.encounter_date,
        e.encounter_type,
        e.chief_complaint,
        COUNT(co.id) as total_orders,
        COUNT(CASE WHEN co.status = 'COMPLETED' THEN co.id END) as completed_orders,
        COUNT(CASE WHEN co.status IN ('ORDERED', 'SCHEDULED', 'IN_PROGRESS') THEN co.id END) as pending_orders,
        COUNT(CASE WHEN co.status = 'CANCELLED' THEN co.id END) as cancelled_orders,
        AVG(CASE 
            WHEN co.completed_datetime IS NOT NULL AND co.order_datetime IS NOT NULL 
            THEN (julianday(co.completed_datetime) - julianday(co.order_datetime)) * 24 
        END) as avg_turnaround_hours,
        CASE 
            WHEN e.discharge_date IS NOT NULL AND e.admission_date IS NOT NULL 
            THEN (julianday(e.discharge_date) - julianday(e.admission_date)) * 24
            ELSE 2  -- Default outpatient encounter duration
        END as length_of_stay_hours,
        e.status as encounter_status
    FROM encounters e
    JOIN patients p ON e.patient_id = p.id
    JOIN providers pr ON e.provider_id = pr.id
    LEFT JOIN clinical_orders co ON e.id = co.encounter_id
    GROUP BY e.id
    """
    
    encounter_summary_data = []
    for row in norm_conn.execute(encounter_query):
        encounter_summary_data.append(tuple(row))
    
    denorm_conn.executemany("""
        INSERT INTO encounter_summary VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, encounter_summary_data)
    
    print("Building provider productivity...")
    productivity_query = """
    SELECT
        pr.id as provider_id,
        DATE(e.encounter_date) as date,
        COUNT(DISTINCT e.id) as encounters_count,
        COUNT(co.id) as total_orders,
        COUNT(CASE WHEN co.status = 'COMPLETED' THEN co.id END) as completed_orders,
        AVG(CASE 
            WHEN co.completed_datetime IS NOT NULL AND co.order_datetime IS NOT NULL 
            THEN (julianday(co.completed_datetime) - julianday(co.order_datetime)) * 24 
        END) as avg_turnaround_hours,
        COUNT(CASE WHEN co.priority = 'STAT' THEN co.id END) as stat_orders
    FROM providers pr
    LEFT JOIN encounters e ON pr.id = e.provider_id
    LEFT JOIN clinical_orders co ON e.id = co.encounter_id
    WHERE e.encounter_date IS NOT NULL
    GROUP BY pr.id, DATE(e.encounter_date)
    """
    
    productivity_data = []
    for row in norm_conn.execute(productivity_query):
        stat_completion_rate = 0.95 + rng.uniform(-0.1, 0.05)  # High stat completion rate
        patient_satisfaction = rng.uniform(3.5, 5.0)
        
        productivity_data.append(tuple(row) + (stat_completion_rate, patient_satisfaction))
    
    denorm_conn.executemany("""
        INSERT INTO provider_productivity VALUES 
        (?,?,?,?,?,?,?,?,?)
    """, productivity_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_encounter_summary_date ON encounter_summary(encounter_date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_provider_productivity_date ON provider_productivity(date)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()