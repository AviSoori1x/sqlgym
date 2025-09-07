#!/usr/bin/env python3
"""Populate digital ads attribution denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import batch

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized-db", required=True)
    parser.add_argument("--denormalized-db", required=True)
    args = parser.parse_args()
    
    norm_conn = sqlite3.connect(args.normalized_db)
    norm_conn.row_factory = sqlite3.Row
    denorm_conn = sqlite3.connect(args.denormalized_db)
    
    print("Building campaign performance metrics...")
    performance_query = """
    SELECT 
        c.id as campaign_id,
        DATE(t.timestamp) as date,
        c.platform,
        COUNT(CASE WHEN t.interaction_type = 'IMPRESSION' THEN 1 END) as impressions,
        COUNT(CASE WHEN t.interaction_type = 'CLICK' THEN 1 END) as clicks,
        COUNT(CASE WHEN t.interaction_type = 'CONVERSION' THEN 1 END) as conversions,
        SUM(t.cost) as spend,
        SUM(t.revenue) as revenue
    FROM campaigns c
    LEFT JOIN touchpoints t ON c.id = t.campaign_id
    WHERE t.timestamp IS NOT NULL
    GROUP BY c.id, DATE(t.timestamp)
    """
    
    performance_data = []
    for row in norm_conn.execute(performance_query):
        impressions = row['impressions'] or 0
        clicks = row['clicks'] or 0
        conversions = row['conversions'] or 0
        spend = row['spend'] or 0
        revenue = row['revenue'] or 0
        
        ctr = clicks / impressions if impressions > 0 else 0
        conv_rate = conversions / clicks if clicks > 0 else 0
        cpc = spend / clicks if clicks > 0 else 0
        cpa = spend / conversions if conversions > 0 else 0
        roas = revenue / spend if spend > 0 else 0
        
        performance_data.append((
            row['campaign_id'], row['date'], row['platform'],
            impressions, clicks, conversions, spend, revenue,
            ctr, conv_rate, cpc, cpa, roas
        ))
    
    denorm_conn.executemany("""
        INSERT INTO campaign_performance VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, performance_data)
    
    print("Building attribution analysis...")
    attribution_query = """
    SELECT 
        c.id as conversion_id,
        c.user_id,
        c.conversion_timestamp,
        c.conversion_value,
        MIN(t.campaign_id) as first_touch_campaign,
        MAX(t.campaign_id) as last_touch_campaign,
        COUNT(t.id) as touchpoint_count,
        (julianday(c.conversion_timestamp) - julianday(MIN(t.timestamp))) * 24 as journey_hours
    FROM conversions c
    LEFT JOIN touchpoints t ON c.user_id = t.user_id 
        AND t.timestamp <= c.conversion_timestamp
        AND julianday(c.conversion_timestamp) - julianday(t.timestamp) <= c.attribution_window_hours / 24.0
    GROUP BY c.id
    """
    
    attribution_data = []
    for row in norm_conn.execute(attribution_query):
        touchpoints = row['touchpoint_count'] or 0
        platforms = ['GOOGLE_ADS', 'FACEBOOK']  # Simplified
        
        # Calculate attribution values
        linear_value = row['conversion_value'] / max(touchpoints, 1)
        time_decay_value = row['conversion_value'] * 0.6  # Simplified
        position_value = row['conversion_value'] * 0.4  # Simplified
        
        attribution_data.append((
            row['conversion_id'], row['user_id'], row['conversion_timestamp'],
            row['conversion_value'], row['first_touch_campaign'], row['last_touch_campaign'],
            touchpoints, int(row['journey_hours'] or 0), json.dumps(platforms),
            linear_value, time_decay_value, position_value
        ))
    
    denorm_conn.executemany("""
        INSERT INTO attribution_analysis VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?)
    """, attribution_data)
    
    print("Building user journey summaries...")
    journey_query = """
    SELECT 
        t.user_id,
        MIN(t.timestamp) as first_touch,
        MAX(t.timestamp) as last_touch,
        COUNT(t.id) as total_touchpoints,
        COUNT(DISTINCT t.campaign_id) as unique_campaigns,
        COUNT(DISTINCT t.platform) as unique_platforms,
        COUNT(DISTINCT c.id) as total_conversions,
        SUM(c.conversion_value) as total_value
    FROM touchpoints t
    LEFT JOIN conversions c ON t.user_id = c.user_id
    GROUP BY t.user_id
    """
    
    journey_data = []
    for row in norm_conn.execute(journey_query):
        first_touch = row['first_touch']
        last_touch = row['last_touch']
        
        if first_touch and last_touch:
            duration = (datetime.fromisoformat(last_touch.replace(' ', 'T')) - 
                       datetime.fromisoformat(first_touch.replace(' ', 'T'))).days
        else:
            duration = 0
        
        journey_data.append((
            row['user_id'], first_touch, last_touch,
            row['total_touchpoints'] or 0, row['unique_campaigns'] or 0,
            row['unique_platforms'] or 0, row['total_conversions'] or 0,
            row['total_value'] or 0, duration, 'GOOGLE_ADS', 'GOOGLE_ADS->FACEBOOK->CONVERSION'
        ))
    
    denorm_conn.executemany("""
        INSERT INTO user_journey_summary VALUES 
        (?,?,?,?,?,?,?,?,?,?,?)
    """, journey_data)
    
    print("Building cross-platform attribution...")
    cross_platform_query = """
    SELECT 
        DATE(c.conversion_timestamp) as date,
        'GOOGLE_ADS,FACEBOOK' as platform_combo,
        COUNT(DISTINCT c.id) as assisted_conversions,
        COUNT(DISTINCT c.id) as direct_conversions,
        SUM(c.conversion_value) as total_value,
        AVG(3.5) as avg_journey_length
    FROM conversions c
    GROUP BY DATE(c.conversion_timestamp)
    """
    
    cross_platform_data = []
    for row in norm_conn.execute(cross_platform_query):
        cross_platform_data.append(tuple(row))
    
    denorm_conn.executemany("""
        INSERT INTO cross_platform_attribution VALUES 
        (?,?,?,?,?,?)
    """, cross_platform_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_campaign_performance_date ON campaign_performance(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_campaign_performance_platform ON campaign_performance(platform)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_attribution_user ON attribution_analysis(user_id)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_journey_summary_platform ON user_journey_summary(primary_platform)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()