#!/usr/bin/env python3
"""Populate chatbot deflection normalized schema with synthetic data."""
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
CUSTOMERS = 3000
INTENT_CATEGORIES = 25
CONVERSATIONS = 15000
MESSAGES_PER_CONV = 8
ESCALATION_RATE = 0.2

# Common intents for chatbot
INTENTS = [
    ('Order Status', True, 'LOW'),
    ('Track Package', True, 'LOW'),
    ('Return Policy', True, 'LOW'),
    ('Product Information', True, 'LOW'),
    ('Account Balance', True, 'LOW'),
    ('Password Reset', True, 'LOW'),
    ('Billing Question', True, 'MEDIUM'),
    ('Technical Support', False, 'HIGH'),
    ('Refund Request', False, 'MEDIUM'),
    ('Complaint', False, 'HIGH'),
    ('Cancel Order', True, 'MEDIUM'),
    ('Update Profile', True, 'LOW'),
    ('Payment Failed', False, 'HIGH'),
    ('Shipping Cost', True, 'LOW'),
    ('Store Hours', True, 'LOW'),
    ('Warranty Info', True, 'LOW'),
    ('Promo Code', True, 'LOW'),
    ('Stock Check', True, 'LOW'),
    ('Installation Help', False, 'HIGH'),
    ('Account Locked', False, 'HIGH'),
    ('Fraud Alert', False, 'HIGH'),
    ('Service Outage', False, 'HIGH'),
    ('Upgrade Plan', True, 'MEDIUM'),
    ('FAQ', True, 'LOW'),
    ('Other', False, 'MEDIUM')
]

