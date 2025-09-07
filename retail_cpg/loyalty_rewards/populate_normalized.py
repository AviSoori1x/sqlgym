#!/usr/bin/env python3
"""Populate loyalty rewards normalized schema with synthetic data."""
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
MEMBERS = 8000
POINT_TRANSACTIONS_PER_MEMBER = 15
REDEMPTIONS_PER_MEMBER = 3

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert tiers
    print("Inserting loyalty tiers...")
    tiers_data = [
        (1, 'Bronze', 1, 0, 0, json.dumps(['Basic rewards', '1x points']), 1.0, 1),
        (2, 'Silver', 2, 1000, 5000, json.dumps(['Free shipping', '1.25x points', 'Birthday bonus']), 1.25, 1),
        (3, 'Gold', 3, 5000, 25000, json.dumps(['Premium rewards', '1.5x points', 'Early access']), 1.5, 1),
        (4, 'Platinum', 4, 15000, 75000, json.dumps(['VIP treatment', '2x points', 'Personal shopper']), 2.0, 1)
    ]
    conn.executemany("INSERT INTO tiers VALUES (?,?,?,?,?,?,?,?)", tiers_data)
    
    # Insert rewards catalog
    print("Inserting rewards catalog...")
    rewards_data = [
        (1, '$5 Off Purchase', 'DISCOUNT', 500, 5.0, None, None, 1, '2024-01-01', '2024-12-31'),
        (2, '$10 Off Purchase', 'DISCOUNT', 1000, 10.0, None, None, 1, '2024-01-01', '2024-12-31'),
        (3, 'Free Shipping', 'FREE_SHIPPING', 250, 8.0, None, None, 1, '2024-01-01', '2024-12-31'),
        (4, 'Free Coffee Mug', 'FREE_PRODUCT', 750, 15.0, None, 100, 1, '2024-01-01', '2024-12-31'),
        (5, 'VIP Experience', 'EXPERIENCE', 5000, 200.0, 4, 10, 1, '2024-01-01', '2024-12-31'),
        (6, '20% Off Next Purchase', 'DISCOUNT', 2000, 20.0, 3, None, 1, '2024-01-01', '2024-12-31')
    ]
    conn.executemany("INSERT INTO rewards_catalog VALUES (?,?,?,?,?,?,?,?,?,?)", rewards_data)
    
    # Insert members
    print(f"Inserting {MEMBERS} loyalty members...")
    members_data = []
    
    for i in range(1, MEMBERS + 1):
        enrollment_date = (datetime.now() - timedelta(days=rng.randint(30, 1095))).strftime('%Y-%m-%d')
        lifetime_spend = rng.uniform(0, 20000)
        
        # Assign tier based on spend
        if lifetime_spend >= 15000:
            tier_id = 4
        elif lifetime_spend >= 5000:
            tier_id = 3
        elif lifetime_spend >= 1000:
            tier_id = 2
        else:
            tier_id = 1
        
        total_points = int(lifetime_spend * tiers_data[tier_id-1][6])  # Apply multiplier
        current_balance = rng.randint(0, total_points)
        status = rng.choices(['ACTIVE', 'INACTIVE'], weights=[0.85, 0.15])[0]
        
        members_data.append((
            i, f'customer_{i}', f'customer{i}@example.com', tier_id,
            enrollment_date, total_points, current_balance, lifetime_spend, status
        ))
    
    for chunk in batch(members_data, 1000):
        conn.executemany("INSERT INTO members VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert point transactions
    print("Inserting point transactions...")
    transactions_data = []
    transaction_id = 1
    
    for member_id in range(1, MEMBERS + 1):
        member = members_data[member_id - 1]
        enrollment_date = datetime.strptime(member[4], '%Y-%m-%d')
        
        num_transactions = rng.randint(5, POINT_TRANSACTIONS_PER_MEMBER)
        
        for _ in range(num_transactions):
            trans_date = enrollment_date + timedelta(days=rng.randint(0, (datetime.now() - enrollment_date).days))
            trans_type = rng.choices(['EARN', 'REDEEM', 'EXPIRE'], weights=[0.7, 0.25, 0.05])[0]
            
            if trans_type == 'EARN':
                points = rng.randint(10, 500)
                order_id = f'order_{transaction_id}'
                description = 'Points earned from purchase'
                expiry = (trans_date + timedelta(days=365)).strftime('%Y-%m-%d')
            elif trans_type == 'REDEEM':
                points = -rng.randint(100, 1000)
                order_id = f'order_{transaction_id}'
                description = 'Points redeemed for reward'
                expiry = None
            else:  # EXPIRE
                points = -rng.randint(50, 200)
                order_id = None
                description = 'Points expired'
                expiry = None
            
            transactions_data.append((
                transaction_id, member_id, trans_type, points,
                trans_date.strftime('%Y-%m-%d'), order_id, expiry, description
            ))
            transaction_id += 1
    
    for chunk in batch(transactions_data, 1000):
        conn.executemany("INSERT INTO point_transactions VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    # Insert redemptions
    print("Inserting redemptions...")
    redemptions_data = []
    redemption_id = 1
    
    for member_id in range(1, MEMBERS + 1):
        if rng.random() < 0.6:  # 60% of members have redemptions
            num_redemptions = rng.randint(1, REDEMPTIONS_PER_MEMBER)
            
            for _ in range(num_redemptions):
                reward_id = rng.randint(1, len(rewards_data))
                reward = rewards_data[reward_id - 1]
                points_cost = reward[3]
                
                redemption_date = (datetime.now() - timedelta(days=rng.randint(0, 365))).strftime('%Y-%m-%d')
                order_id = f'order_{redemption_id}' if rng.random() < 0.8 else None
                status = rng.choices(['PROCESSED', 'PENDING'], weights=[0.9, 0.1])[0]
                
                redemptions_data.append((
                    redemption_id, member_id, reward_id, redemption_date,
                    points_cost, order_id, status
                ))
                redemption_id += 1
    
    for chunk in batch(redemptions_data, 1000):
        conn.executemany("INSERT INTO redemptions VALUES (?,?,?,?,?,?,?)", chunk)
    
    # Insert tier movements
    print("Inserting tier movements...")
    movements_data = []
    movement_id = 1
    
    for member_id in range(1, MEMBERS + 1):
        if rng.random() < 0.3:  # 30% of members had tier changes
            current_tier = members_data[member_id - 1][3]
            
            # Create upgrade history
            if current_tier > 1:
                for tier in range(1, current_tier):
                    movement_date = (datetime.now() - timedelta(days=rng.randint(30, 700))).strftime('%Y-%m-%d')
                    movements_data.append((
                        movement_id, member_id, tier if tier > 1 else None,
                        tier + 1, movement_date, 'SPEND_THRESHOLD'
                    ))
                    movement_id += 1
    
    for chunk in batch(movements_data, 500):
        conn.executemany("INSERT INTO tier_movements VALUES (?,?,?,?,?,?)", chunk)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_members_tier ON members(tier_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_members_status ON members(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_point_transactions_member ON point_transactions(member_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_redemptions_member ON redemptions(member_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()