#!/usr/bin/env python3
"""Run completion scripts and create missing databases."""

import subprocess
import os

def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n🔧 {description}")
    print("-" * 50)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print(f"❌ Error: {description}")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🏗️ COMPLETING ALL MISSING IMPLEMENTATIONS")
    print("=" * 60)
    
    # Step 1: Complete Energy Manufacturing denormalized schemas
    success1 = run_command(
        "python3 complete_energy_manufacturing_denormalized.py",
        "Creating Energy Manufacturing denormalized schemas and populators"
    )
    
    # Step 2: Create Finance wealth_advisory denormalized database
    success2 = run_command(
        "cd finance/wealth_advisory && python3 populate_denormalized.py --db morgan_stanley_wealth_denormalized.db",
        "Creating Morgan Stanley Wealth denormalized database"
    )
    
    # Step 3: Verify completion
    success3 = run_command(
        "python3 verify_all_databases.py",
        "Verifying all databases are now complete"
    )
    
    print(f"\n🎯 COMPLETION SUMMARY:")
    print(f"Energy Manufacturing schemas: {'✅' if success1 else '❌'}")
    print(f"Finance wealth_advisory DB: {'✅' if success2 else '❌'}")
    print(f"Final verification: {'✅' if success3 else '❌'}")
    
    if success1 and success2:
        print("\n🏆 ALL IMPLEMENTATIONS COMPLETED SUCCESSFULLY!")
    else:
        print("\n⚠️  Some implementations had issues - manual review needed")

if __name__ == '__main__':
    main()
