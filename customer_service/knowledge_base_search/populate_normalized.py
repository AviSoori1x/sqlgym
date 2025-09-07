#!/usr/bin/env python3
"""Populate knowledge base search normalized schema."""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
SCALE_ARTICLES=500
SCALE_VIEWS=20000

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--db',required=True); args=p.parse_args()
    conn=sqlite3.connect(args.db)
    conn.executescript(Path('schema_normalized.sql').read_text())
    # TODO populate
    conn.executescript('''
    CREATE INDEX idx_views_article_date ON article_views(article_id, viewed_at);
    CREATE INDEX idx_feedback_article ON feedback(article_id);
    ''')
    conn.commit(); conn.close()
if __name__=='__main__':
    main()
