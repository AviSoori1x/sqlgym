#!/usr/bin/env python3
"""
Verify all database files exist with proper business names and sizes.
"""

import json
import os
from pathlib import Path

def load_business_names():
    """Load business database name mappings."""
    with open('business_database_names.json', 'r') as f:
        data = json.load(f)
    return data['business_database_names']

def format_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def main():
    print("🎯 COMPLETE DATABASE VERIFICATION REPORT")
    print("=" * 60)
    
    business_names = load_business_names()
    
    total_databases = 0
    total_size = 0
    domain_stats = {}
    
    for domain, subdomains in business_names.items():
        print(f"\n🏢 {domain.upper().replace('_', ' ')} DOMAIN")
        print("-" * 50)
        
        domain_count = 0
        domain_size = 0
        
        for subdomain, business_name in subdomains.items():
            print(f"\n📁 {subdomain} → {business_name}")
            
            # Check normalized database
            norm_db = f"{domain}/{subdomain}/{business_name}_normalized.db"
            denorm_db = f"{domain}/{subdomain}/{business_name}_denormalized.db"
            
            norm_exists = os.path.exists(norm_db)
            denorm_exists = os.path.exists(denorm_db)
            
            if norm_exists:
                norm_size = os.path.getsize(norm_db)
                print(f"    ✅ Normalized:   {format_size(norm_size)}")
                domain_count += 1
                domain_size += norm_size
                total_databases += 1
                total_size += norm_size
            else:
                print(f"    ❌ Normalized:   MISSING")
            
            if denorm_exists:
                denorm_size = os.path.getsize(denorm_db)
                print(f"    ✅ Denormalized: {format_size(denorm_size)}")
                domain_count += 1
                domain_size += denorm_size
                total_databases += 1
                total_size += denorm_size
            else:
                print(f"    ❌ Denormalized: MISSING")
        
        domain_stats[domain] = {
            'count': domain_count,
            'size': domain_size
        }
        
        print(f"\n📊 {domain.upper()} SUMMARY: {domain_count} databases, {format_size(domain_size)}")
    
    print(f"\n🎉 FINAL SUMMARY")
    print("=" * 60)
    print(f"Total Databases: {total_databases}")
    print(f"Total Size: {format_size(total_size)}")
    
    print(f"\n📊 BY DOMAIN:")
    for domain, stats in domain_stats.items():
        print(f"  {domain.replace('_', ' ').title()}: {stats['count']} databases ({format_size(stats['size'])})")
    
    # Calculate expected vs actual
    expected_total = sum(len(subdomains) * 2 for subdomains in business_names.values())
    completion_rate = (total_databases / expected_total) * 100
    
    print(f"\n🎯 COMPLETION RATE: {completion_rate:.1f}% ({total_databases}/{expected_total} databases)")
    
    if completion_rate >= 95:
        print("🏆 EXCELLENT! Nearly all databases are present.")
    elif completion_rate >= 85:
        print("✅ GOOD! Most databases are present.")
    else:
        print("⚠️  Some databases are still missing.")

if __name__ == '__main__':
    main()
