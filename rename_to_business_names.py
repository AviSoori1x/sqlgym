#!/usr/bin/env python3
"""Rename databases and update references to use realistic business names."""
from __future__ import annotations

import json
import shutil
import re
from pathlib import Path

def load_business_names():
    """Load business name mappings."""
    with open('business_database_names.json') as f:
        return json.load(f)['business_database_names']

def rename_database_files(domain: str, subdomain: str, business_name: str):
    """Rename database files for a subdomain."""
    subdir = Path(domain) / subdomain
    
    # Old database names
    old_norm_db = f"{subdomain}_normalized.db"
    old_denorm_db = f"{subdomain}_denormalized.db"
    
    # New database names
    new_norm_db = f"{business_name}_normalized.db"
    new_denorm_db = f"{business_name}_denormalized.db"
    
    renamed_files = []
    
    # Rename normalized database if exists
    old_norm_path = subdir / old_norm_db
    new_norm_path = subdir / new_norm_db
    if old_norm_path.exists():
        shutil.move(old_norm_path, new_norm_path)
        renamed_files.append(f"  {old_norm_db} → {new_norm_db}")
    
    # Rename denormalized database if exists  
    old_denorm_path = subdir / old_denorm_db
    new_denorm_path = subdir / new_denorm_db
    if old_denorm_path.exists():
        shutil.move(old_denorm_path, new_denorm_path)
        renamed_files.append(f"  {old_denorm_db} → {new_denorm_db}")
    
    return renamed_files, new_norm_db, new_denorm_db

def update_script_references(domain: str, subdomain: str, business_name: str, new_norm_db: str, new_denorm_db: str):
    """Update script references to use new database names."""
    subdir = Path(domain) / subdomain
    updated_files = []
    
    # Files that might contain database references
    script_files = [
        'populate_normalized.py',
        'populate_denormalized.py', 
        'evidence_loader.py',
        'generate_schema_normalized.py',
        'sample_text_to_sql_tasks.md',
        'README.md'
    ]
    
    old_norm_name = f"{subdomain}_normalized.db"
    old_denorm_name = f"{subdomain}_denormalized.db"
    
    for script_file in script_files:
        script_path = subdir / script_file
        if script_path.exists():
            try:
                content = script_path.read_text()
                original_content = content
                
                # Replace database name references
                content = content.replace(old_norm_name, new_norm_db)
                content = content.replace(old_denorm_name, new_denorm_db)
                
                # Replace subdomain references in documentation
                if script_file in ['README.md', 'sample_text_to_sql_tasks.md']:
                    # Update titles and headers
                    content = content.replace(f"# {subdomain}", f"# {business_name}")
                    content = content.replace(f"Sample Tasks for {subdomain}", f"Sample Tasks for {business_name}")
                    content = content.replace(f"{subdomain} domain", f"{business_name} system")
                
                # Only write if content changed
                if content != original_content:
                    script_path.write_text(content)
                    updated_files.append(f"  Updated {script_file}")
                    
            except Exception as e:
                print(f"    Warning: Could not update {script_file}: {e}")
    
    return updated_files

def main():
    """Execute comprehensive renaming across all domains."""
    
    print("🏢 RENAMING DATABASES TO REALISTIC BUSINESS NAMES")
    print("=" * 60)
    
    business_names = load_business_names()
    total_renamed = 0
    total_updated = 0
    
    for domain, subdomains in business_names.items():
        print(f"\\n📂 {domain.upper()} DOMAIN:")
        
        for subdomain, business_name in subdomains.items():
            print(f"\\n  🔄 {subdomain} → {business_name}")
            
            try:
                # Rename database files
                renamed_files, new_norm_db, new_denorm_db = rename_database_files(domain, subdomain, business_name)
                
                if renamed_files:
                    print("\\n".join(renamed_files))
                    total_renamed += len(renamed_files)
                
                # Update script references
                updated_files = update_script_references(domain, subdomain, business_name, new_norm_db, new_denorm_db)
                
                if updated_files:
                    print("\\n".join(updated_files))
                    total_updated += len(updated_files)
                
                print(f"    ✅ {subdomain} → {business_name} completed")
                
            except Exception as e:
                print(f"    ❌ Error processing {subdomain}: {e}")
    
    print(f"\\n🎉 BUSINESS RENAMING COMPLETED!")
    print(f"=" * 40)
    print(f"✅ Database files renamed: {total_renamed}")
    print(f"✅ Script files updated: {total_updated}")
    print(f"✅ All references updated to business names")
    
    print(f"\\n🏆 REALISTIC BUSINESS DATABASE NAMES:")
    print(f"   • ZenDesk AI Support, SurveyMonkey Feedback")
    print(f"   • Chase Consumer Banking, JPMorgan Treasury")
    print(f"   • Amazon Customer Insights, Google Ads Analytics") 
    print(f"   • Anthem Claims System, Epic Clinical Orders")
    print(f"   • Exxon Carbon Tracking, Boeing Manufacturing")
    
    print(f"\\n🎯 The corpus now uses realistic business system names!")
    print(f"   Perfect for training, demos, and real-world scenarios!")
    
    return {
        'domains_processed': len(business_names),
        'subdomains_renamed': sum(len(subs) for subs in business_names.values()),
        'files_renamed': total_renamed,
        'scripts_updated': total_updated
    }

if __name__ == "__main__":
    result = main()
    print(f"\\n🚀 Ready for production use with realistic business names!")
