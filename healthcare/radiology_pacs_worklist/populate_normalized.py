#!/usr/bin/env python3
"""Populate radiology PACS worklist normalized schema with synthetic data."""
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
PATIENTS = 5000
RADIOLOGISTS = 40
IMAGING_STUDIES = 40000

# Imaging study templates
STUDY_TEMPLATES = [
    ('CT', 'Head', 'CT Head without contrast'),
    ('CT', 'Chest', 'CT Chest with contrast'),
    ('MRI', 'Brain', 'MRI Brain without contrast'),
    ('MRI', 'Knee', 'MRI Knee without contrast'),
    ('XRAY', 'Chest', 'Chest X-ray 2 views'),
    ('XRAY', 'Hand', 'Hand X-ray 3 views'),
    ('ULTRASOUND', 'Abdomen', 'Abdominal ultrasound'),
    ('MAMMOGRAPHY', 'Breast', 'Screening mammography'),
    ('NUCLEAR', 'Heart', 'Myocardial perfusion scan'),
    ('PET', 'Whole Body', 'PET/CT whole body')
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
    
    # Insert radiologists
    print(f"Inserting {RADIOLOGISTS} radiologists...")
    radiologists_data = []
    subspecialties = ['GENERAL', 'NEURO', 'CARDIAC', 'MUSCULOSKELETAL', 'ABDOMINAL', 'CHEST']
    
    for i in range(1, RADIOLOGISTS + 1):
        subspecialty = rng.choice(subspecialties)
        shift_pref = rng.choice(['DAY', 'EVENING', 'ANY'])
        
        radiologists_data.append((
            i, f'RAD{i:03d}', f'Dr. Radiologist{i}', f'LastName{i}',
            subspecialty, f'LIC{i:06d}', shift_pref, 'ACTIVE'
        ))
    
    conn.executemany("INSERT INTO radiologists VALUES (?,?,?,?,?,?,?,?)", radiologists_data)
    
    # Insert imaging studies
    print(f"Inserting {IMAGING_STUDIES} imaging studies...")
    studies_data = []
    images_data = []
    assignments_data = []
    reports_data = []
    
    study_id = 1
    image_id = 1
    assignment_id = 1
    report_id = 1
    
    for _ in range(IMAGING_STUDIES):
        patient_id = rng.randint(1, PATIENTS)
        modality, body_part, description = rng.choice(STUDY_TEMPLATES)
        
        study_datetime = (datetime.now() - timedelta(days=rng.randint(1, 180))).strftime('%Y-%m-%d %H:%M:%S')
        priority = rng.choices(['ROUTINE', 'URGENT', 'STAT'], weights=[0.8, 0.15, 0.05])[0]
        contrast = rng.random() < 0.3  # 30% use contrast
        status = rng.choices(['COMPLETED', 'IN_PROGRESS', 'CANCELLED'], weights=[0.85, 0.10, 0.05])[0]
        
        studies_data.append((
            study_id, f'ACC{study_id:09d}', patient_id, study_datetime,
            modality, body_part, description, f'Dr. Ordering{rng.randint(1, 200)}',
            f'Clinical indication {study_id}', contrast, status, priority
        ))
        
        # Create images for completed studies
        if status == 'COMPLETED':
            num_images = rng.randint(10, 100)  # Varies by modality
            
            for img_num in range(1, min(num_images + 1, 20)):  # Limit for performance
                acquisition_time = (datetime.strptime(study_datetime, '%Y-%m-%d %H:%M:%S') + 
                                  timedelta(minutes=img_num * 2)).strftime('%Y-%m-%d %H:%M:%S')
                
                image_type = rng.choice(['SCOUT', 'AXIAL', 'CORONAL', 'SAGITTAL'])
                quality = rng.choices(['EXCELLENT', 'GOOD', 'FAIR'], weights=[0.7, 0.25, 0.05])[0]
                file_size = rng.uniform(5, 50)  # MB
                
                images_data.append((
                    image_id, study_id, img_num, image_type,
                    acquisition_time, quality, file_size
                ))
                image_id += 1
            
            # Create worklist assignment
            radiologist_id = rng.randint(1, RADIOLOGISTS)
            assignment_datetime = (datetime.strptime(study_datetime, '%Y-%m-%d %H:%M:%S') + 
                                 timedelta(hours=rng.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S')
            
            assignments_data.append((
                assignment_id, study_id, radiologist_id, assignment_datetime,
                'PRIMARY', 1, rng.randint(15, 60), 'COMPLETED'
            ))
            assignment_id += 1
            
            # Create radiology report
            report_datetime = (datetime.strptime(assignment_datetime, '%Y-%m-%d %H:%M:%S') + 
                             timedelta(hours=rng.randint(1, 8))).strftime('%Y-%m-%d %H:%M:%S')
            
            findings = f'Findings for {description}: Normal study'
            impression = f'Impression: Normal {body_part.lower()} {modality.lower()}'
            critical_finding = rng.random() < 0.05  # 5% critical findings
            
            reports_data.append((
                report_id, study_id, radiologist_id, report_datetime,
                findings, impression, 'Recommend follow-up if clinically indicated',
                'FINAL', rng.uniform(10, 45), critical_finding
            ))
            report_id += 1
        
        study_id += 1
    
    # Batch insert all data
    for chunk in batch(studies_data, 1000):
        conn.executemany("INSERT INTO imaging_studies VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(images_data, 1000):
        conn.executemany("INSERT INTO study_images VALUES (?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(assignments_data, 1000):
        conn.executemany("INSERT INTO worklist_assignments VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(reports_data, 1000):
        conn.executemany("INSERT INTO radiology_reports VALUES (?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_patients_mrn ON patients(medical_record_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_imaging_studies_patient ON imaging_studies(patient_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_imaging_studies_datetime ON imaging_studies(study_datetime)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_worklist_assignments_radiologist ON worklist_assignments(radiologist_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()