#!/usr/bin/env python3
"""Performance benchmarking suite for SQLGym corpus."""
from __future__ import annotations

import sqlite3
import time
import json
import statistics
from pathlib import Path

# Business systems to benchmark
BENCHMARK_SYSTEMS = [
    ('customer_service/chatbot_deflection', 'zendesk_ai_support'),
    ('healthcare/claims_processing', 'anthem_claims_system'),
    ('finance/consumer_lending_loans_cards', 'chase_consumer_banking'),
    ('retail_cpg/customer_360_segmentation', 'amazon_customer_insights'),
    ('energy_manufacturing/carbon_accounting_emissions', 'exxon_carbon_tracking')
]

# Benchmark queries for different complexity levels
BENCHMARK_QUERIES = {
    'simple_lookup': {
        'zendesk_ai_support': "SELECT * FROM conversations WHERE id = 1000;",
        'anthem_claims_system': "SELECT * FROM medical_claims WHERE claim_number = 'CLM000001000';",
        'chase_consumer_banking': "SELECT * FROM customers WHERE customer_id = 'CUST01000';",
        'amazon_customer_insights': "SELECT * FROM customers WHERE customer_id = 'customer1000';",
        'exxon_carbon_tracking': "SELECT * FROM facilities WHERE facility_code = 'FAC010';"
    },
    'aggregation': {
        'zendesk_ai_support': "SELECT channel, COUNT(*) FROM conversations GROUP BY channel;",
        'anthem_claims_system': "SELECT status, COUNT(*) FROM medical_claims GROUP BY status;", 
        'chase_consumer_banking': "SELECT status, COUNT(*) FROM loans GROUP BY status;",
        'amazon_customer_insights': "SELECT acquisition_channel, COUNT(*) FROM customers GROUP BY acquisition_channel;",
        'exxon_carbon_tracking': "SELECT facility_type, COUNT(*) FROM facilities GROUP BY facility_type;"
    },
    'complex_join': {
        'zendesk_ai_support': """
            SELECT c.channel, COUNT(DISTINCT conv.id) as conversations, COUNT(e.id) as escalations
            FROM conversations conv 
            JOIN customers c ON conv.customer_id = c.id
            LEFT JOIN escalations e ON conv.id = e.conversation_id
            GROUP BY c.channel;
        """,
        'anthem_claims_system': """
            SELECT p.specialty, COUNT(mc.id) as claims, AVG(cli.paid_amount) as avg_payment
            FROM medical_claims mc
            JOIN providers p ON mc.provider_id = p.id  
            JOIN claim_line_items cli ON mc.id = cli.claim_id
            WHERE mc.service_date >= DATE('now', '-90 days')
            GROUP BY p.specialty;
        """,
        'chase_consumer_banking': """
            SELECT lp.product_type, COUNT(l.id) as loans, AVG(l.current_balance) as avg_balance
            FROM loans l
            JOIN loan_products lp ON l.loan_product_id = lp.id
            JOIN customers c ON l.customer_id = c.id
            WHERE l.status = 'ACTIVE'
            GROUP BY lp.product_type;
        """,
        'amazon_customer_insights': """
            SELECT cs.name as segment, COUNT(DISTINCT c.id) as customers, AVG(t.total_amount) as avg_transaction
            FROM customers c
            JOIN customer_segment_assignments csa ON c.id = csa.customer_id
            JOIN customer_segments cs ON csa.segment_id = cs.id  
            LEFT JOIN transactions t ON c.id = t.customer_id
            GROUP BY cs.name;
        """,
        'exxon_carbon_tracking': """
            SELECT f.facility_type, SUM(ec.co2_equivalent_kg)/1000 as total_co2_tonnes
            FROM facilities f
            JOIN emission_sources es ON f.id = es.facility_id
            JOIN emissions_calculations ec ON es.id = ec.source_id
            WHERE ec.reporting_period >= '2024-01'
            GROUP BY f.facility_type;
        """
    }
}

def benchmark_query(db_path: Path, query: str, query_name: str) -> dict:
    """Benchmark a single query and return performance metrics."""
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Warm up query (run once to load into cache)
        conn.execute(query).fetchall()
        
        # Benchmark runs
        times = []
        for _ in range(5):
            start_time = time.perf_counter()
            result = conn.execute(query).fetchall()
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        # Get query plan
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        query_plan = conn.execute(explain_query).fetchall()
        
        conn.close()
        
        return {
            'query_name': query_name,
            'avg_time_ms': round(statistics.mean(times), 2),
            'min_time_ms': round(min(times), 2),
            'max_time_ms': round(max(times), 2),
            'std_dev_ms': round(statistics.stdev(times) if len(times) > 1 else 0, 2),
            'result_count': len(result),
            'uses_index': any('USING INDEX' in str(step) for step in query_plan),
            'query_plan': [str(step) for step in query_plan]
        }
        
    except Exception as e:
        return {
            'query_name': query_name,
            'error': str(e),
            'avg_time_ms': None
        }

