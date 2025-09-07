#!/usr/bin/env python3
"""Populate CSAT/NPS denormalized schema with analytical data."""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import batch

def determine_sentiment(comment):
    """Simple sentiment analysis based on keywords."""
    if not comment:
        return None
    comment_lower = comment.lower()
    positive_words = ['great', 'excellent', 'satisfied', 'recommend', 'helpful', 'quick', 'easy']
    negative_words = ['disappointed', 'poor', 'complicated', 'wait', 'improve', 'expected']
    
    pos_count = sum(1 for word in positive_words if word in comment_lower)
    neg_count = sum(1 for word in negative_words if word in comment_lower)
    
    if pos_count > neg_count:
        return 'POSITIVE'
    elif neg_count > pos_count:
        return 'NEGATIVE'
    else:
        return 'NEUTRAL'

def get_score_category(score, survey_type):
    """Categorize score based on survey type."""
    if not score:
        return None
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

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized-db", required=True)
    parser.add_argument("--denormalized-db", required=True)
    args = parser.parse_args()
    
    # Connect to both databases
    norm_conn = sqlite3.connect(args.normalized_db)
    norm_conn.row_factory = sqlite3.Row
    denorm_conn = sqlite3.connect(args.denormalized_db)
    
    print("Building survey analytics...")
    # Build survey_analytics table
    analytics_query = """
    SELECT 
        s.id as survey_id,
        c.email as customer_email,
        c.segment as customer_segment,
        t.name as touchpoint_name,
        t.channel,
        s.survey_type,
        s.sent_at,
        s.responded_at,
        CASE 
            WHEN s.responded_at IS NOT NULL THEN 
                CAST((julianday(s.responded_at) - julianday(s.sent_at)) * 24 AS INTEGER)
            ELSE NULL 
        END as response_time_hours,
        s.score,
        s.comment,
        st.trigger_event,
        f.action_type as follow_up_action,
        f.outcome as follow_up_outcome
    FROM surveys s
    JOIN customers c ON s.customer_id = c.id
    JOIN touchpoints t ON s.touchpoint_id = t.id
    LEFT JOIN survey_triggers st ON s.id = st.survey_id
    LEFT JOIN follow_ups f ON s.id = f.survey_id
    """
    
    analytics_data = []
    for row in norm_conn.execute(analytics_query):
        score_category = get_score_category(row['score'], row['survey_type'])
        comment_sentiment = determine_sentiment(row['comment'])
        
        analytics_data.append((
            row['survey_id'],
            row['customer_email'],
            row['customer_segment'],
            row['touchpoint_name'],
            row['channel'],
            row['survey_type'],
            row['sent_at'],
            row['responded_at'],
            row['response_time_hours'],
            row['score'],
            score_category,
            row['comment'],
            comment_sentiment,
            row['trigger_event'],
            row['follow_up_action'],
            row['follow_up_outcome']
        ))
    
    # Insert in batches
    for chunk in batch(analytics_data, 1000):
        denorm_conn.executemany("""
            INSERT INTO survey_analytics VALUES 
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building daily metrics...")
    # Build daily_metrics
    daily_query = """
    SELECT 
        DATE(s.sent_at) as date,
        s.survey_type,
        COUNT(*) as total_sent,
        COUNT(CASE WHEN s.responded_at IS NOT NULL THEN 1 END) as total_responses,
        CAST(COUNT(CASE WHEN s.responded_at IS NOT NULL THEN 1 END) AS REAL) / COUNT(*) as response_rate,
        AVG(s.score) as avg_score
    FROM surveys s
    GROUP BY DATE(s.sent_at), s.survey_type
    """
    
    daily_data = []
    for row in norm_conn.execute(daily_query):
        # Calculate NPS score if applicable
        nps_score = None
        csat_percentage = None
        
        if row['survey_type'] == 'NPS' and row['avg_score']:
            # Get promoters and detractors for NPS calculation
            nps_query = """
            SELECT 
                COUNT(CASE WHEN score >= 9 THEN 1 END) as promoters,
                COUNT(CASE WHEN score <= 6 THEN 1 END) as detractors,
                COUNT(CASE WHEN score IS NOT NULL THEN 1 END) as total
            FROM surveys
            WHERE DATE(sent_at) = ? AND survey_type = 'NPS'
            """
            nps_row = norm_conn.execute(nps_query, (row['date'],)).fetchone()
            if nps_row['total'] > 0:
                nps_score = int(((nps_row['promoters'] - nps_row['detractors']) / nps_row['total']) * 100)
        
        elif row['survey_type'] == 'CSAT' and row['avg_score']:
            # Calculate satisfaction percentage for CSAT
            csat_query = """
            SELECT 
                COUNT(CASE WHEN score >= 8 THEN 1 END) as satisfied,
                COUNT(CASE WHEN score IS NOT NULL THEN 1 END) as total
            FROM surveys
            WHERE DATE(sent_at) = ? AND survey_type = 'CSAT'
            """
            csat_row = norm_conn.execute(csat_query, (row['date'],)).fetchone()
            if csat_row['total'] > 0:
                csat_percentage = (csat_row['satisfied'] / csat_row['total']) * 100
        
        daily_data.append((
            row['date'],
            row['survey_type'],
            row['total_sent'],
            row['total_responses'],
            row['response_rate'],
            row['avg_score'],
            nps_score,
            csat_percentage
        ))
    
    denorm_conn.executemany("""
        INSERT INTO daily_metrics VALUES 
        (?,?,?,?,?,?,?,?)
    """, daily_data)
    
    print("Building segment scores...")
    # Build segment_scores
    segment_query = """
    SELECT 
        c.segment,
        s.survey_type,
        strftime('%Y-%m', s.sent_at) as month,
        COUNT(*) as total_surveys,
        COUNT(CASE WHEN s.responded_at IS NOT NULL THEN 1 END) as responses,
        AVG(s.score) as avg_score
    FROM surveys s
    JOIN customers c ON s.customer_id = c.id
    GROUP BY c.segment, s.survey_type, strftime('%Y-%m', s.sent_at)
    """
    
    segment_data = []
    prev_scores = {}  # Track previous month scores for trends
    
    for row in norm_conn.execute(segment_query):
        key = (row['segment'], row['survey_type'])
        score_trend = None
        
        if key in prev_scores and row['avg_score']:
            score_trend = row['avg_score'] - prev_scores[key]
        
        if row['avg_score']:
            prev_scores[key] = row['avg_score']
        
        # Get top drivers (simplified - in real world would use text analytics)
        drivers_query = """
        SELECT 
            st.trigger_event,
            AVG(s.score) as avg_score,
            COUNT(*) as count
        FROM surveys s
        JOIN customers c ON s.customer_id = c.id
        JOIN survey_triggers st ON s.id = st.survey_id
        WHERE c.segment = ? AND s.survey_type = ? AND strftime('%Y-%m', s.sent_at) = ?
            AND s.score IS NOT NULL
        GROUP BY st.trigger_event
        ORDER BY avg_score DESC
        """
        
        drivers = list(norm_conn.execute(drivers_query, (row['segment'], row['survey_type'], row['month'])))
        top_positive = drivers[0]['trigger_event'] if drivers and drivers[0]['avg_score'] >= 7 else None
        top_negative = drivers[-1]['trigger_event'] if drivers and drivers[-1]['avg_score'] < 7 else None
        
        segment_data.append((
            row['segment'],
            row['survey_type'],
            row['month'],
            row['total_surveys'],
            row['responses'],
            row['avg_score'],
            score_trend,
            top_positive,
            top_negative
        ))
    
    denorm_conn.executemany("""
        INSERT INTO segment_scores VALUES 
        (?,?,?,?,?,?,?,?,?)
    """, segment_data)
    
    print("Building touchpoint performance...")
    # Build touchpoint_performance
    touchpoint_query = """
    SELECT 
        t.name as touchpoint_name,
        printf('%04d-Q%d', 
            CAST(strftime('%Y', s.sent_at) AS INTEGER),
            (CAST(strftime('%m', s.sent_at) AS INTEGER) - 1) / 3 + 1
        ) as quarter,
        COUNT(*) as total_surveys,
        AVG(CASE WHEN s.survey_type = 'CSAT' THEN s.score END) as avg_csat,
        AVG(CASE WHEN s.survey_type = 'NPS' THEN s.score END) as avg_nps,
        CAST(COUNT(CASE WHEN s.responded_at IS NOT NULL THEN 1 END) AS REAL) / COUNT(*) as response_rate,
        CAST(COUNT(DISTINCT f.survey_id) AS REAL) / COUNT(*) as follow_up_rate,
        CAST(COUNT(CASE WHEN f.outcome = 'RESOLVED' THEN 1 END) AS REAL) / 
            NULLIF(COUNT(DISTINCT f.survey_id), 0) as issue_resolution_rate
    FROM surveys s
    JOIN touchpoints t ON s.touchpoint_id = t.id
    LEFT JOIN follow_ups f ON s.id = f.survey_id
    GROUP BY t.name, quarter
    """
    
    touchpoint_data = []
    for row in norm_conn.execute(touchpoint_query):
        touchpoint_data.append(tuple(row))
    
    denorm_conn.executemany("""
        INSERT INTO touchpoint_performance VALUES 
        (?,?,?,?,?,?,?,?)
    """, touchpoint_data)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_survey_analytics_date ON survey_analytics(sent_at)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_survey_analytics_type ON survey_analytics(survey_type)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_survey_analytics_segment ON survey_analytics(customer_segment)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date)")
    denorm_conn.execute("CREATE INDEX IF NOT EXISTS idx_segment_scores_month ON segment_scores(month)")
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    print("Done!")

if __name__ == "__main__":
    main()