#!/usr/bin/env python3
"""Populate lab information system normalized schema with synthetic data."""
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
PATIENTS = 7000
LAB_ORDERS = 80000
LAB_RESULTS = 150000

# Lab test definitions
LAB_TESTS = [
    ('CBC', 'Complete Blood Count', 'HEMATOLOGY', 'BLOOD', 4, '4.5-11.0 x10³/µL', 2.0, 20.0),
    ('BMP', 'Basic Metabolic Panel', 'CHEMISTRY', 'BLOOD', 6, '136-145 mmol/L', 120, 160),
    ('LIPID', 'Lipid Panel', 'CHEMISTRY', 'BLOOD', 12, '<200 mg/dL', 50, 400),
    ('TSH', 'Thyroid Stimulating Hormone', 'IMMUNOLOGY', 'BLOOD', 24, '0.4-4.0 mU/L', 0.1, 20.0),
    ('GLUCOSE', 'Glucose Random', 'CHEMISTRY', 'BLOOD', 2, '70-99 mg/dL', 40, 400),
    ('URINE', 'Urinalysis', 'CHEMISTRY', 'URINE', 2, 'Normal', None, None),
    ('CULTURE', 'Blood Culture', 'MICROBIOLOGY', 'BLOOD', 72, 'No Growth', None, None),
    ('COVID', 'COVID-19 PCR', 'MOLECULAR', 'SWAB', 24, 'Negative', None, None)
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
        
        patients_data.append((
            i, f'PAT{i:07d}', f'Patient{i}', f'LastName{i}',
            birth_date, rng.choice(['M', 'F', 'OTHER']),
            f'MRN{i:08d}', 'ACTIVE'
        ))
    
    for chunk in batch(patients_data, 1000):
        conn.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    # Insert lab tests
    print("Inserting lab tests...")
    lab_tests_data = []
    for i, (code, name, category, specimen, turnaround, ref_range, crit_low, crit_high) in enumerate(LAB_TESTS, 1):
        lab_tests_data.append((i, code, name, category, specimen, turnaround, ref_range, crit_low, crit_high, 1))
    
    conn.executemany("INSERT INTO lab_tests VALUES (?,?,?,?,?,?,?,?,?,?)", lab_tests_data)
    
    # Insert lab orders
    print(f"Inserting {LAB_ORDERS} lab orders...")
    orders_data = []
    specimens_data = []
    results_data = []
    qc_data = []
    
    order_id = 1
    specimen_id = 1
    result_id = 1
    qc_id = 1
    
    for _ in range(LAB_ORDERS):
        patient_id = rng.randint(1, PATIENTS)
        test_id = rng.randint(1, len(LAB_TESTS))
        test_info = LAB_TESTS[test_id - 1]
        
        order_datetime = (datetime.now() - timedelta(days=rng.randint(1, 180))).strftime('%Y-%m-%d %H:%M:%S')
        priority = rng.choices(['ROUTINE', 'URGENT', 'STAT'], weights=[0.7, 0.2, 0.1])[0]
        status = rng.choices(['COMPLETED', 'IN_PROGRESS', 'CANCELLED'], weights=[0.85, 0.10, 0.05])[0]
        
        orders_data.append((
            order_id, f'ORD{order_id:09d}', patient_id, f'Dr. Provider {rng.randint(1, 100)}',
            test_id, order_datetime, priority, f'Clinical indication {order_id}', status
        ))
        
        # Create specimen if order is processed
        if status != 'CANCELLED':
            collection_datetime = (datetime.strptime(order_datetime, '%Y-%m-%d %H:%M:%S') + 
                                 timedelta(minutes=rng.randint(30, 240))).strftime('%Y-%m-%d %H:%M:%S')
            
            specimen_condition = rng.choices(['ACCEPTABLE', 'HEMOLYZED', 'CLOTTED'], weights=[0.9, 0.05, 0.05])[0]
            processing_status = 'COMPLETED' if status == 'COMPLETED' else 'PROCESSING'
            
            specimens_data.append((
                specimen_id, f'SPEC{specimen_id:09d}', order_id, collection_datetime,
                'Venipuncture', f'Tech{rng.randint(1, 20)}', rng.uniform(1.0, 10.0),
                specimen_condition, collection_datetime, processing_status
            ))
            
            # Create results for completed specimens
            if status == 'COMPLETED' and specimen_condition == 'ACCEPTABLE':
                result_datetime = (datetime.strptime(collection_datetime, '%Y-%m-%d %H:%M:%S') + 
                                 timedelta(hours=test_info[4])).strftime('%Y-%m-%d %H:%M:%S')
                
                # Generate realistic lab values
                if test_info[6] and test_info[7]:  # Has critical values
                    if rng.random() < 0.05:  # 5% critical results
                        if rng.random() < 0.5:
                            result_value = rng.uniform(0, test_info[6])  # Critical low
                            abnormal_flag = 'CRITICAL_LOW'
                        else:
                            result_value = rng.uniform(test_info[7], test_info[7] * 1.5)  # Critical high
                            abnormal_flag = 'CRITICAL_HIGH'
                    else:
                        result_value = rng.uniform(test_info[6], test_info[7])
                        abnormal_flag = rng.choices(['NORMAL', 'HIGH', 'LOW'], weights=[0.8, 0.1, 0.1])[0]
                    
                    result_str = f'{result_value:.2f}'
                    units = test_info[5].split()[-1] if ' ' in test_info[5] else 'units'
                else:
                    result_str = rng.choice(['Negative', 'Positive', 'Normal', 'Abnormal'])
                    abnormal_flag = 'NORMAL' if result_str in ['Negative', 'Normal'] else 'ABNORMAL'
                    units = None
                
                results_data.append((
                    result_id, specimen_id, test_id, result_datetime, result_str, units,
                    abnormal_flag, f'Tech{rng.randint(1, 30)}', 
                    f'Path{rng.randint(1, 10)}' if abnormal_flag.startswith('CRITICAL') else None,
                    'FINAL'
                ))
                result_id += 1
            
            specimen_id += 1
        
        order_id += 1
    
    # Batch insert all data
    for chunk in batch(orders_data, 1000):
        conn.executemany("INSERT INTO lab_orders VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(specimens_data, 1000):
        conn.executemany("INSERT INTO specimens VALUES (?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(results_data, 1000):
        conn.executemany("INSERT INTO lab_results VALUES (?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert quality controls
    print("Inserting quality controls...")
    for test_id in range(1, len(LAB_TESTS) + 1):
        for day in range(30):  # 30 days of QC
            qc_date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d %H:%M:%S')
            expected_value = rng.uniform(50, 150)
            actual_value = expected_value * rng.uniform(0.95, 1.05)
            variance = abs((actual_value - expected_value) / expected_value * 100)
            
            qc_status = 'PASSED' if variance < 5 else 'OUT_OF_RANGE'
            
            qc_data.append((
                qc_id, f'QC{qc_id:06d}', test_id, qc_date,
                expected_value, actual_value, variance, qc_status,
                f'Tech{rng.randint(1, 10)}'
            ))
            qc_id += 1
    
    for chunk in batch(qc_data, 1000):
        conn.executemany("INSERT INTO quality_controls VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_patients_mrn ON patients(medical_record_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lab_orders_patient ON lab_orders(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lab_orders_datetime ON lab_orders(order_datetime)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_specimens_order ON specimens(order_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lab_results_specimen ON lab_results(specimen_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()