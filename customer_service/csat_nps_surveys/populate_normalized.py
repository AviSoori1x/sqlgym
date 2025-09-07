#!/usr/bin/env python3
"""Populate CSAT/NPS survey normalized schema with synthetic data."""
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
CUSTOMERS = 5000
TOUCHPOINTS = 12
SURVEYS = 30000
RESPONSE_RATE = 0.35

# Touchpoint definitions
TOUCHPOINT_DATA = [
    ('Purchase Confirmation', 'EMAIL'),
    ('Support Chat', 'WEB'),
    ('Mobile App', 'IN_APP'),
    ('Call Center', 'PHONE'),
    ('Order Delivery', 'SMS'),
    ('Account Dashboard', 'WEB'),
    ('Onboarding Email', 'EMAIL'),
    ('Renewal Notice', 'EMAIL'),
    ('Feature Tutorial', 'IN_APP'),
    ('Billing Portal', 'WEB'),
    ('Customer Success Call', 'PHONE'),
    ('Product Update', 'EMAIL')
]

def get_score_category(score, survey_type):
    """Categorize score based on survey type."""
    if survey_type == 'NPS':
        if score >= 9:
            return 'Promoter'
        elif score >= 7:
            return 'Passive'
        else:
            return 'Detractor'
    elif survey_type == 'CSAT':
        if score >= 8:
            return 'Satisfied'
        elif score >= 6:
            return 'Neutral'
        else:
            return 'Dissatisfied'
    else:  # CES
        if score <= 3:
            return 'Easy'
        elif score <= 5:
            return 'Moderate'
        else:
            return 'Difficult'

