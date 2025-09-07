#!/usr/bin/env python3
"""Populate workforce management normalized schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta, time
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

# Scale constants
AGENTS = 300
SKILLS = 25
SHIFTS_PER_DAY = 15
DAYS = 30

# Skill catalog
SKILL_CATALOG = [
    ('English', 'LANGUAGE', False),
    ('Spanish', 'LANGUAGE', False),
    ('French', 'LANGUAGE', False),
    ('CRM_System', 'TECHNICAL', True),
    ('Billing_Platform', 'TECHNICAL', True),
    ('API_Support', 'TECHNICAL', True),
    ('Product_Basic', 'PRODUCT', False),
    ('Product_Advanced', 'PRODUCT', True),
    ('Conflict_Resolution', 'SOFT_SKILL', False),
    ('Sales_Techniques', 'SOFT_SKILL', False),
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
    
    # Insert agents
    print(f"Inserting {AGENTS} agents...")
    agents_data = []
    depts = ['SUPPORT', 'SALES', 'TECHNICAL', 'BILLING', 'RETENTION']
    dept_weights = [0.40, 0.25, 0.20, 0.10, 0.05]
    levels = ['JUNIOR', 'MID', 'SENIOR', 'LEAD', 'MANAGER']
    level_weights = [0.30, 0.35, 0.25, 0.08, 0.02]
    
    for i in range(1, AGENTS + 1):
        dept = rng.choices(depts, weights=dept_weights)[0]
        level = rng.choices(levels, weights=level_weights)[0]
        emp_type = rng.choices(['FULL_TIME', 'PART_TIME', 'CONTRACT'], weights=[0.70, 0.20, 0.10])[0]
        hire_days = rng.randint(30, 1000) if level != 'JUNIOR' else rng.randint(30, 365)
        hire_date = (datetime.now() - timedelta(days=hire_days)).strftime('%Y-%m-%d')
        status = rng.choices(['ACTIVE', 'ON_LEAVE', 'TRAINING'], weights=[0.90, 0.05, 0.05])[0]
        
        agents_data.append((i, f'EMP{i:04d}', f'Agent {i}', f'agent{i}@company.com', 
                          dept, level, emp_type, hire_date, status))
    
    conn.executemany("INSERT INTO agents VALUES (?,?,?,?,?,?,?,?,?)", agents_data)
    
    # Insert skills
    print("Inserting skills...")
    skills_data = [(i+1, name, cat, cert) for i, (name, cat, cert) in enumerate(SKILL_CATALOG)]
    conn.executemany("INSERT INTO skills VALUES (?,?,?,?)", skills_data)
    
    # Assign skills to agents
    print("Assigning skills...")
    agent_skills_data = []
    skill_id = 1
    
    for agent_id in range(1, AGENTS + 1):
        num_skills = rng.randint(2, 6)
        selected_skills = rng.sample(range(1, len(SKILL_CATALOG) + 1), num_skills)
        
        for skill_idx in selected_skills:
            proficiency = rng.randint(1, 5)
            cert_date = None
            exp_date = None
            if skills_data[skill_idx-1][3] and proficiency >= 3:
                cert_date = (datetime.now() - timedelta(days=rng.randint(30, 365))).strftime('%Y-%m-%d')
                exp_date = (datetime.now() + timedelta(days=rng.randint(180, 730))).strftime('%Y-%m-%d')
            
            agent_skills_data.append((skill_id, agent_id, skill_idx, proficiency, cert_date, exp_date))
            skill_id += 1
    
    conn.executemany("INSERT INTO agent_skills VALUES (?,?,?,?,?,?)", agent_skills_data)
    
    # Generate shifts
    print("Generating shifts...")
    shifts_data = []
    shift_id = 1
    base_date = datetime.now() - timedelta(days=15)
    
    for day in range(DAYS):
        date = base_date + timedelta(days=day)
        for shift_type, hours, req in [('MORNING', (6, 14), 40), ('AFTERNOON', (14, 22), 50), 
                                       ('NIGHT', (22, 6), 20)]:
            required = int(req * (0.7 if date.weekday() >= 5 else 1.0))
            min_level = 'MID' if shift_type == 'NIGHT' else 'JUNIOR'
            
            shifts_data.append((shift_id, date.strftime('%Y-%m-%d'), f'{hours[0]:02d}:00:00',
                              f'{hours[1]:02d}:00:00', shift_type, required, min_level))
            shift_id += 1
    
    conn.executemany("INSERT INTO shifts VALUES (?,?,?,?,?,?,?)", shifts_data)
    
    # Create schedules
    print("Creating schedules...")
    schedules_data = []
    schedule_id = 1
    
    for shift in shifts_data[:len(shifts_data)//2]:  # Only schedule half for brevity
        shift_id = shift[0]
        required = min(shift[5], 20)  # Limit per shift
        available = [a[0] for a in agents_data if a[8] == 'ACTIVE']
        
        for agent_id in rng.sample(available, min(required, len(available))):
            status = rng.choices(['SCHEDULED', 'CONFIRMED', 'COMPLETED'], weights=[0.20, 0.30, 0.50])[0]
            check_in = None
            check_out = None
            if status == 'COMPLETED':
                check_in = f"{shift[1]} {shift[2]}"
                check_out = f"{shift[1]} {shift[3]}"
            
            schedules_data.append((schedule_id, agent_id, shift_id, status, check_in, check_out, 30, 0))
            schedule_id += 1
    
    conn.executemany("INSERT INTO schedules VALUES (?,?,?,?,?,?,?,?)", schedules_data)
    
    # Time off requests
    print("Creating time off requests...")
    time_off_data = []
    request_id = 1
    
    for _ in range(int(AGENTS * 0.2)):  # 20% of agents have requests
        agent_id = rng.randint(1, AGENTS)
        req_type = rng.choice(['VACATION', 'SICK', 'PERSONAL'])
        start = datetime.now() + timedelta(days=rng.randint(-10, 30))
        duration = rng.randint(1, 5)
        end = start + timedelta(days=duration)
        status = rng.choice(['PENDING', 'APPROVED', 'REJECTED'])
        
        time_off_data.append((request_id, agent_id, req_type, start.strftime('%Y-%m-%d'),
                            end.strftime('%Y-%m-%d'), status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            None, 'Request'))
        request_id += 1
    
    conn.executemany("INSERT INTO time_off_requests VALUES (?,?,?,?,?,?,?,?,?)", time_off_data)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_department ON agents(department)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_skills_agent ON agent_skills(agent_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_shifts_date ON shifts(shift_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_schedules_agent_date ON schedules(agent_id, shift_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
