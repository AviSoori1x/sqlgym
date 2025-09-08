#!/usr/bin/env python3
"""
Comprehensive audit of data types across all schemas to assess diversity.
"""

import sqlite3
import os
import json
from pathlib import Path
from collections import defaultdict, Counter

def get_schema_info(db_path):
    """Extract schema information from a database."""
    try:
        if not os.path.exists(db_path) or os.path.getsize(db_path) < 1000:
            return None
            
        conn = sqlite3.connect(db_path)
        
        # Get all tables
        tables = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'evidence_kv'
        """).fetchall()
        
        schema_info = {}
        
        for (table_name,) in tables:
            # Get column information
            columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
            
            column_info = []
            for col in columns:
                cid, name, data_type, notnull, default_value, pk = col
                column_info.append({
                    'name': name,
                    'type': data_type,
                    'not_null': bool(notnull),
                    'primary_key': bool(pk),
                    'default': default_value
                })
            
            schema_info[table_name] = column_info
        
        conn.close()
        return schema_info
        
    except Exception as e:
        return None

def analyze_data_types():
    """Analyze data type diversity across all schemas."""
    
    print("🔍 COMPREHENSIVE DATA TYPE DIVERSITY AUDIT")
    print("=" * 60)
    
    # Collect all schema information
    all_schemas = {}
    type_stats = defaultdict(int)
    domain_type_stats = defaultdict(lambda: defaultdict(int))
    constraint_stats = defaultdict(int)
    
    domains = ['customer_service', 'finance', 'retail_cpg', 'healthcare', 'energy_manufacturing']
    
    for domain in domains:
        if not os.path.exists(domain):
            continue
            
        print(f"\n🏢 {domain.upper().replace('_', ' ')} DOMAIN")
        print("-" * 40)
        
        subdomains = [d for d in os.listdir(domain) if os.path.isdir(os.path.join(domain, d)) and not d.startswith('.')]
        
        for subdomain in subdomains:
            subdomain_path = os.path.join(domain, subdomain)
            
            # Find database files
            db_files = [f for f in os.listdir(subdomain_path) if f.endswith('_normalized.db')]
            
            if not db_files:
                continue
                
            db_path = os.path.join(subdomain_path, db_files[0])
            schema_info = get_schema_info(db_path)
            
            if not schema_info:
                continue
            
            print(f"\n📁 {subdomain}")
            
            subdomain_types = set()
            subdomain_constraints = set()
            
            for table_name, columns in schema_info.items():
                print(f"    📋 {table_name}: {len(columns)} columns")
                
                for col in columns:
                    data_type = col['type'].upper()
                    type_stats[data_type] += 1
                    domain_type_stats[domain][data_type] += 1
                    subdomain_types.add(data_type)
                    
                    # Track constraints
                    if col['not_null']:
                        constraint_stats['NOT_NULL'] += 1
                        subdomain_constraints.add('NOT_NULL')
                    if col['primary_key']:
                        constraint_stats['PRIMARY_KEY'] += 1
                        subdomain_constraints.add('PRIMARY_KEY')
                    if col['default'] is not None:
                        constraint_stats['DEFAULT'] += 1
                        subdomain_constraints.add('DEFAULT')
                    
                    # Check for CHECK constraints in type
                    if 'CHECK' in data_type:
                        constraint_stats['CHECK'] += 1
                        subdomain_constraints.add('CHECK')
                    
                    print(f"        {col['name']}: {data_type}")
            
            print(f"    🎯 Types used: {sorted(subdomain_types)}")
            print(f"    🔒 Constraints: {sorted(subdomain_constraints)}")
            
            all_schemas[f"{domain}/{subdomain}"] = schema_info
    
    # Generate comprehensive analysis
    print(f"\n📊 OVERALL DATA TYPE DIVERSITY ANALYSIS")
    print("=" * 60)
    
    print(f"\n🎯 Data Type Distribution:")
    for data_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {data_type}: {count} columns")
    
    print(f"\n🏢 Data Types by Domain:")
    for domain, types in domain_type_stats.items():
        print(f"\n  {domain.replace('_', ' ').title()}:")
        for data_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"    {data_type}: {count}")
    
    print(f"\n🔒 Constraint Usage:")
    for constraint, count in sorted(constraint_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {constraint}: {count} occurrences")
    
    # Diversity metrics
    total_columns = sum(type_stats.values())
    unique_types = len(type_stats)
    type_diversity_ratio = unique_types / total_columns if total_columns > 0 else 0
    
    print(f"\n📈 DIVERSITY METRICS:")
    print(f"  Total Columns: {total_columns}")
    print(f"  Unique Data Types: {unique_types}")
    print(f"  Type Diversity Ratio: {type_diversity_ratio:.3f}")
    
    # Check for sophistication indicators
    sophisticated_types = {'REAL', 'BOOLEAN', 'JSON', 'BLOB', 'DATETIME', 'TIMESTAMP'}
    sophisticated_count = sum(type_stats.get(t, 0) for t in sophisticated_types)
    sophistication_ratio = sophisticated_count / total_columns if total_columns > 0 else 0
    
    print(f"  Sophisticated Types: {sophisticated_count}/{total_columns} ({sophistication_ratio:.1%})")
    
    # Assessment
    print(f"\n🏆 ASSESSMENT:")
    if type_diversity_ratio > 0.05:
        print("✅ EXCELLENT: High data type diversity")
    elif type_diversity_ratio > 0.03:
        print("✅ GOOD: Adequate data type diversity") 
    else:
        print("⚠️  LIMITED: Low data type diversity")
    
    if sophistication_ratio > 0.15:
        print("✅ EXCELLENT: High use of sophisticated data types")
    elif sophistication_ratio > 0.10:
        print("✅ GOOD: Adequate use of sophisticated data types")
    else:
        print("⚠️  BASIC: Limited use of sophisticated data types")
    
    # Generate detailed report
    report_data = {
        'total_columns': total_columns,
        'unique_types': unique_types,
        'type_diversity_ratio': type_diversity_ratio,
        'sophistication_ratio': sophistication_ratio,
        'type_distribution': dict(type_stats),
        'domain_breakdown': dict(domain_type_stats),
        'constraint_usage': dict(constraint_stats)
    }
    
    with open('DATA_TYPE_AUDIT_REPORT.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Detailed report saved to DATA_TYPE_AUDIT_REPORT.json")

if __name__ == '__main__':
    analyze_data_types()
