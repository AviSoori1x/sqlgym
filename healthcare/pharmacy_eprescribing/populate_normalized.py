#!/usr/bin/env python3
"""Populate pharmacy eprescribing normalized schema with synthetic data."""
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
PATIENTS = 6000
PRESCRIBERS = 200
PHARMACIES = 150
MEDICATIONS = 500
PRESCRIPTIONS_PER_PATIENT = 8

# Common medications
MEDICATIONS_DATA = [
    ('00093015001', 'Lisinopril', 'Prinivil', '10mg', 'TABLET', 'ACE Inhibitor', None, 1),
    ('00093015002', 'Atorvastatin', 'Lipitor', '20mg', 'TABLET', 'Statin', None, 1),
    ('00093015003', 'Metformin', 'Glucophage', '500mg', 'TABLET', 'Antidiabetic', None, 1),
    ('00093015004', 'Amlodipine', 'Norvasc', '5mg', 'TABLET', 'Calcium Channel Blocker', None, 1),
    ('00093015005', 'Omeprazole', 'Prilosec', '20mg', 'CAPSULE', 'Proton Pump Inhibitor', None, 1),
    ('00093015006', 'Hydrocodone', 'Vicodin', '5mg/325mg', 'TABLET', 'Opioid Analgesic', 'CII', 0),
    ('00093015007', 'Alprazolam', 'Xanax', '0.25mg', 'TABLET', 'Benzodiazepine', 'CIV', 0),
    ('00093015008', 'Amoxicillin', 'Amoxil', '500mg', 'CAPSULE', 'Antibiotic', None, 1),
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
        birth_date = (datetime.now() - timedelta(days=rng.randint(18*365, 85*365))).strftime('%Y-%m-%d')
        allergies = rng.sample(['Penicillin', 'Sulfa', 'Aspirin', 'Latex'], rng.randint(0, 2))
        
        patients_data.append((
            i, f'PAT{i:07d}', f'Patient{i}', f'LastName{i}',
            birth_date, rng.choice(['M', 'F']), f'{i} Health Ave',
            f'555-{i:04d}', f'INS{i:06d}', json.dumps(allergies), 'ACTIVE'
        ))
    
    for chunk in batch(patients_data, 1000):
        conn.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert prescribers
    print(f"Inserting {PRESCRIBERS} prescribers...")
    prescribers_data = []
    specialties = ['Family Medicine', 'Internal Medicine', 'Cardiology', 'Endocrinology', 'Psychiatry']
    
    for i in range(1, PRESCRIBERS + 1):
        specialty = rng.choice(specialties)
        npi = f'{1000000000 + i}'
        dea = f'A{rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}{i:07d}'
        
        prescribers_data.append((
            i, f'PRES{i:05d}', f'Dr. First{i}', f'Last{i}',
            specialty, npi, dea, f'LIC{i:06d}',
            f'{i} Medical Plaza', 'ACTIVE'
        ))
    
    conn.executemany("INSERT INTO prescribers VALUES (?,?,?,?,?,?,?,?,?,?)", prescribers_data)
    
    # Insert pharmacies
    print(f"Inserting {PHARMACIES} pharmacies...")
    pharmacies_data = []
    states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI']
    
    for i in range(1, PHARMACIES + 1):
        chain = rng.choice(['CVS', 'Walgreens', 'Rite Aid', 'Independent', 'Hospital'])
        state = rng.choice(states)
        pharmacy_type = 'HOSPITAL' if chain == 'Hospital' else 'RETAIL'
        
        pharmacies_data.append((
            i, f'PHARM{i:05d}', f'Pharmacy {i}', chain,
            f'{i} Pharmacy Blvd', f'City{i}', state, f'{10000+i}',
            f'555-{i:04d}', f'NCPDP{i:06d}', pharmacy_type
        ))
    
    conn.executemany("INSERT INTO pharmacies VALUES (?,?,?,?,?,?,?,?,?,?,?)", pharmacies_data)
    
    # Insert medications
    print("Inserting medications...")
    medications_data = []
    for i, (ndc, generic, brand, strength, form, drug_class, schedule, is_generic) in enumerate(MEDICATIONS_DATA, 1):
        medications_data.append((i, ndc, generic, brand, strength, form, drug_class, schedule, is_generic))
    
    # Add more medications
    for i in range(len(MEDICATIONS_DATA) + 1, MEDICATIONS + 1):
        medications_data.append((
            i, f'00093{i:06d}', f'Generic Drug {i}', f'Brand {i}',
            f'{rng.randint(1, 100)}mg', rng.choice(['TABLET', 'CAPSULE', 'LIQUID']),
            'Miscellaneous', None, 1
        ))
    
    conn.executemany("INSERT INTO medications VALUES (?,?,?,?,?,?,?,?,?)", medications_data)
    
    # Insert prescriptions and fills
    print("Inserting prescriptions...")
    prescriptions_data = []
    fills_data = []
    interactions_data = []
    
    prescription_id = 1
    fill_id = 1
    interaction_id = 1
    
    for patient in patients_data:
        patient_id = patient[0]
        num_prescriptions = rng.randint(2, PRESCRIPTIONS_PER_PATIENT)
        
        for _ in range(num_prescriptions):
            prescriber_id = rng.randint(1, PRESCRIBERS)
            medication_id = rng.randint(1, len(medications_data))
            pharmacy_id = rng.randint(1, PHARMACIES)
            
            written_date = (datetime.now() - timedelta(days=rng.randint(1, 365))).strftime('%Y-%m-%d')
            quantity = rng.randint(30, 90)
            days_supply = rng.randint(30, 90)
            refills = rng.randint(0, 5)
            
            directions = f'Take {rng.randint(1, 3)} tablet(s) {rng.choice(["daily", "twice daily", "three times daily"])}'
            transmission = rng.choices(['ELECTRONIC', 'PHONE', 'FAX'], weights=[0.8, 0.15, 0.05])[0]
            status = rng.choices(['FILLED', 'PENDING', 'CANCELLED'], weights=[0.85, 0.10, 0.05])[0]
            
            prescriptions_data.append((
                prescription_id, f'RX{prescription_id:08d}', patient_id, prescriber_id,
                medication_id, pharmacy_id, written_date, quantity, days_supply,
                refills, directions, f'Indication {prescription_id}',
                transmission, status
            ))
            
            # Create fills for filled prescriptions
            if status == 'FILLED':
                fill_date = (datetime.strptime(written_date, '%Y-%m-%d') + 
                           timedelta(days=rng.randint(0, 3))).strftime('%Y-%m-%d')
                
                fills_data.append((
                    fill_id, prescription_id, 1, fill_date, quantity, days_supply,
                    f'RPH{rng.randint(1, 50):03d}', 'COMPLETE',
                    rng.uniform(5, 50), rng.uniform(20, 200), rng.uniform(5, 30)
                ))
                fill_id += 1
            
            prescription_id += 1
    
    for chunk in batch(prescriptions_data, 1000):
        conn.executemany("INSERT INTO prescriptions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(fills_data, 1000):
        conn.executemany("INSERT INTO prescription_fills VALUES (?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_prescriptions_written_date ON prescriptions(written_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_prescription_fills_prescription ON prescription_fills(prescription_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()