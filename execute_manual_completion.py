#!/usr/bin/env python3
"""Manually execute completion steps."""

import subprocess
import os
import sys

def execute_step(description, command, cwd='.'):
    """Execute a step and report results."""
    print(f"\n🔧 {description}")
    print("-" * 50)
    
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        else:
            result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print("❌ ERROR")
            if result.stderr.strip():
                print("STDERR:", result.stderr)
            if result.stdout.strip():
                print("STDOUT:", result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    print("🏗️ MANUAL COMPLETION EXECUTION")
    print("=" * 50)
    
    # Step 1: Complete Energy Manufacturing denormalized schemas
    step1 = execute_step(
        "Complete Energy Manufacturing denormalized schemas",
        ["python3", "complete_energy_manufacturing_denormalized.py"]
    )
    
    # Step 2: Create wealth_advisory denormalized database
    step2 = execute_step(
        "Create wealth_advisory denormalized database",
        ["python3", "populate_denormalized.py", "--db", "morgan_stanley_wealth_denormalized.db"],
        cwd="finance/wealth_advisory"
    )
    
    # Step 3: Run data type audit
    step3 = execute_step(
        "Run comprehensive data type audit",
        ["python3", "audit_data_types.py"]
    )
    
    # Step 4: Final verification
    step4 = execute_step(
        "Final database verification",
        ["python3", "verify_all_databases.py"]
    )
    
    print(f"\n🎯 EXECUTION SUMMARY:")
    print(f"Energy Manufacturing completion: {'✅' if step1 else '❌'}")
    print(f"Finance wealth_advisory: {'✅' if step2 else '❌'}")
    print(f"Data type audit: {'✅' if step3 else '❌'}")
    print(f"Final verification: {'✅' if step4 else '❌'}")
    
    success_count = sum([step1, step2, step3, step4])
    print(f"\nOverall success: {success_count}/4 steps completed")

if __name__ == '__main__':
    main()
