#!/usr/bin/env python3
"""Populate Morgan Stanley Wealth Management denormalized analytics database."""
from __future__ import annotations

import argparse
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="Database file path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    # Connect to both normalized and denormalized databases
    norm_conn = sqlite3.connect(args.db.replace('_denormalized', '_normalized'))
    denorm_conn = sqlite3.connect(args.db)
    
    # Create denormalized schema
    with open('schema_denormalized.sql', 'r') as f:
        denorm_conn.executescript(f.read())
    
    print("Building client portfolio summary...")
    
    # Build client portfolio summary
    client_summary_data = []
    clients = norm_conn.execute("""
        SELECT c.id, c.client_code, c.first_name || ' ' || c.last_name as name,
               c.advisor_id, c.risk_tolerance, c.investment_objective,
               c.onboarding_date, c.net_worth
        FROM clients c
    """).fetchall()
    
    for client in clients:
        client_id, client_code, name, advisor_id, risk_tolerance, investment_objective, onboarding_date, net_worth = client
        
        # Get portfolio aggregates
        portfolio_stats = norm_conn.execute("""
            SELECT COUNT(*), COALESCE(SUM(current_value), 0)
            FROM portfolios WHERE client_id = ?
        """, (client_id,)).fetchone()
        
        total_portfolios, total_value = portfolio_stats
        total_value = total_value or 0
        
        # Calculate performance metrics (simplified)
        ytd_return = rng.uniform(-0.15, 0.25)
        ytd_benchmark = rng.uniform(-0.12, 0.20)
        ytd_excess = ytd_return - ytd_benchmark
        
        # Get unrealized gains
        unrealized_gain = norm_conn.execute("""
            SELECT COALESCE(SUM(unrealized_gain_loss), 0)
            FROM positions p
            JOIN portfolios pt ON p.portfolio_id = pt.id
            WHERE pt.client_id = ?
        """, (client_id,)).fetchone()[0] or 0
        
        # Asset allocation (simplified)
        equity_pct = rng.uniform(0.3, 0.8)
        fixed_income_pct = rng.uniform(0.1, 0.4)
        alternative_pct = rng.uniform(0.0, 0.2)
        cash_pct = max(0.01, 1.0 - equity_pct - fixed_income_pct - alternative_pct)
        
        client_summary_data.append((
            client_id, client_code, name, advisor_id, risk_tolerance, investment_objective,
            total_value, total_portfolios, onboarding_date, net_worth,
            ytd_return, ytd_benchmark, ytd_excess, unrealized_gain,
            equity_pct, fixed_income_pct, alternative_pct, cash_pct,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    # Insert client summary data
    for chunk in batch(client_summary_data, 1000):
        denorm_conn.executemany("""
            INSERT INTO client_portfolio_summary VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building portfolio performance analytics...")
    
    # Build portfolio performance analytics
    portfolio_analytics_data = []
    portfolios = norm_conn.execute("""
        SELECT p.id, p.client_id, p.portfolio_name, p.portfolio_type,
               p.inception_date, p.current_value, p.benchmark_index, p.status
        FROM portfolios p
    """).fetchall()
    
    for portfolio in portfolios:
        portfolio_id, client_id, name, portfolio_type, inception_date, current_value, benchmark_index, status = portfolio
        
        # Calculate performance metrics
        inception_return = rng.uniform(-0.2, 0.4)
        inception_benchmark = rng.uniform(-0.15, 0.35)
        inception_excess = inception_return - inception_benchmark
        
        one_year_return = rng.uniform(-0.3, 0.5) if rng.random() > 0.2 else None
        three_year_return = rng.uniform(-0.1, 0.3) if rng.random() > 0.5 else None
        five_year_return = rng.uniform(0.02, 0.25) if rng.random() > 0.7 else None
        
        sharpe_ratio = rng.uniform(0.2, 2.5)
        beta = rng.uniform(0.6, 1.4)
        alpha = rng.uniform(-0.05, 0.08)
        max_drawdown = -rng.uniform(0.05, 0.35)
        volatility = rng.uniform(0.08, 0.25)
        
        # Trade statistics
        total_trades = norm_conn.execute("""
            SELECT COUNT(*) FROM trades WHERE portfolio_id = ?
        """, (portfolio_id,)).fetchone()[0] or 0
        
        avg_trade_size = norm_conn.execute("""
            SELECT AVG(ABS(gross_amount)) FROM trades WHERE portfolio_id = ?
        """, (portfolio_id,)).fetchone()[0] or 0
        
        # Rebalancing dates
        last_rebalance = (datetime.now() - timedelta(days=rng.randint(30, 180))).strftime('%Y-%m-%d')
        next_rebalance = (datetime.now() + timedelta(days=rng.randint(30, 120))).strftime('%Y-%m-%d')
        
        portfolio_analytics_data.append((
            portfolio_id, client_id, name, portfolio_type, inception_date, current_value, benchmark_index,
            inception_return, inception_benchmark, inception_excess,
            one_year_return, three_year_return, five_year_return,
            sharpe_ratio, beta, alpha, max_drawdown, volatility,
            total_trades, avg_trade_size, last_rebalance, next_rebalance, status
        ))
    
    # Insert portfolio analytics data
    for chunk in batch(portfolio_analytics_data, 1000):
        denorm_conn.executemany("""
            INSERT INTO portfolio_performance_analytics VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building security holdings analysis...")
    
    # Build security holdings analysis
    security_analysis_data = []
    securities = norm_conn.execute("""
        SELECT s.id, s.symbol, s.security_name, s.asset_class, s.security_type, s.sector
        FROM securities s
    """).fetchall()
    
    for security in securities:
        security_id, symbol, security_name, asset_class, security_type, sector = security
        
        # Aggregate holdings data
        holdings_stats = norm_conn.execute("""
            SELECT COALESCE(SUM(market_value), 0), COALESCE(SUM(quantity), 0),
                   COALESCE(AVG(average_cost), 0), COALESCE(AVG(current_price), 0),
                   COALESCE(SUM(unrealized_gain_loss), 0), COUNT(DISTINCT portfolio_id),
                   COALESCE(MAX(market_value), 0), COALESCE(MIN(market_value), 0)
            FROM positions WHERE security_id = ?
        """, (security_id,)).fetchone()
        
        if holdings_stats[0] == 0:  # No holdings for this security
            continue
            
        total_market_value, total_quantity, avg_cost, current_price, total_unrealized, portfolios_count, max_position, min_position = holdings_stats
        
        unrealized_pct = (total_unrealized / (total_market_value - total_unrealized)) * 100 if total_market_value > total_unrealized else 0
        
        # Calculate weight in total AUM (simplified)
        total_aum = norm_conn.execute("SELECT SUM(current_value) FROM portfolios").fetchone()[0] or 1
        weight_in_aum = (total_market_value / total_aum) * 100
        
        # Last trade date
        last_trade = norm_conn.execute("""
            SELECT MAX(trade_date) FROM trades WHERE security_id = ?
        """, (security_id,)).fetchone()[0]
        
        # Price metrics (simulated)
        price_52w_high = current_price * rng.uniform(1.0, 1.8)
        price_52w_low = current_price * rng.uniform(0.5, 1.0)
        ytd_performance = rng.uniform(-0.4, 0.6)
        
        security_analysis_data.append((
            security_id, symbol, security_name, asset_class, security_type, sector,
            total_market_value, total_quantity, avg_cost, current_price,
            total_unrealized, unrealized_pct, portfolios_count,
            max_position, min_position, weight_in_aum,
            last_trade, price_52w_high, price_52w_low, ytd_performance
        ))
    
    # Insert security analysis data
    for chunk in batch(security_analysis_data, 1000):
        denorm_conn.executemany("""
            INSERT INTO security_holdings_analysis VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    print("Building daily AUM flows...")
    
    # Build daily AUM flows (last 90 days)
    daily_flows_data = []
    base_aum = total_aum
    
    for i in range(90):
        business_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Simulate daily metrics
        daily_aum = base_aum * rng.uniform(0.95, 1.05)
        net_flows = rng.uniform(-1000000, 2000000)
        market_appreciation = rng.uniform(-500000, 1500000)
        new_client_assets = rng.uniform(0, 500000)
        client_departures = rng.uniform(0, 300000)
        dividend_income = rng.uniform(0, 100000)
        interest_income = rng.uniform(0, 50000)
        fees_generated = daily_aum * 0.01 / 365  # 1% annual fee
        
        active_clients = len(clients)
        active_portfolios = len(portfolios)
        daily_trades = rng.randint(50, 200)
        trade_volume = rng.uniform(1000000, 10000000)
        
        daily_flows_data.append((
            business_date, daily_aum, net_flows, market_appreciation,
            new_client_assets, client_departures, dividend_income, interest_income,
            fees_generated, active_clients, active_portfolios, daily_trades, trade_volume
        ))
    
    # Insert daily flows data
    for chunk in batch(daily_flows_data, 1000):
        denorm_conn.executemany("""
            INSERT INTO daily_aum_flows VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, chunk)
    
    # Create indexes
    print("Creating indexes...")
    denorm_conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_client_summary_advisor ON client_portfolio_summary(advisor_id);
        CREATE INDEX IF NOT EXISTS idx_client_summary_risk ON client_portfolio_summary(risk_tolerance);
        CREATE INDEX IF NOT EXISTS idx_portfolio_analytics_client ON portfolio_performance_analytics(client_id);
        CREATE INDEX IF NOT EXISTS idx_portfolio_analytics_type ON portfolio_performance_analytics(portfolio_type);
        CREATE INDEX IF NOT EXISTS idx_security_analysis_class ON security_holdings_analysis(asset_class);
        CREATE INDEX IF NOT EXISTS idx_security_analysis_sector ON security_holdings_analysis(sector);
        CREATE INDEX IF NOT EXISTS idx_daily_aum_date ON daily_aum_flows(business_date);
    """)
    
    denorm_conn.commit()
    denorm_conn.close()
    norm_conn.close()
    
    print("Done!")

if __name__ == "__main__":
    main()
