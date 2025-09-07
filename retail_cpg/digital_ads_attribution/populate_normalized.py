#!/usr/bin/env python3
"""Populate digital ads attribution normalized schema with synthetic data."""
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
CAMPAIGNS = 50
AD_GROUPS_PER_CAMPAIGN = 4
ADS_PER_AD_GROUP = 3
USERS = 10000
TOUCHPOINTS_PER_USER = 8
CONVERSION_RATE = 0.05

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert campaigns
    print(f"Inserting {CAMPAIGNS} campaigns...")
    campaigns_data = []
    platforms = ['GOOGLE_ADS', 'FACEBOOK', 'INSTAGRAM', 'TWITTER', 'AMAZON']
    campaign_types = ['SEARCH', 'DISPLAY', 'VIDEO', 'SHOPPING', 'SOCIAL']
    objectives = ['AWARENESS', 'TRAFFIC', 'ENGAGEMENT', 'SALES']
    
    for i in range(1, CAMPAIGNS + 1):
        platform = rng.choice(platforms)
        camp_type = rng.choice(campaign_types)
        objective = rng.choice(objectives)
        
        start_date = (datetime.now() - timedelta(days=rng.randint(30, 180))).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=rng.randint(30, 90))).strftime('%Y-%m-%d')
        budget = rng.uniform(1000, 50000)
        status = rng.choices(['ACTIVE', 'PAUSED', 'COMPLETED'], weights=[0.6, 0.3, 0.1])[0]
        
        campaigns_data.append((
            i, f'Campaign_{i}_{platform}', platform, camp_type, objective,
            start_date, end_date, round(budget, 2), status
        ))
    
    conn.executemany("INSERT INTO campaigns VALUES (?,?,?,?,?,?,?,?,?)", campaigns_data)
    
    # Insert ad groups
    print("Inserting ad groups...")
    ad_groups_data = []
    ad_group_id = 1
    
    for campaign_id in range(1, CAMPAIGNS + 1):
        for j in range(AD_GROUPS_PER_CAMPAIGN):
            targeting = {'age': [25, 45], 'interests': ['shopping', 'technology']}
            bid_strategy = rng.choice(['CPC', 'CPM', 'CPA', 'ROAS'])
            max_bid = rng.uniform(0.5, 5.0)
            
            ad_groups_data.append((
                ad_group_id, campaign_id, f'AdGroup_{ad_group_id}',
                json.dumps(targeting), bid_strategy, round(max_bid, 2), 'ACTIVE'
            ))
            ad_group_id += 1
    
    conn.executemany("INSERT INTO ad_groups VALUES (?,?,?,?,?,?,?)", ad_groups_data)
    
    # Insert ads
    print("Inserting ads...")
    ads_data = []
    ad_id = 1
    
    for ag_id in range(1, len(ad_groups_data) + 1):
        for k in range(ADS_PER_AD_GROUP):
            ad_type = rng.choice(['TEXT', 'IMAGE', 'VIDEO', 'CAROUSEL'])
            cta = rng.choice(['LEARN_MORE', 'SHOP_NOW', 'SIGN_UP'])
            
            ads_data.append((
                ad_id, ag_id, f'creative_{ad_id}', ad_type,
                f'Headline {ad_id}', f'Description for ad {ad_id}',
                cta, f'https://example.com/landing/{ad_id}', 'ACTIVE'
            ))
            ad_id += 1
    
    conn.executemany("INSERT INTO ads VALUES (?,?,?,?,?,?,?,?,?)", ads_data)
    
    # Insert touchpoints
    print("Inserting touchpoints...")
    touchpoints_data = []
    touchpoint_id = 1
    
    for user_id in range(1, USERS + 1):
        num_touchpoints = rng.randint(1, TOUCHPOINTS_PER_USER)
        session_id = f'session_{user_id}_{rng.randint(1000, 9999)}'
        
        for _ in range(num_touchpoints):
            timestamp = (datetime.now() - timedelta(days=rng.randint(0, 60))).strftime('%Y-%m-%d %H:%M:%S')
            platform = rng.choice(platforms + ['ORGANIC'])
            
            if platform != 'ORGANIC':
                campaign_id = rng.randint(1, CAMPAIGNS)
                ad_group_id = rng.randint(1, len(ad_groups_data))
                ad_id = rng.randint(1, len(ads_data))
            else:
                campaign_id = None
                ad_group_id = None
                ad_id = None
            
            interaction = rng.choices(['IMPRESSION', 'CLICK', 'VIEW'], weights=[0.7, 0.25, 0.05])[0]
            cost = rng.uniform(0.1, 2.0) if interaction == 'CLICK' else 0
            
            touchpoints_data.append((
                touchpoint_id, f'user_{user_id}', session_id, timestamp,
                platform, campaign_id, ad_group_id, ad_id, interaction,
                round(cost, 2), 0
            ))
            touchpoint_id += 1
    
    for chunk in batch(touchpoints_data, 1000):
        conn.executemany("INSERT INTO touchpoints VALUES (?,?,?,?,?,?,?,?,?,?,?)", chunk)
    
    # Insert conversions
    print("Inserting conversions...")
    conversions_data = []
    conversion_id = 1
    
    # Select users who will convert
    converting_users = rng.sample(range(1, USERS + 1), int(USERS * CONVERSION_RATE))
    
    for user_id in converting_users:
        num_conversions = rng.randint(1, 3)
        
        for _ in range(num_conversions):
            conv_timestamp = (datetime.now() - timedelta(days=rng.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
            conv_type = rng.choices(['PURCHASE', 'SIGNUP', 'LEAD'], weights=[0.6, 0.3, 0.1])[0]
            
            if conv_type == 'PURCHASE':
                conv_value = rng.uniform(50, 500)
                order_id = f'order_{conversion_id}'
            else:
                conv_value = rng.uniform(10, 100)
                order_id = None
            
            conversions_data.append((
                conversion_id, f'user_{user_id}', conv_timestamp, conv_type,
                round(conv_value, 2), order_id, 168
            ))
            conversion_id += 1
    
    conn.executemany("INSERT INTO conversions VALUES (?,?,?,?,?,?,?)", conversions_data)
    
    # Insert attribution models
    print("Inserting attribution models...")
    models_data = [
        (1, 'First Touch', 'FIRST_TOUCH', '{}', 1),
        (2, 'Last Touch', 'LAST_TOUCH', '{}', 1),
        (3, 'Linear', 'LINEAR', '{}', 1),
        (4, 'Time Decay', 'TIME_DECAY', '{"decay_rate": 0.5}', 1),
        (5, 'Position Based', 'POSITION_BASED', '{"first_touch_weight": 0.4, "last_touch_weight": 0.4}', 1)
    ]
    
    conn.executemany("INSERT INTO attribution_models VALUES (?,?,?,?,?)", models_data)
    
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_platform ON campaigns(platform)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_touchpoints_user ON touchpoints(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_touchpoints_timestamp ON touchpoints(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversions_user ON conversions(user_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()