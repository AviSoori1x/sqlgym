#!/usr/bin/env python3
"""Populate ecommerce funnel A/B test normalized schema with synthetic data."""
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
EXPERIMENTS = 8
SESSIONS = 15000
EVENTS_PER_SESSION = 6

# Funnel step definitions
FUNNEL_STEPS = [
    ('Landing Page', 1, '/landing*', 'LANDING', True),
    ('Product Category', 2, '/category/*', 'CATEGORY', True),
    ('Product Detail', 3, '/product/*', 'PRODUCT', True),
    ('Add to Cart', 4, '/cart*', 'CART', True),
    ('Checkout Start', 5, '/checkout*', 'CHECKOUT', True),
    ('Order Complete', 6, '/confirmation*', 'CONFIRMATION', True)
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
    
    # Insert funnel steps
    print("Inserting funnel steps...")
    steps_data = [(i+1, name, order, pattern, step_type, required) 
                  for i, (name, order, pattern, step_type, required) in enumerate(FUNNEL_STEPS)]
    conn.executemany("INSERT INTO funnel_steps VALUES (?,?,?,?,?,?)", steps_data)
    
    # Insert experiments
    print(f"Inserting {EXPERIMENTS} experiments...")
    experiments_data = []
    for i in range(1, EXPERIMENTS + 1):
        start_date = (datetime.now() - timedelta(days=rng.randint(30, 90))).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=rng.randint(7, 30))).strftime('%Y-%m-%d')
        
        experiments_data.append((
            i, f'Experiment_{i}', rng.choice(['A_B', 'MULTIVARIATE']),
            rng.choice(['RUNNING', 'COMPLETED']), start_date, end_date,
            rng.uniform(0.1, 0.5), f'Test hypothesis {i}',
            'conversion_rate', rng.uniform(0.8, 0.99) if rng.random() < 0.7 else None
        ))
    
    conn.executemany("INSERT INTO experiments VALUES (?,?,?,?,?,?,?,?,?,?)", experiments_data)
    
    # Insert variants
    print("Inserting variants...")
    variants_data = []
    variant_id = 1
    
    for exp_id in range(1, EXPERIMENTS + 1):
        # Control variant
        variants_data.append((
            variant_id, exp_id, 'Control', 'CONTROL', 0.5, 
            json.dumps({'version': 'original'}), 0
        ))
        variant_id += 1
        
        # Treatment variant
        variants_data.append((
            variant_id, exp_id, 'Treatment', 'TREATMENT', 0.5,
            json.dumps({'version': 'new_design', 'feature': 'enabled'}), 0
        ))
        variant_id += 1
    
    conn.executemany("INSERT INTO variants VALUES (?,?,?,?,?,?,?)", variants_data)
    
    # Insert user sessions
    print(f"Inserting {SESSIONS} user sessions...")
    sessions_data = []
    
    for i in range(1, SESSIONS + 1):
        user_id = f'user_{rng.randint(1, 5000)}'
        session_id = f'session_{i}'
        
        # Assign to experiment (70% of sessions)
        if rng.random() < 0.7:
            exp_id = rng.randint(1, EXPERIMENTS)
            variant_id = exp_id * 2 - rng.randint(0, 1)  # Control or treatment
        else:
            exp_id = None
            variant_id = None
        
        start_time = (datetime.now() - timedelta(days=rng.randint(0, 60))).strftime('%Y-%m-%d %H:%M:%S')
        end_time = (datetime.fromisoformat(start_time.replace(' ', 'T')) + 
                   timedelta(minutes=rng.randint(2, 45))).strftime('%Y-%m-%d %H:%M:%S')
        
        device = rng.choices(['DESKTOP', 'MOBILE', 'TABLET'], weights=[0.45, 0.45, 0.10])[0]
        traffic_source = rng.choices(['ORGANIC', 'PAID', 'DIRECT', 'REFERRAL'], weights=[0.3, 0.3, 0.25, 0.15])[0]
        
        # Conversion varies by variant (treatment performs better)
        if variant_id and variant_id % 2 == 0:  # Treatment
            converted = rng.random() < 0.08
        else:  # Control or no experiment
            converted = rng.random() < 0.06
        
        conv_value = rng.uniform(50, 300) if converted else 0
        
        sessions_data.append((
            i, user_id, session_id, exp_id, variant_id, start_time, end_time,
            device, traffic_source, converted, conv_value
        ))
    
    for chunk in batch(sessions_data, 1000):
        conn.executemany("INSERT INTO user_sessions VALUES (?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert funnel events
    print("Inserting funnel events...")
    events_data = []
    event_id = 1
    
    for session in sessions_data:
        session_id = session[2]
        converted = session[9]
        
        # Determine how far through funnel this session goes
        if converted:
            max_step = len(FUNNEL_STEPS)  # Complete funnel
        else:
            # Drop off at various points
            max_step = rng.choices(range(1, len(FUNNEL_STEPS) + 1), 
                                 weights=[0.3, 0.25, 0.2, 0.15, 0.08, 0.02])[0]
        
        session_start = datetime.fromisoformat(session[5].replace(' ', 'T'))
        current_time = session_start
        
        for step_idx in range(max_step):
            step_id = step_idx + 1
            event_type = 'PAGE_VIEW' if step_idx < max_step - 1 else 'PURCHASE'
            
            # Time spent on step
            if step_idx == max_step - 1:  # Last step
                time_on_step = rng.randint(30, 300)
            else:
                time_on_step = rng.randint(15, 180)
            
            event_data = {'step': step_id, 'page_url': f'/step{step_id}'}
            
            events_data.append((
                event_id, session_id, step_id, current_time.strftime('%Y-%m-%d %H:%M:%S'),
                event_type, json.dumps(event_data), time_on_step
            ))
            
            current_time += timedelta(seconds=time_on_step)
            event_id += 1
    
    for chunk in batch(events_data, 1000):
        conn.executemany("INSERT INTO funnel_events VALUES (?,?,?,?,?,?,?)", chunk)
    
    # Insert conversion goals
    print("Inserting conversion goals...")
    goals_data = [
        (1, 'Purchase Completion', 'CONVERSION_RATE', 6, 24, 1),
        (2, 'Cart Addition', 'CONVERSION_RATE', 4, 24, 0),
        (3, 'Revenue per Session', 'REVENUE', 6, 24, 0)
    ]
    conn.executemany("INSERT INTO conversion_goals VALUES (?,?,?,?,?,?)", goals_data)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_experiment ON user_sessions(experiment_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_timestamp ON user_sessions(start_timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_funnel_events_session ON funnel_events(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_funnel_events_timestamp ON funnel_events(timestamp)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()