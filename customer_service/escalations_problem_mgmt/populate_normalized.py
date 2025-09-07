#!/usr/bin/env python3
"""Populate escalations and problem management normalized schema with synthetic data."""
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
CUSTOMERS = 2000
AGENTS = 100
ISSUES = 20000
ESCALATION_RATE = 0.25
PROBLEM_RATE = 0.05

# Agent distribution by level
AGENT_LEVELS = {
    'L1': 0.50,
    'L2': 0.30,
    'L3': 0.15,
    'MANAGER': 0.04,
    'DIRECTOR': 0.01
}

def can_escalate_to(from_level, to_level):
    """Check if escalation path is valid."""
    hierarchy = ['L1', 'L2', 'L3', 'MANAGER', 'DIRECTOR']
    return hierarchy.index(to_level) > hierarchy.index(from_level)

def get_resolution_hours(severity, escalation_count):
    """Calculate resolution time based on severity and escalations."""
    base_hours = {
        'LOW': 4,
        'MEDIUM': 8,
        'HIGH': 24,
        'CRITICAL': 4
    }
    return base_hours[severity] * (1 + escalation_count * 0.5)

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
    tiers = ['BRONZE', 'SILVER', 'GOLD', 'PLATINUM']
    tier_weights = [0.50, 0.30, 0.15, 0.05]
    
    for i in range(1, CUSTOMERS + 1):
        tier = rng.choices(tiers, weights=tier_weights)[0]
        # Account value correlates with tier
        value_ranges = {
            'BRONZE': (1000, 10000),
            'SILVER': (10000, 50000),
            'GOLD': (50000, 200000),
            'PLATINUM': (200000, 1000000)
        }
        account_value = rng.randint(*value_ranges[tier])
        customers_data.append((i, f'Customer_{i}', tier, account_value))
    
    for chunk in batch(customers_data, 1000):
        conn.executemany("INSERT INTO customers VALUES (?,?,?,?)", chunk)
    
    # Insert agents
    print(f"Inserting {AGENTS} agents...")
    agents_data = []
    departments = ['SUPPORT', 'TECHNICAL', 'BILLING', 'SALES']
    agent_id = 1
    
    for dept in departments:
        dept_size = AGENTS // len(departments)
        for _ in range(dept_size):
            level = rng.choices(list(AGENT_LEVELS.keys()), weights=list(AGENT_LEVELS.values()))[0]
            agents_data.append((
                agent_id, 
                f'Agent_{agent_id}',
                f'agent{agent_id}@company.com',
                level,
                dept
            ))
            agent_id += 1
    
    conn.executemany("INSERT INTO agents VALUES (?,?,?,?,?)", agents_data)
    
    # Create agent lookup for escalations
    agents_by_level = {}
    for agent in agents_data:
        level = agent[3]
        if level not in agents_by_level:
            agents_by_level[level] = []
        agents_by_level[level].append(agent[0])
    
    # Insert issues and escalations
    print(f"Inserting {ISSUES} issues...")
    issues_data = []
    escalations_data = []
    problem_records_data = []
    
    issue_id = 1
    escalation_id = 1
    problem_id = 1
    base_date = datetime(2024, 1, 1)
    
    categories = ['BUG', 'BILLING', 'ACCESS', 'PERFORMANCE', 'FEATURE_REQUEST', 'COMPLIANCE']
    severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    severity_weights = [0.40, 0.35, 0.20, 0.05]
    
    for _ in range(ISSUES):
        customer_id = rng.randint(1, CUSTOMERS)
        customer_tier = customers_data[customer_id-1][2]
        
        # L1 agents typically create initial issues
        created_by = rng.choice(agents_by_level['L1'])
        category = rng.choice(categories)
        
        # Severity influenced by customer tier
        if customer_tier == 'PLATINUM':
            severity = rng.choices(severities, weights=[0.20, 0.30, 0.35, 0.15])[0]
        else:
            severity = rng.choices(severities, weights=severity_weights)[0]
        
        created_at = base_date + timedelta(
            days=rng.randint(0, 30),
            hours=rng.randint(8, 18),
            minutes=rng.randint(0, 59)
        )
        
        # Determine if issue gets escalated
        will_escalate = rng.random() < ESCALATION_RATE or severity == 'CRITICAL'
        escalation_count = 0
        current_agent = created_by
        current_level = 'L1'
        
        # Generate escalation chain
        if will_escalate:
            max_escalations = rng.randint(1, 3)
            for _ in range(max_escalations):
                # Find next level
                possible_levels = [l for l in ['L2', 'L3', 'MANAGER', 'DIRECTOR'] 
                                 if can_escalate_to(current_level, l)]
                if not possible_levels:
                    break
                
                next_level = possible_levels[0]  # Usually escalate to next level
                if rng.random() < 0.2 and len(possible_levels) > 1:
                    next_level = possible_levels[1]  # Sometimes skip a level
                
                next_agent = rng.choice(agents_by_level[next_level])
                
                # Determine escalation reason
                if severity == 'CRITICAL':
                    reason = 'SLA_BREACH'
                elif customer_tier == 'PLATINUM':
                    reason = 'HIGH_VALUE_CUSTOMER'
                elif category == 'COMPLIANCE':
                    reason = 'LEGAL_RISK'
                else:
                    reason = rng.choice(['EXPERTISE_REQUIRED', 'CUSTOMER_REQUEST'])
                
                escalate_time = created_at + timedelta(hours=rng.randint(1, 8))
                
                escalations_data.append((
                    escalation_id,
                    issue_id,
                    current_agent,
                    next_agent,
                    reason,
                    escalate_time.strftime('%Y-%m-%d %H:%M:%S'),
                    f'Escalating {category} issue for {severity} severity'
                ))
                
                escalation_id += 1
                escalation_count += 1
                current_agent = next_agent
                current_level = next_level
        
        # Determine resolution
        if rng.random() < 0.85:  # 85% get resolved
            status = 'RESOLVED'
            resolution_hours = get_resolution_hours(severity, escalation_count)
            resolved_at = created_at + timedelta(hours=resolution_hours + rng.uniform(-2, 2))
        else:
            status = rng.choice(['OPEN', 'IN_PROGRESS', 'ESCALATED'])
            resolved_at = None
        
        updated_at = resolved_at if resolved_at else created_at + timedelta(hours=rng.randint(1, 24))
        
        # Calculate impact score
        impact_base = {'LOW': 10, 'MEDIUM': 30, 'HIGH': 60, 'CRITICAL': 90}
        impact_score = min(100, impact_base[severity] + rng.randint(-10, 10))
        
        issues_data.append((
            issue_id,
            customer_id,
            created_by,
            category,
            severity,
            status,
            created_at.strftime('%Y-%m-%d %H:%M:%S'),
            updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            resolved_at.strftime('%Y-%m-%d %H:%M:%S') if resolved_at else None,
            f'{category} issue: {severity} priority for customer',
            impact_score
        ))
        
        # Create problem record for some high-impact issues
        if (severity in ['HIGH', 'CRITICAL'] and rng.random() < PROBLEM_RATE) or \
           (escalation_count >= 2 and rng.random() < PROBLEM_RATE * 2):
            
            affected = rng.randint(5, 100) if category == 'BUG' else rng.randint(1, 20)
            problem_status = rng.choice(['INVESTIGATING', 'ROOT_CAUSE_FOUND', 'FIX_IN_PROGRESS', 'RESOLVED'])
            
            problem_created = created_at + timedelta(hours=rng.randint(2, 24))
            problem_closed = None
            if problem_status == 'RESOLVED':
                problem_closed = problem_created + timedelta(days=rng.randint(1, 14))
            
            root_causes = {
                'BUG': 'Code defect in module X',
                'PERFORMANCE': 'Database query optimization needed',
                'ACCESS': 'Permission configuration error',
                'BILLING': 'Invoice generation logic flaw',
                'COMPLIANCE': 'Missing data validation',
                'FEATURE_REQUEST': 'Gap in current functionality'
            }
            
            problem_records_data.append((
                problem_id,
                issue_id,
                f'Multiple customers experiencing {category} issues',
                root_causes.get(category, 'Under investigation'),
                'Fix deployed to production' if problem_status == 'RESOLVED' else None,
                affected,
                problem_created.strftime('%Y-%m-%d %H:%M:%S'),
                problem_closed.strftime('%Y-%m-%d %H:%M:%S') if problem_closed else None,
                problem_status
            ))
            problem_id += 1
        
        issue_id += 1
    
    # Batch insert all data
    for chunk in batch(issues_data, 1000):
        conn.executemany("INSERT INTO issues VALUES (?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(escalations_data, 1000):
        conn.executemany("INSERT INTO escalations VALUES (?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(problem_records_data, 1000):
        conn.executemany("INSERT INTO problem_records VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_issues_customer ON issues(customer_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues(severity)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_issues_created ON issues(created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_escalations_issue ON escalations(issue_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_escalations_date ON escalations(escalated_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_problem_records_status ON problem_records(status)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()