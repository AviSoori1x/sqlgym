#!/usr/bin/env python3
"""Populate HSE incidents normalized schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

# Scale constants
EMPLOYEES = 2000
INCIDENTS = 5000

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert employees
    print(f"Inserting {EMPLOYEES} employees...")
    employees_data = []
    departments = ['Production', 'Maintenance', 'Quality', 'Safety', 'Engineering']
    
    for i in range(1, EMPLOYEES + 1):
        hire_date = (datetime.now() - timedelta(days=rng.randint(30, 3650))).strftime('%Y-%m-%d')
        safety_training = (datetime.strptime(hire_date, '%Y-%m-%d') + timedelta(days=rng.randint(1, 90))).strftime('%Y-%m-%d')
        
        employees_data.append((
            i, f'EMP{i:05d}', f'Employee{i}', f'LastName{i}',
            rng.choice(departments), f'Job Title {i}', hire_date, safety_training, 'ACTIVE'
        ))
    
    conn.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?,?)", employees_data)
    
    # Insert incident types
    incident_types_data = [
        (1, 'SLIP_FALL', 'Slip and Fall', 'MINOR', 1),
        (2, 'CUT_LACERATION', 'Cut/Laceration', 'MODERATE', 1),
        (3, 'CHEMICAL_EXPOSURE', 'Chemical Exposure', 'MAJOR', 1),
        (4, 'FIRE_EXPLOSION', 'Fire/Explosion', 'CATASTROPHIC', 1),
        (5, 'EQUIPMENT_FAILURE', 'Equipment Failure', 'MODERATE', 0)
    ]
    conn.executemany("INSERT INTO incident_types VALUES (?,?,?,?,?)", incident_types_data)
    
    # Insert HSE incidents
    print(f"Inserting {INCIDENTS} HSE incidents...")
    incidents_data = []
    
    for i in range(1, INCIDENTS + 1):
        incident_date = (datetime.now() - timedelta(days=rng.randint(1, 730))).strftime('%Y-%m-%d')
        incident_time = f'{rng.randint(6, 18):02d}:{rng.randint(0, 59):02d}:00'
        
        type_id = rng.randint(1, len(incident_types_data))
        severity = rng.choice(['MINOR', 'MODERATE', 'MAJOR', 'CATASTROPHIC'])
        
        injured_employee = rng.randint(1, EMPLOYEES) if rng.random() < 0.7 else None
        reported_by = rng.randint(1, EMPLOYEES)
        
        incidents_data.append((
            i, f'INC{i:06d}', incident_date, incident_time, f'Location {rng.randint(1, 50)}',
            type_id, severity, f'Incident description {i}', f'Immediate cause {i}',
            f'Root cause analysis {i}', injured_employee, reported_by, 'CLOSED'
        ))
    
    conn.executemany("INSERT INTO hse_incidents VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", incidents_data)
    
    # Create evidence table
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hse_incidents_date ON hse_incidents(incident_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hse_incidents_severity ON hse_incidents(severity)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()