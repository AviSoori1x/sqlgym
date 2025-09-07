#!/usr/bin/env python3
"""Populate field service dispatch normalized schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random
import json
import math
from pathlib import Path
from datetime import datetime, timedelta, time
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

# Scale constants
CUSTOMERS = 3000
TECHNICIANS = 150
SERVICE_REQUESTS = 25000

# Geographic bounds
LAT_MIN, LAT_MAX = 37.0, 38.0
LON_MIN, LON_MAX = -122.5, -121.5

# Service types and skills
SERVICE_SKILLS = {
    'INSTALL': ['installation', 'electrical'],
    'REPAIR': ['diagnostics', 'repair'],
    'MAINTENANCE': ['maintenance', 'inspection'],
    'INSPECTION': ['inspection', 'testing'],
    'EMERGENCY': ['emergency', 'repair']
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert customers
    print(f"Inserting {CUSTOMERS} customers...")
    customers_data = []
    for i in range(1, CUSTOMERS + 1):
        lat = rng.uniform(LAT_MIN, LAT_MAX)
        lon = rng.uniform(LON_MIN, LON_MAX)
        level = rng.choices(['STANDARD', 'PRIORITY', 'VIP'], weights=[0.70, 0.25, 0.05])[0]
        customers_data.append((i, f'Customer_{i}', f'{rng.randint(100, 9999)} Street', lat, lon, level))
    
    for chunk in batch(customers_data, 1000):
        conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", chunk)
    
    # Insert technicians
    print(f"Inserting {TECHNICIANS} technicians...")
    technicians_data = []
    all_skills = ['installation', 'electrical', 'diagnostics', 'repair', 'maintenance', 'inspection', 'testing', 'emergency']
    
    for i in range(1, TECHNICIANS + 1):
        skills = rng.sample(all_skills, k=rng.randint(3, 6))
        cert = rng.choices(['APPRENTICE', 'JOURNEYMAN', 'MASTER'], weights=[0.40, 0.45, 0.15])[0]
        lat = rng.uniform(LAT_MIN, LAT_MAX)
        lon = rng.uniform(LON_MIN, LON_MAX)
        max_jobs = 10 if cert == 'MASTER' else 8
        status = rng.choices(['ACTIVE', 'ON_LEAVE'], weights=[0.95, 0.05])[0]
        
        technicians_data.append((i, f'Tech_{i}', f'tech{i}@field.com', json.dumps(skills), cert, lat, lon, max_jobs, status))
    
    conn.executemany("INSERT INTO technicians VALUES (?,?,?,?,?,?,?,?,?)", technicians_data)
    
    # Insert service requests
    print(f"Inserting {SERVICE_REQUESTS} service requests...")
    requests_data = []
    appointments_data = []
    events_data = []
    
    req_id = 1
    appt_id = 1
    event_id = 1
    base_date = datetime(2024, 1, 1)
    
    for _ in range(SERVICE_REQUESTS):
        customer_id = rng.randint(1, CUSTOMERS)
        req_type = rng.choice(list(SERVICE_SKILLS.keys()))
        priority = rng.choices(['LOW', 'MEDIUM', 'HIGH', 'EMERGENCY'], weights=[0.30, 0.45, 0.20, 0.05])[0]
        if req_type == 'EMERGENCY':
            priority = 'EMERGENCY'
        
        skills_req = SERVICE_SKILLS[req_type]
        duration = rng.uniform(0.5, 4)
        created = base_date + timedelta(days=rng.randint(0, 28), hours=rng.randint(7, 19))
        
        if priority == 'EMERGENCY':
            requested = created.date()
        else:
            requested = created.date() + timedelta(days=rng.randint(1, 7))
        
        window = rng.choices(['MORNING', 'AFTERNOON', 'EVENING', 'ANYTIME'], weights=[0.35, 0.35, 0.10, 0.20])[0]
        status = rng.choices(['SCHEDULED', 'PENDING', 'CANCELLED'], weights=[0.85, 0.10, 0.05])[0]
        
        requests_data.append((
            req_id, customer_id, req_type, priority, json.dumps(skills_req), duration,
            created.strftime('%Y-%m-%d %H:%M:%S'), requested.strftime('%Y-%m-%d'), window, status
        ))
        
        # Create appointment if scheduled
        if status == 'SCHEDULED':
            tech_id = rng.randint(1, TECHNICIANS)
            start_hour = rng.randint(8, 16)
            start_time = f"{start_hour:02d}:00:00"
            end_hour = start_hour + int(duration) + 1
            end_time = f"{end_hour:02d}:00:00"
            
            customer = customers_data[customer_id-1]
            tech = technicians_data[tech_id-1]
            distance = haversine_distance(customer[3], customer[4], tech[5], tech[6])
            
            appt_status = rng.choices(['COMPLETED', 'SCHEDULED', 'MISSED'], weights=[0.80, 0.15, 0.05])[0]
            actual_start = start_time if appt_status == 'COMPLETED' else None
            actual_end = end_time if appt_status == 'COMPLETED' else None
            
            appointments_data.append((
                appt_id, req_id, tech_id, requested.strftime('%Y-%m-%d'),
                start_time, end_time, actual_start, actual_end, distance, appt_status
            ))
            
            # Create events
            events_data.append((
                event_id, appt_id, 'ASSIGNED', created.strftime('%Y-%m-%d %H:%M:%S'),
                f'Assigned to Tech_{tech_id}', None, None
            ))
            event_id += 1
            
            if appt_status == 'COMPLETED':
                events_data.append((
                    event_id, appt_id, 'COMPLETED',
                    f"{requested} {end_time}", 'Job completed', customer[3], customer[4]
                ))
                event_id += 1
            
            appt_id += 1
        
        req_id += 1
    
    # Batch insert
    for chunk in batch(requests_data, 1000):
        conn.executemany("INSERT INTO service_requests VALUES (?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(appointments_data, 1000):
        conn.executemany("INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(events_data, 1000):
        conn.executemany("INSERT INTO dispatch_events VALUES (?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_kv (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_location ON customers(latitude, longitude)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_technicians_status ON technicians(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_service_requests_status ON service_requests(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_service_requests_date ON service_requests(requested_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(scheduled_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_technician ON appointments(technician_id, scheduled_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_dispatch_events_appointment ON dispatch_events(appointment_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
