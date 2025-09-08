#!/usr/bin/env python3
"""Execute data type audit across all schemas."""

import sqlite3
import os
import json
from collections import defaultdict, Counter

def main():
    print("🔍 DATA TYPE DIVERSITY AUDIT")
    print("=" * 50)
    
    # Analyze schemas from actual database files
    type_stats = Counter()
    domain_stats = defaultdict(lambda: defaultdict(int))
    constraint_patterns = Counter()
    
    domains = ['customer_service', 'finance', 'retail_cpg', 'healthcare', 'energy_manufacturing']
    total_columns = 0
    total_tables = 0
    
    for domain in domains:
        if not os.path.exists(domain):
            continue
            
        print(f"\n🏢 {domain.upper().replace('_', ' ')}")
        domain_columns = 0
        domain_tables = 0
        
        subdomains = [d for d in os.listdir(domain) 
                     if os.path.isdir(os.path.join(domain, d)) and not d.startswith('.')]
        
        for subdomain in subdomains:
            # Find a database file to analyze
            subdomain_path = os.path.join(domain, subdomain)
            db_files = [f for f in os.listdir(subdomain_path) 
                       if f.endswith('.db') and os.path.getsize(os.path.join(subdomain_path, f)) > 1000]
            
            if not db_files:
                continue
                
            db_path = os.path.join(subdomain_path, db_files[0])
            
            try:
                conn = sqlite3.connect(db_path)
                
                # Get table schemas
                tables = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'evidence_kv'
                """).fetchall()
                
                subdomain_types = set()
                subdomain_columns = 0
                
                for (table_name,) in tables:
                    # Get column info
                    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                    
                    for col in columns:
                        cid, name, data_type, notnull, default_value, pk = col
                        
                        # Normalize data type
                        clean_type = data_type.upper().split('(')[0].strip()
                        if not clean_type:
                            clean_type = 'TEXT'  # Default for empty types
                        
                        type_stats[clean_type] += 1
                        domain_stats[domain][clean_type] += 1
                        subdomain_types.add(clean_type)
                        subdomain_columns += 1
                        
                        # Analyze constraints
                        if notnull:
                            constraint_patterns['NOT_NULL'] += 1
                        if pk:
                            constraint_patterns['PRIMARY_KEY'] += 1
                        if default_value is not None:
                            constraint_patterns['DEFAULT'] += 1
                        if 'CHECK' in data_type.upper():
                            constraint_patterns['CHECK'] += 1
                        if 'REFERENCES' in data_type.upper():
                            constraint_patterns['FOREIGN_KEY'] += 1
                
                domain_columns += subdomain_columns
                domain_tables += len(tables)
                
                print(f"  📁 {subdomain}: {len(tables)} tables, {subdomain_columns} columns")
                print(f"     Types: {sorted(subdomain_types)}")
                
                conn.close()
                
            except Exception as e:
                print(f"  ❌ Error analyzing {subdomain}: {e}")
                continue
        
        print(f"  📊 Domain total: {domain_tables} tables, {domain_columns} columns")
        total_columns += domain_columns
        total_tables += domain_tables
    
    # Generate comprehensive analysis
    print(f"\n📈 OVERALL ANALYSIS")
    print("=" * 50)
    
    print(f"📊 Summary Statistics:")
    print(f"  Total Tables: {total_tables}")
    print(f"  Total Columns: {total_columns}")
    print(f"  Unique Data Types: {len(type_stats)}")
    print(f"  Avg Columns per Table: {total_columns/total_tables:.1f}")
    
    print(f"\n🎯 Data Type Distribution:")
    for data_type, count in type_stats.most_common(15):
        percentage = (count / total_columns) * 100
        print(f"  {data_type:20}: {count:4d} ({percentage:5.1f}%)")
    
    print(f"\n🔒 Constraint Usage:")
    for constraint, count in constraint_patterns.most_common():
        percentage = (count / total_columns) * 100
        print(f"  {constraint:15}: {count:4d} ({percentage:5.1f}%)")
    
    # Diversity assessment
    basic_types = {'TEXT', 'INTEGER'}
    advanced_types = {'REAL', 'BOOLEAN', 'BLOB', 'JSON', 'DATETIME', 'TIMESTAMP'}
    
    basic_count = sum(type_stats[t] for t in basic_types)
    advanced_count = sum(type_stats[t] for t in advanced_types if t in type_stats)
    
    basic_ratio = basic_count / total_columns
    advanced_ratio = advanced_count / total_columns
    diversity_score = len(type_stats) / 10  # Normalized diversity score
    
    print(f"\n🏆 DIVERSITY ASSESSMENT:")
    print(f"  Basic Types (TEXT, INTEGER): {basic_count} ({basic_ratio:.1%})")
    print(f"  Advanced Types (REAL, BOOLEAN, etc.): {advanced_count} ({advanced_ratio:.1%})")
    print(f"  Diversity Score: {diversity_score:.2f}/1.0")
    
    # Final assessment
    if diversity_score > 0.6 and advanced_ratio > 0.2:
        print(f"  🌟 EXCELLENT: High diversity with sophisticated data types")
    elif diversity_score > 0.4 and advanced_ratio > 0.15:
        print(f"  ✅ GOOD: Adequate diversity and sophistication")
    elif diversity_score > 0.3:
        print(f"  ⚠️  MODERATE: Limited but acceptable diversity")
    else:
        print(f"  ❌ POOR: Low diversity, needs improvement")
    
    # Save detailed report
    report = {
        'summary': {
            'total_tables': total_tables,
            'total_columns': total_columns,
            'unique_types': len(type_stats),
            'diversity_score': diversity_score,
            'basic_ratio': basic_ratio,
            'advanced_ratio': advanced_ratio
        },
        'type_distribution': dict(type_stats),
        'domain_breakdown': dict(domain_stats),
        'constraint_patterns': dict(constraint_patterns)
    }
    
    with open('DATA_TYPE_DIVERSITY_REPORT.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved: DATA_TYPE_DIVERSITY_REPORT.json")

if __name__ == '__main__':
    main()
