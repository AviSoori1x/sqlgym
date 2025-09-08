#!/usr/bin/env python3
"""
Populate all missing database files across all domains and subdomains.
Creates both normalized and denormalized databases with proper business names.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def load_business_names():
    """Load business database name mappings."""
    with open('business_database_names.json', 'r') as f:
        data = json.load(f)
    return data['business_database_names']

def get_all_subdomains():
    """Get all domain/subdomain combinations from the file system."""
    domains = {}
    
    # Define the domains to check
    domain_dirs = ['customer_service', 'finance', 'retail_cpg', 'healthcare', 'energy_manufacturing']
    
    for domain in domain_dirs:
        if os.path.exists(domain):
            domains[domain] = []
            for item in os.listdir(domain):
                subdomain_path = os.path.join(domain, item)
                if os.path.isdir(subdomain_path) and not item.startswith('.'):
                    domains[domain].append(item)
    
    return domains

def database_exists(domain, subdomain, business_name, db_type):
    """Check if database file exists."""
    db_file = f"{domain}/{subdomain}/{business_name}_{db_type}.db"
    return os.path.exists(db_file) and os.path.getsize(db_file) > 0

def create_database(domain, subdomain, business_name, db_type):
    """Create a database from schema and populate it."""
    schema_file = f"{domain}/{subdomain}/schema_{db_type}.sql"
    populate_script = f"{domain}/{subdomain}/populate_{db_type}.py"
    db_file = f"{domain}/{subdomain}/{business_name}_{db_type}.db"
    
    print(f"Creating {db_file}...")
    
    # Check if schema file exists
    if not os.path.exists(schema_file):
        print(f"  ❌ Schema file missing: {schema_file}")
        return False
    
    # Create database from schema
    try:
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Remove existing database if it exists
        if os.path.exists(db_file):
            os.remove(db_file)
        
        # Create database with schema
        result = subprocess.run(['sqlite3', db_file], 
                              input=schema_sql, 
                              text=True, 
                              capture_output=True)
        
        if result.returncode != 0:
            print(f"  ❌ Failed to create schema: {result.stderr}")
            return False
        
        print(f"  ✅ Schema created successfully")
        
        # Populate database if populate script exists
        if os.path.exists(populate_script):
            print(f"  📊 Populating data...")
            
            # Make script executable
            os.chmod(populate_script, 0o755)
            
            # Run population script
            result = subprocess.run([
                'python3', populate_script, 
                '--db', db_file
            ], capture_output=True, text=True, cwd='.')
            
            if result.returncode != 0:
                print(f"  ⚠️  Population script had issues: {result.stderr}")
                # Don't return False here - database still exists with schema
            else:
                print(f"  ✅ Data populated successfully")
        else:
            print(f"  ⚠️  No populate script found: {populate_script}")
        
        # Verify database was created with some size
        if os.path.exists(db_file) and os.path.getsize(db_file) > 1000:  # At least 1KB
            print(f"  ✅ Database created: {os.path.getsize(db_file)} bytes")
            return True
        else:
            print(f"  ❌ Database too small or missing")
            return False
            
    except Exception as e:
        print(f"  ❌ Error creating database: {e}")
        return False

def main():
    print("🏗️  POPULATING ALL MISSING DATABASE FILES")
    print("=" * 50)
    
    # Load business name mappings
    business_names = load_business_names()
    
    # Get all subdomains
    all_subdomains = get_all_subdomains()
    
    total_created = 0
    total_skipped = 0
    total_failed = 0
    
    # Process each domain/subdomain
    for domain, subdomains in all_subdomains.items():
        print(f"\n🏢 {domain.upper().replace('_', ' ')} DOMAIN")
        print("-" * 40)
        
        for subdomain in sorted(subdomains):
            print(f"\n📁 {subdomain}")
            
            # Get business name
            if domain in business_names and subdomain in business_names[domain]:
                business_name = business_names[domain][subdomain]
            else:
                print(f"  ⚠️  No business name mapping found, skipping...")
                continue
            
            # Check and create normalized database
            if database_exists(domain, subdomain, business_name, 'normalized'):
                print(f"  ✅ Normalized DB exists: {business_name}_normalized.db")
                total_skipped += 1
            else:
                if create_database(domain, subdomain, business_name, 'normalized'):
                    total_created += 1
                else:
                    total_failed += 1
            
            # Check and create denormalized database
            if database_exists(domain, subdomain, business_name, 'denormalized'):
                print(f"  ✅ Denormalized DB exists: {business_name}_denormalized.db")
                total_skipped += 1
            else:
                if create_database(domain, subdomain, business_name, 'denormalized'):
                    total_created += 1
                else:
                    total_failed += 1
    
    print(f"\n🎯 SUMMARY:")
    print(f"✅ Created: {total_created} databases")
    print(f"⏭️  Skipped: {total_skipped} (already existed)")
    print(f"❌ Failed: {total_failed} databases")
    print(f"\n🏆 Database population {'completed successfully!' if total_failed == 0 else 'completed with some issues.'}")

if __name__ == '__main__':
    main()
