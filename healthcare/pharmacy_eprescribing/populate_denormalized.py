#!/usr/bin/env python3
"""Populate pharmacy eprescribing denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
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
    
    print("Building prescription analytics...")
    analytics_query = """
    SELECT
        p.id as prescription_id,
        pat.patient_id,
        pat.first_name || ' ' || pat.last_name as patient_name,
        pres.first_name || ' ' || pres.last_name as prescriber_name,
        pres.specialty,
        m.generic_name,
        m.brand_name,
        m.drug_class,
        p.written_date,
        p.quantity_prescribed,
        p.days_supply,
        p.status as prescription_status,
        COUNT(pf.id) as fill_count,
        SUM(pf.quantity_dispensed) as total_dispensed,
        MAX(pf.fill_date) as last_fill_date
    FROM prescriptions p
    JOIN patients pat ON p.patient_id = pat.id
    JOIN prescribers pres ON p.prescriber_id = pres.id
    JOIN medications m ON p.medication_id = m.id
    LEFT JOIN prescription_fills pf ON p.id = pf.prescription_id
    GROUP BY p.id
    """
    
    analytics_data = []
    for row in norm_conn.execute(analytics_query):
        # Calculate adherence metrics
        days_supply = row['days_supply'] or 30
        fill_count = row['fill_count'] or 0
        
        if fill_count > 0:
            adherence_rate = min(1.0, fill_count / max(1, days_supply / 30))
        else:
            adherence_rate = 0.0
        
        analytics_data.append(tuple(row) + (adherence_rate,))
    
    denorm_conn.executemany("""
        INSERT INTO prescription_analytics VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, analytics_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_prescription_analytics_patient ON prescription_analytics(patient_id)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()