def generate_comment(rng, score, survey_type):
    """Generate realistic comment based on score."""
    if score >= 8:
        positive = [
            "Great service, very satisfied!",
            "Excellent experience overall",
            "Would definitely recommend",
            "Team was very helpful",
            "Quick and easy process"
        ]
        return rng.choice(positive) if rng.random() < 0.3 else None
    elif score <= 4:
        negative = [
            "Very disappointed with the service",
            "Process was too complicated",
            "Long wait times, poor communication",
            "Need to improve customer support",
            "Not what I expected"
        ]
        return rng.choice(negative) if rng.random() < 0.5 else None
    else:
        return None

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
    segments = ['ENTERPRISE', 'SMB', 'CONSUMER']
    segment_weights = [0.15, 0.35, 0.50]
    base_date = datetime(2023, 1, 1)
    
    for i in range(1, CUSTOMERS + 1):
        segment = rng.choices(segments, weights=segment_weights)[0]
        created = base_date + timedelta(days=rng.randint(0, 365))
        customers_data.append((i, f'customer{i}@example.com', segment, created.strftime('%Y-%m-%d')))
    
    for chunk in batch(customers_data, 1000):
        conn.executemany("INSERT INTO customers VALUES (?,?,?,?)", chunk)
    
    # Insert touchpoints
    print(f"Inserting {len(TOUCHPOINT_DATA)} touchpoints...")
    touchpoints_data = [(i+1, name, channel) for i, (name, channel) in enumerate(TOUCHPOINT_DATA)]
    conn.executemany("INSERT INTO touchpoints VALUES (?,?,?)", touchpoints_data)
    
    # Insert surveys and related data
    print(f"Inserting {SURVEYS} surveys...")
    surveys_data = []
    triggers_data = []
    followups_data = []
    
    survey_id = 1
    trigger_id = 1
    followup_id = 1
    base_survey_date = datetime(2024, 1, 1)
    
    # Survey type distribution
    survey_types = ['CSAT', 'NPS', 'CES']
    type_weights = [0.5, 0.35, 0.15]
    
    # Trigger events
    trigger_events = ['PURCHASE', 'SUPPORT_CLOSE', 'ONBOARDING', 'RENEWAL', 'CANCELLATION']
    
    for _ in range(SURVEYS):
        customer_id = rng.randint(1, CUSTOMERS)
        touchpoint_id = rng.randint(1, len(TOUCHPOINT_DATA))
        survey_type = rng.choices(survey_types, weights=type_weights)[0]
        
        # Survey timing
        sent_at = base_survey_date + timedelta(
            days=rng.randint(0, 30),
            hours=rng.randint(8, 18),
            minutes=rng.randint(0, 59)
        )
        
        # Response simulation
        responded = rng.random() < RESPONSE_RATE
        if responded:
            # Response delay
            response_delay = timedelta(
                hours=rng.lognormvariate(1.5, 1.2),  # Log-normal distribution for realistic delays
                minutes=rng.randint(0, 59)
            )
            responded_at = sent_at + response_delay
            
            # Score generation (biased by segment and touchpoint)
            customer_segment = customers_data[customer_id-1][2]
            if customer_segment == 'ENTERPRISE':
                score = min(10, max(1, int(rng.normalvariate(8.5, 1.5))))
            elif customer_segment == 'SMB':
                score = min(10, max(1, int(rng.normalvariate(7.5, 2))))
            else:  # CONSUMER
                score = min(10, max(1, int(rng.normalvariate(7, 2.5))))
            
            status = 'COMPLETED'
            comment = generate_comment(rng, score, survey_type)
        else:
            responded_at = None
            score = None
            comment = None
            status = rng.choices(['SENT', 'OPENED', 'EXPIRED'], weights=[0.3, 0.4, 0.3])[0]
        
        surveys_data.append((
            survey_id, customer_id, touchpoint_id, survey_type,
            sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            responded_at.strftime('%Y-%m-%d %H:%M:%S') if responded_at else None,
            score, comment, status
        ))
        
        # Create trigger
        trigger_event = rng.choice(trigger_events)
        event_time = sent_at - timedelta(hours=rng.randint(1, 48))
        context = f'{{"order_id": {rng.randint(10000, 99999)}}}' if trigger_event == 'PURCHASE' else None
        
        triggers_data.append((
            trigger_id, survey_id, trigger_event,
            event_time.strftime('%Y-%m-%d %H:%M:%S'),
            context
        ))
        
        # Create follow-up for low scores
        if score and score <= 6:
            if score <= 3:
                action = rng.choices(['CALLBACK', 'ESCALATION'], weights=[0.7, 0.3])[0]
            else:
                action = rng.choices(['EMAIL', 'DISCOUNT', 'NONE'], weights=[0.5, 0.3, 0.2])[0]
            
            if action != 'NONE':
                assigned = f'agent_{rng.randint(1, 50)}' if action in ['CALLBACK', 'ESCALATION'] else None
                created = responded_at + timedelta(hours=rng.randint(1, 24))
                completed = created + timedelta(hours=rng.randint(4, 72)) if rng.random() < 0.8 else None
                outcome = rng.choice(['RESOLVED', 'PENDING', 'CUSTOMER_SATISFIED']) if completed else None
                
                followups_data.append((
                    followup_id, survey_id, action, assigned,
                    created.strftime('%Y-%m-%d %H:%M:%S'),
                    completed.strftime('%Y-%m-%d %H:%M:%S') if completed else None,
                    outcome
                ))
                followup_id += 1
        
        survey_id += 1
        trigger_id += 1
    
    # Batch insert all data
    for chunk in batch(surveys_data, 1000):
        conn.executemany("INSERT INTO surveys VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(triggers_data, 1000):
        conn.executemany("INSERT INTO survey_triggers VALUES (?,?,?,?,?)", chunk)
    
    for chunk in batch(followups_data, 1000):
        conn.executemany("INSERT INTO follow_ups VALUES (?,?,?,?,?,?,?)", chunk)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_surveys_customer ON surveys(customer_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_surveys_type ON surveys(survey_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_surveys_sent ON surveys(sent_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_surveys_status ON surveys(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_surveys_score ON surveys(score)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_triggers_event ON survey_triggers(trigger_event)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()