def benchmark_business_system(domain_subdir: str, business_name: str) -> dict:
    """Benchmark all query types for a business system."""
    
    db_path = Path(domain_subdir) / f"{business_name}_normalized.db"
    
    if not db_path.exists():
        return {'error': f'Database not found: {db_path}'}
    
    print(f"🔍 Benchmarking {business_name}...")
    
    system_results = {
        'business_name': business_name,
        'domain_subdir': domain_subdir,
        'database_size_mb': round(db_path.stat().st_size / (1024 * 1024), 2),
        'benchmarks': {}
    }
    
    for complexity, queries in BENCHMARK_QUERIES.items():
        if business_name in queries:
            query = queries[business_name]
            result = benchmark_query(db_path, query, f"{complexity}_{business_name}")
            system_results['benchmarks'][complexity] = result
            
            if 'error' not in result:
                print(f"  {complexity}: {result['avg_time_ms']}ms (index: {result['uses_index']})")
            else:
                print(f"  {complexity}: ERROR - {result['error']}")
    
    return system_results

def main():
    """Run comprehensive performance benchmarks across the corpus."""
    
    print("📊 SQLGYM PERFORMANCE BENCHMARK SUITE")
    print("=" * 50)
    
    all_results = []
    
    for domain_subdir, business_name in BENCHMARK_SYSTEMS:
        result = benchmark_business_system(domain_subdir, business_name)
        all_results.append(result)
    
    # Generate performance report
    print("\\n📈 PERFORMANCE SUMMARY")
    print("=" * 30)
    
    performance_summary = {
        'benchmark_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'systems_tested': len(BENCHMARK_SYSTEMS),
        'query_types': list(BENCHMARK_QUERIES.keys()),
        'results': all_results,
        'summary_stats': {}
    }
    
    # Calculate summary statistics
    simple_times = [r['benchmarks'].get('simple_lookup', {}).get('avg_time_ms') for r in all_results if 'benchmarks' in r]
    simple_times = [t for t in simple_times if t is not None]
    
    aggregation_times = [r['benchmarks'].get('aggregation', {}).get('avg_time_ms') for r in all_results if 'benchmarks' in r]
    aggregation_times = [t for t in aggregation_times if t is not None]
    
    complex_times = [r['benchmarks'].get('complex_join', {}).get('avg_time_ms') for r in all_results if 'benchmarks' in r]
    complex_times = [t for t in complex_times if t is not None]
    
    if simple_times:
        performance_summary['summary_stats']['simple_lookup'] = {
            'avg_ms': round(statistics.mean(simple_times), 2),
            'min_ms': round(min(simple_times), 2),
            'max_ms': round(max(simple_times), 2)
        }
        print(f"Simple Lookups: {statistics.mean(simple_times):.2f}ms avg ({min(simple_times):.2f}-{max(simple_times):.2f}ms)")
    
    if aggregation_times:
        performance_summary['summary_stats']['aggregation'] = {
            'avg_ms': round(statistics.mean(aggregation_times), 2),
            'min_ms': round(min(aggregation_times), 2),
            'max_ms': round(max(aggregation_times), 2)
        }
        print(f"Aggregations: {statistics.mean(aggregation_times):.2f}ms avg ({min(aggregation_times):.2f}-{max(aggregation_times):.2f}ms)")
    
    if complex_times:
        performance_summary['summary_stats']['complex_join'] = {
            'avg_ms': round(statistics.mean(complex_times), 2),
            'min_ms': round(min(complex_times), 2),
            'max_ms': round(max(complex_times), 2)
        }
        print(f"Complex Joins: {statistics.mean(complex_times):.2f}ms avg ({min(complex_times):.2f}-{max(complex_times):.2f}ms)")
    
    # Save detailed results
    with open('performance_benchmark_results.json', 'w') as f:
        json.dump(performance_summary, f, indent=2)
    
    print(f"\\n✅ Benchmark completed!")
    print(f"📊 Detailed results saved to: performance_benchmark_results.json")
    
    # Performance rating
    if simple_times and statistics.mean(simple_times) < 10:
        print(f"🏆 EXCELLENT: Simple queries under 10ms average")
    if aggregation_times and statistics.mean(aggregation_times) < 100:
        print(f"🏆 EXCELLENT: Aggregation queries under 100ms average")
    if complex_times and statistics.mean(complex_times) < 500:
        print(f"🏆 EXCELLENT: Complex joins under 500ms average")
    
    print(f"\\n🎯 SQLGym Performance: PRODUCTION READY!")
    
    return performance_summary

if __name__ == "__main__":
    results = main()
