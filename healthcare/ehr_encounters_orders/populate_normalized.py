#!/usr/bin/env python3
"""Populate EHR encounters and orders normalized schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

# Scale constants
PATIENTS = 8000
PROVIDERS = 300
ENCOUNTERS_PER_PATIENT = 4
ORDERS_PER_ENCOUNTER = 6

# Medical specialties and departments
SPECIALTIES = [
    'Internal Medicine', 'Family Medicine', 'Emergency Medicine', 'Cardiology',
    'Orthopedics', 'Neurology', 'Psychiatry', 'Radiology', 'Pathology', 
    'Anesthesiology', 'Surgery', 'Pediatrics', 'Obstetrics', 'Dermatology'
]

DEPARTMENTS = [
    'Emergency Department', 'Internal Medicine', 'Surgery', 'Cardiology',
    'Orthopedics', 'Radiology', 'Laboratory', 'Pharmacy', 'ICU', 'Medical Floor'
]

# Order types by category
ORDER_TYPES = [
    ('LAB_CBC', 'Complete Blood Count', 'LABORATORY', False, 4),
    ('LAB_BMP', 'Basic Metabolic Panel', 'LABORATORY', False, 6),
    ('RAD_CHEST', 'Chest X-Ray', 'RADIOLOGY', True, 2),
    ('RAD_CT_HEAD', 'CT Head', 'RADIOLOGY', True, 1),
    ('MED_ASPIRIN', 'Aspirin 81mg', 'MEDICATION', False, 1),
    ('MED_LIPITOR', 'Atorvastatin 20mg', 'MEDICATION', False, 1),
    ('PROC_EKG', 'Electrocardiogram', 'PROCEDURE', False, 1),
    ('CONSULT_CARDIO', 'Cardiology Consultation', 'CONSULT', True, 24),
    ('THERAPY_PT', 'Physical Therapy', 'THERAPY', True, 48)
]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert patients
    print(f"Inserting {PATIENTS} patients...")
    patients_data = []
    
    for i in range(1, PATIENTS + 1):
        birth_date = (datetime.now() - timedelta(days=rng.randint(1*365, 90*365))).strftime('%Y-%m-%d')
        gender = rng.choice(['M', 'F', 'OTHER'])
        status = rng.choices(['ACTIVE', 'INACTIVE'], weights=[0.95, 0.05])[0]
        
        patients_data.append((
            i, f'PAT{i:07d}', f'FirstName{i}', f'LastName{i}',
            birth_date, gender, f'{i} Patient Street, Medical City',
            f'555-{i:04d}', f'patient{i}@email.com',
            f'Emergency Contact {i}', f'INS{i:06d}', status
        ))
    
    for chunk in batch(patients_data, 1000):
        conn.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert providers
    print(f"Inserting {PROVIDERS} providers...")
    providers_data = []
    
    for i in range(1, PROVIDERS + 1):
        specialty = rng.choice(SPECIALTIES)
        department = rng.choice(DEPARTMENTS)
        npi = f'{1000000000 + i}'
        license_num = f'LIC{i:06d}'
        status = rng.choices(['ACTIVE', 'INACTIVE'], weights=[0.95, 0.05])[0]
        
        providers_data.append((
            i, f'PROV{i:05d}', f'Dr. FirstName{i}', f'LastName{i}',
            specialty, department, npi, license_num, status
        ))
    
    for chunk in batch(providers_data, 1000):
        conn.executemany("INSERT INTO providers VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert order types
    print("Inserting order types...")
    order_types_data = []
    for i, (code, name, category, auth_required, turnaround) in enumerate(ORDER_TYPES, 1):
        order_types_data.append((i, code, name, category, auth_required, turnaround, 1))
    
    conn.executemany("INSERT INTO order_types VALUES (?,?,?,?,?,?,?)", order_types_data)
    
    # Insert encounters
    print("Inserting encounters...")
    encounters_data = []
    encounter_id = 1
    
    for patient in patients_data:
        if patient[11] != 'ACTIVE':  # Skip inactive patients
            continue
            
        patient_id = patient[0]
        num_encounters = rng.randint(1, ENCOUNTERS_PER_PATIENT)
        
        for _ in range(num_encounters):
            provider_id = rng.randint(1, PROVIDERS)
            encounter_date = (datetime.now() - timedelta(days=rng.randint(1, 365))).strftime('%Y-%m-%d %H:%M:%S')
            
            encounter_type = rng.choices(['OUTPATIENT', 'INPATIENT', 'EMERGENCY'], 
                                       weights=[0.7, 0.2, 0.1])[0]
            
            # Admission/discharge for inpatient
            if encounter_type == 'INPATIENT':
                admission_date = encounter_date
                discharge_date = (datetime.strptime(encounter_date, '%Y-%m-%d %H:%M:%S') + 
                                timedelta(days=rng.randint(1, 7))).strftime('%Y-%m-%d %H:%M:%S')
            else:
                admission_date = None
                discharge_date = None
            
            chief_complaint = rng.choice([
                'Chest pain', 'Shortness of breath', 'Abdominal pain', 'Headache',
                'Back pain', 'Fever', 'Fatigue', 'Nausea', 'Dizziness'
            ])
            
            diagnosis_codes = rng.sample([
                'I10', 'E11.9', 'M79.3', 'R06.02', 'K21.9', 'J44.1', 'F32.9'
            ], rng.randint(1, 3))
            
            status = rng.choices(['COMPLETED', 'IN_PROGRESS', 'CANCELLED'], 
                               weights=[0.8, 0.15, 0.05])[0]
            
            encounters_data.append((
                encounter_id, f'ENC{encounter_id:08d}', patient_id, provider_id,
                encounter_date, encounter_type, admission_date, discharge_date,
                chief_complaint, json.dumps(diagnosis_codes), status
            ))
            encounter_id += 1
    
    for chunk in batch(encounters_data, 1000):
        conn.executemany("INSERT INTO encounters VALUES (?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert clinical orders and results
    print("Inserting clinical orders...")
    orders_data = []
    results_data = []
    tracking_data = []
    
    order_id = 1
    result_id = 1
    tracking_id = 1
    
    for encounter in encounters_data:
        if encounter[10] != 'COMPLETED':  # Only generate orders for completed encounters
            continue
            
        encounter_id = encounter[0]
        provider_id = encounter[3]
        encounter_datetime = datetime.strptime(encounter[4], '%Y-%m-%d %H:%M:%S')
        
        num_orders = rng.randint(2, ORDERS_PER_ENCOUNTER)
        
        for _ in range(num_orders):
            order_type_id = rng.randint(1, len(ORDER_TYPES))
            order_type = ORDER_TYPES[order_type_id - 1]
            
            order_datetime = encounter_datetime + timedelta(minutes=rng.randint(5, 120))
            priority = rng.choices(['ROUTINE', 'URGENT', 'STAT'], weights=[0.7, 0.2, 0.1])[0]
            
            # Order details based on type
            order_details = {
                'order_type': order_type[1],
                'priority': priority,
                'special_instructions': f'Standard {order_type[2].lower()} order'
            }
            
            # Order status workflow
            if priority == 'STAT':
                status = 'COMPLETED'
                scheduled_datetime = order_datetime + timedelta(minutes=15)
                completed_datetime = scheduled_datetime + timedelta(hours=order_type[4])
            else:
                status = rng.choices(['COMPLETED', 'IN_PROGRESS', 'SCHEDULED'], 
                                   weights=[0.7, 0.2, 0.1])[0]
                
                if status == 'COMPLETED':
                    scheduled_datetime = order_datetime + timedelta(hours=rng.randint(1, 24))
                    completed_datetime = scheduled_datetime + timedelta(hours=order_type[4])
                elif status == 'IN_PROGRESS':
                    scheduled_datetime = order_datetime + timedelta(hours=rng.randint(1, 12))
                    completed_datetime = None
                else:
                    scheduled_datetime = order_datetime + timedelta(hours=rng.randint(12, 48))
                    completed_datetime = None
            
            orders_data.append((
                order_id, f'ORD{order_id:09d}', encounter_id, provider_id,
                order_type_id, order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                priority, json.dumps(order_details), status,
                scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S') if scheduled_datetime else None,
                completed_datetime.strftime('%Y-%m-%d %H:%M:%S') if completed_datetime else None,
                f'{priority} {order_type[1]} order'
            ))
            
            # Create results for completed orders
            if status == 'COMPLETED' and completed_datetime:
                result_datetime = completed_datetime + timedelta(minutes=rng.randint(5, 60))
                result_type = rng.choices(['PRELIMINARY', 'FINAL'], weights=[0.3, 0.7])[0]
                
                if order_type[2] == 'LABORATORY':
                    result_status = rng.choices(['NORMAL', 'ABNORMAL', 'CRITICAL'], weights=[0.7, 0.25, 0.05])[0]
                    result_value = f'{rng.uniform(1.0, 10.0):.2f}'
                    result_units = 'mg/dL'
                    reference_range = '1.0-5.0'
                else:
                    result_status = rng.choices(['NORMAL', 'ABNORMAL'], weights=[0.8, 0.2])[0]
                    result_value = 'See report'
                    result_units = None
                    reference_range = None
                
                interpreting_provider = rng.randint(1, PROVIDERS)
                
                results_data.append((
                    result_id, order_id, result_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    result_type, result_status, result_value, result_units,
                    reference_range, interpreting_provider, f'Result for {order_type[1]}'
                ))
                result_id += 1
            
            # Create tracking entry
            tracking_data.append((
                tracking_id, order_id, order_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                None, 'ORDERED', provider_id, 'Initial order placement', 'Order placed'
            ))
            tracking_id += 1
            
            order_id += 1
    
    # Batch insert all data
    for chunk in batch(orders_data, 1000):
        conn.executemany("INSERT INTO clinical_orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(results_data, 1000):
        conn.executemany("INSERT INTO order_results VALUES (?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(tracking_data, 1000):
        conn.executemany("INSERT INTO order_tracking VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_kv (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    conn.commit()
    
    # Create indexes after bulk loading
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_encounters_patient ON encounters(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_encounters_date ON encounters(encounter_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_clinical_orders_encounter ON clinical_orders(encounter_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_clinical_orders_datetime ON clinical_orders(order_datetime)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_order_results_order ON order_results(order_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()