def generate_message_content(rng, intent_name, sender_type):
    """Generate realistic message content based on intent and sender."""
    if sender_type == 'CUSTOMER':
        templates = {
            'Order Status': ['Where is my order #{}?', 'Can you check order {} status?', 'I need to know about order {}'],
            'Track Package': ['How do I track package {}?', 'Tracking number {} not working', 'Where is my shipment {}?'],
            'Return Policy': ['What is your return policy?', 'How many days to return?', 'Can I return after 30 days?'],
            'Password Reset': ['I forgot my password', 'Cannot login to my account', 'Need password reset'],
            'Technical Support': ['The app keeps crashing', 'Error code {} appearing', 'System not working properly'],
            'Complaint': ['Very unhappy with service', 'Need to file a complaint', 'This is unacceptable'],
        }
        return rng.choice(templates.get(intent_name, ['I need help with something'])).format(rng.randint(10000, 99999))
    else:
        return f"Response regarding {intent_name} issue"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Create evidence_kv table if needed
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_kv (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    # Insert customers
    print(f"Inserting {CUSTOMERS} customers...")
    customers_data = []
    base_date = datetime(2023, 1, 1)
    for i in range(1, CUSTOMERS + 1):
        created = base_date + timedelta(days=rng.randint(0, 365))
        customers_data.append((i, f'customer{i}@example.com', created.strftime('%Y-%m-%d')))
    
    for chunk in batch(customers_data, 1000):
        conn.executemany("INSERT INTO customers VALUES (?,?,?)", chunk)
    
    # Insert intent categories
    print(f"Inserting {len(INTENTS)} intent categories...")
    intent_data = [(i+1, name, deflect, priority) for i, (name, deflect, priority) in enumerate(INTENTS)]
    conn.executemany("INSERT INTO intent_categories VALUES (?,?,?,?)", intent_data)
    
    # Insert conversations
    print(f"Inserting {CONVERSATIONS} conversations...")
    conversations_data = []
    messages_data = []
    escalations_data = []
    
    conv_id = 1
    msg_id = 1
    esc_id = 1
    base_conv_date = datetime(2024, 1, 1)
    
    for _ in range(CONVERSATIONS):
        customer_id = rng.randint(1, CUSTOMERS)
        channel = rng.choice(['WEB', 'MOBILE', 'SMS', 'VOICE'])
        started = base_conv_date + timedelta(
            days=rng.randint(0, 30),
            hours=rng.randint(8, 20),
            minutes=rng.randint(0, 59)
        )
        
        # Pick primary intent
        intent_id = rng.randint(1, len(INTENTS))
        intent_name = INTENTS[intent_id-1][0]
        deflectable = INTENTS[intent_id-1][1]
        
        # Determine if escalated
        will_escalate = rng.random() < ESCALATION_RATE or not deflectable
        
        # Set status based on escalation and other factors
        if will_escalate:
            status = 'ESCALATED'
        elif rng.random() < 0.1:
            status = 'ABANDONED'
        else:
            status = 'RESOLVED'
        
        # Calculate end time
        duration_minutes = rng.randint(2, 45) if status != 'ABANDONED' else rng.randint(1, 10)
        ended = None if status == 'ACTIVE' else started + timedelta(minutes=duration_minutes)
        
        # Satisfaction score (only for resolved/escalated)
        satisfaction = None
        if status in ('RESOLVED', 'ESCALATED') and rng.random() < 0.7:
            if status == 'RESOLVED':
                satisfaction = rng.choices([5, 4, 3, 2, 1], weights=[40, 30, 20, 7, 3])[0]
            else:
                satisfaction = rng.choices([5, 4, 3, 2, 1], weights=[10, 20, 30, 25, 15])[0]
        
        conversations_data.append((
            conv_id, customer_id, channel, started.strftime('%Y-%m-%d %H:%M:%S'),
            ended.strftime('%Y-%m-%d %H:%M:%S') if ended else None,
            status, intent_id, satisfaction
        ))
        
        # Generate messages
        num_messages = rng.randint(3, MESSAGES_PER_CONV)
        msg_time = started
        
        for j in range(num_messages):
            sender_type = 'CUSTOMER' if j % 2 == 0 else 'BOT'
            if will_escalate and j >= num_messages - 2:
                sender_type = 'AGENT' if j == num_messages - 1 else sender_type
            
            content = generate_message_content(rng, intent_name, sender_type)
            confidence = None if sender_type == 'CUSTOMER' else rng.uniform(0.6, 0.99)
            
            messages_data.append((
                msg_id, conv_id, sender_type, content, 
                intent_id if sender_type == 'BOT' else None,
                confidence, msg_time.strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            msg_id += 1
            msg_time += timedelta(seconds=rng.randint(10, 120))
        
        # Generate escalation if needed
        if will_escalate:
            reasons = ['LOW_CONFIDENCE', 'CUSTOMER_REQUEST', 'COMPLEX_ISSUE', 'SENTIMENT_NEGATIVE']
            reason = rng.choice(reasons)
            escalated_at = started + timedelta(minutes=rng.randint(5, 20))
            resolved_at = escalated_at + timedelta(minutes=rng.randint(10, 30)) if status == 'ESCALATED' else None
            
            escalations_data.append((
                esc_id, conv_id, reason, 
                escalated_at.strftime('%Y-%m-%d %H:%M:%S'),
                rng.randint(100, 200),  # agent_id
                resolved_at.strftime('%Y-%m-%d %H:%M:%S') if resolved_at else None
            ))
            esc_id += 1
        
        conv_id += 1
    
    # Batch insert all data
    for chunk in batch(conversations_data, 1000):
        conn.executemany("INSERT INTO conversations VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(messages_data, 1000):
        conn.executemany("INSERT INTO messages VALUES (?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(escalations_data, 1000):
        conn.executemany("INSERT INTO escalations VALUES (?,?,?,?,?,?)", chunk)
    
    conn.commit()
    
    # Create indexes after bulk loading
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_customer ON conversations(customer_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_started ON conversations(started_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, sent_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_intent ON messages(intent_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_escalations_reason ON escalations(reason)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
