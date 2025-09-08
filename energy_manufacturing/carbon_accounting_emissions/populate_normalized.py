#!/usr/bin/env python3
"""Populate carbon accounting emissions normalized schema with synthetic data."""
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
FACILITIES = 25
SOURCES_PER_FACILITY = 12
ACTIVITY_RECORDS_PER_SOURCE = 36

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert facilities
    print(f"Inserting {FACILITIES} facilities...")
    facilities_data = []
    
    facility_types = ['POWER_PLANT', 'MANUFACTURING', 'REFINERY', 'CHEMICAL_PLANT']
    countries = ['USA', 'Canada', 'Germany', 'UK', 'Japan']
    
    for i in range(1, FACILITIES + 1):
        facility_type = rng.choice(facility_types)
        country = rng.choice(countries)
        capacity = rng.uniform(10000, 1000000)
        start_date = (datetime.now() - timedelta(days=rng.randint(365, 7300))).strftime('%Y-%m-%d')
        
        facilities_data.append((
            i, f'FAC{i:03d}', f'{facility_type.title()} {i}', facility_type,
            f'Location {i}, {country}', country, f'{country}_REGION',
            start_date, round(capacity, 2), 'OPERATIONAL'
        ))
    
    conn.executemany("INSERT INTO facilities VALUES (?,?,?,?,?,?,?,?,?,?)", facilities_data)
    
    # Insert emission factors
    factors_data = [
        (1, 'EF001', 'NATURAL_GAS_COMBUSTION', 'CO2', 1.96, 'kg CO2/m3', 'EPA AP-42', '2024-01-01', None, 10.0, 1),
        (2, 'EF002', 'COAL_COMBUSTION', 'CO2', 2.23, 'kg CO2/kg', 'EPA AP-42', '2024-01-01', None, 15.0, 1),
        (3, 'EF003', 'ELECTRICITY_CONSUMPTION', 'CO2', 0.45, 'kg CO2/kWh', 'Grid Average', '2024-01-01', None, 20.0, 1)
    ]
    conn.executemany("INSERT INTO emission_factors VALUES (?,?,?,?,?,?,?,?,?,?,?)", factors_data)
    
    # Insert emission sources
    print("Inserting emission sources...")
    sources_data = []
    source_id = 1
    
    for facility_id in range(1, FACILITIES + 1):
        for j in range(SOURCES_PER_FACILITY):
            source_type = rng.choice(['COMBUSTION', 'PROCESS', 'INDIRECT'])
            category = rng.choice(['SCOPE_1', 'SCOPE_2'])
            fuel_type = rng.choice(['NATURAL_GAS', 'ELECTRICITY', 'COAL'])
            
            sources_data.append((
                source_id, f'SRC{source_id:05d}', facility_id, f'Source {j+1}',
                source_type, category, fuel_type, f'Equipment description {source_id}',
                '2023-01-01', 1
            ))
            source_id += 1
    
    conn.executemany("INSERT INTO emission_sources VALUES (?,?,?,?,?,?,?,?,?,?)", sources_data)
    
    # Insert activity data
    print("Inserting activity data...")
    activity_data = []
    emissions_data = []
    
    activity_id = 1
    emission_id = 1
    
    for source in sources_data:
        source_id = source[0]
        fuel_type = source[6]
        
        for month_offset in range(36):  # 3 years
            reporting_period = (datetime.now() - timedelta(days=month_offset * 30)).strftime('%Y-%m')
            
            if fuel_type == 'NATURAL_GAS':
                activity_amount = rng.uniform(10000, 500000)
                activity_units = 'm3'
                factor_id = 1
            elif fuel_type == 'ELECTRICITY':
                activity_amount = rng.uniform(100000, 5000000)
                activity_units = 'kWh'
                factor_id = 3
            else:
                activity_amount = rng.uniform(1000, 100000)
                activity_units = 'kg'
                factor_id = 2
            
            activity_data.append((
                activity_id, source_id, reporting_period, 'FUEL_CONSUMPTION',
                round(activity_amount, 2), activity_units, 'MEASURED',
                'Continuous monitoring', f'Ref {activity_id}'
            ))
            
            # Calculate emissions
            factor = factors_data[factor_id - 1]
            emission_amount = activity_amount * factor[4]
            
            emissions_data.append((
                emission_id, source_id, activity_id, factor_id, reporting_period,
                factor[3], round(emission_amount, 2), round(emission_amount, 2),
                'Direct calculation', datetime.now().strftime('%Y-%m-%d'), 1, datetime.now().strftime('%Y-%m-%d')
            ))
            
            activity_id += 1
            emission_id += 1
    
    for chunk in batch(activity_data, 1000):
        conn.executemany("INSERT INTO activity_data VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(emissions_data, 1000):
        conn.executemany("INSERT INTO emissions_calculations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_emission_sources_facility ON emission_sources(facility_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_data_source ON activity_data(source_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_emissions_calculations_period ON emissions_calculations(reporting_period)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
