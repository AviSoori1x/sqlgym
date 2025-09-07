#!/usr/bin/env python3
"""Populate onboarding customer training normalized schema with synthetic data."""
from __future__ import annotations

import argparse
import sqlite3
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from common.utils import get_rng, batch

# Scale constants
CUSTOMERS = 2500
TRAINING_PROGRAMS = 30
ENROLLMENTS_PER_CUSTOMER = 5
COMPLETION_RATE = 0.75

# Industries
INDUSTRIES = [
    'Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing',
    'Education', 'Government', 'Non-profit', 'Media', 'Consulting'
]

# Training program templates
PROGRAM_TEMPLATES = [
    # Onboarding programs
    ('Getting Started', 'ONBOARDING', 'SELF_PACED', 2, 'BEGINNER', True),
    ('Platform Overview', 'ONBOARDING', 'WEBINAR', 1.5, 'BEGINNER', True),
    ('Initial Setup Guide', 'ONBOARDING', 'SELF_PACED', 3, 'BEGINNER', True),
    ('Best Practices Workshop', 'ONBOARDING', 'INSTRUCTOR_LED', 4, 'INTERMEDIATE', True),
    ('Enterprise Onboarding', 'ONBOARDING', 'ON_SITE', 16, 'INTERMEDIATE', False),
    
    # Feature programs
    ('Advanced Analytics', 'FEATURE', 'SELF_PACED', 4, 'ADVANCED', False),
    ('API Integration', 'FEATURE', 'WEBINAR', 2, 'INTERMEDIATE', False),
    ('Custom Reporting', 'FEATURE', 'INSTRUCTOR_LED', 3, 'INTERMEDIATE', False),
    ('Mobile App Training', 'FEATURE', 'SELF_PACED', 1.5, 'BEGINNER', False),
    ('Automation Features', 'FEATURE', 'WEBINAR', 2.5, 'ADVANCED', False),
    
    # Certification programs
    ('Basic Certification', 'CERTIFICATION', 'SELF_PACED', 8, 'BEGINNER', False),
    ('Professional Certification', 'CERTIFICATION', 'INSTRUCTOR_LED', 16, 'INTERMEDIATE', False),
    ('Expert Certification', 'CERTIFICATION', 'INSTRUCTOR_LED', 24, 'ADVANCED', False),
    ('Admin Certification', 'CERTIFICATION', 'SELF_PACED', 12, 'INTERMEDIATE', False),
    
    # Refresher programs
    ('Quarterly Update', 'REFRESHER', 'WEBINAR', 1, 'BEGINNER', False),
    ('Security Best Practices', 'REFRESHER', 'SELF_PACED', 2, 'INTERMEDIATE', True),
    ('New Features Review', 'REFRESHER', 'WEBINAR', 1.5, 'BEGINNER', False),
]

def calculate_progress(module_progresses, total_modules):
    """Calculate overall progress percentage."""
    if not total_modules:
        return 0
    completed = sum(1 for mp in module_progresses if mp['completed'])
    return int((completed / total_modules) * 100)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = get_rng(args.seed)
    random.seed(args.seed)
    
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Insert customers
    print(f"Inserting {CUSTOMERS} customers...")
    customers_data = []
    company_sizes = ['SMALL', 'MEDIUM', 'LARGE', 'ENTERPRISE']
    size_weights = [0.40, 0.35, 0.20, 0.05]
    
    tier_by_size = {
        'SMALL': ['SELF_SERVICE', 'STANDARD'],
        'MEDIUM': ['STANDARD', 'PREMIUM'],
        'LARGE': ['PREMIUM', 'WHITE_GLOVE'],
        'ENTERPRISE': ['PREMIUM', 'WHITE_GLOVE']
    }
    
    for i in range(1, CUSTOMERS + 1):
        company_size = rng.choices(company_sizes, weights=size_weights)[0]
        industry = rng.choice(INDUSTRIES)
        onboarding_tier = rng.choice(tier_by_size[company_size])
        
        customers_data.append((
            i,
            f'Customer_{i}',
            f'user{i}@company{i}.com',
            company_size,
            industry,
            onboarding_tier
        ))
    
    for chunk in batch(customers_data, 1000):
        conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", chunk)
    
    # Insert training programs
    print(f"Inserting training programs...")
    programs_data = []
    program_id = 1
    
    for name, prog_type, delivery, duration, difficulty, mandatory in PROGRAM_TEMPLATES:
        # Some programs have prerequisites
        prerequisites = []
        if difficulty == 'INTERMEDIATE' and program_id > 3:
            prerequisites = [rng.randint(1, min(3, program_id-1))]
        elif difficulty == 'ADVANCED' and program_id > 5:
            prerequisites = [rng.randint(1, min(5, program_id-1)), rng.randint(4, min(8, program_id-1))]
        
        programs_data.append((
            program_id,
            name,
            prog_type,
            delivery,
            duration,
            difficulty,
            json.dumps(prerequisites) if prerequisites else None,
            mandatory
        ))
        program_id += 1
    
    # Add some industry-specific programs
    for industry in INDUSTRIES[:5]:
        programs_data.append((
            program_id,
            f'{industry} Industry Guide',
            'FEATURE',
            'SELF_PACED',
            3,
            'INTERMEDIATE',
            json.dumps([1]),  # Requires basic onboarding
            False
        ))
        program_id += 1
    
    conn.executemany("INSERT INTO training_programs VALUES (?,?,?,?,?,?,?,?)", programs_data)
    
    # Insert modules for each program
    print("Inserting training modules...")
    modules_data = []
    module_id = 1
    
    for program in programs_data:
        prog_id = program[0]
        duration_hours = program[4]
        prog_type = program[2]
        
        # Calculate number of modules based on duration
        num_modules = max(1, int(duration_hours * 2))
        
        for seq in range(1, num_modules + 1):
            # Mix of content types
            if seq == num_modules and prog_type == 'CERTIFICATION':
                content_type = 'QUIZ'
                passing_score = 80
            elif seq % 3 == 0:
                content_type = 'QUIZ'
                passing_score = 70
            elif prog_type == 'INSTRUCTOR_LED' and seq % 4 == 0:
                content_type = 'LIVE_SESSION'
                passing_score = None
            else:
                content_type = rng.choice(['VIDEO', 'DOCUMENT', 'EXERCISE'])
                passing_score = 60 if content_type == 'EXERCISE' else None
            
            duration_minutes = int((duration_hours * 60) / num_modules * rng.uniform(0.8, 1.2))
            
            modules_data.append((
                module_id,
                prog_id,
                seq,
                f'Module {seq}: {content_type.title()}',
                content_type,
                duration_minutes,
                passing_score
            ))
            module_id += 1
    
    conn.executemany("INSERT INTO modules VALUES (?,?,?,?,?,?,?)", modules_data)
    
    # Insert enrollments and module progress
    print(f"Inserting enrollments and progress...")
    enrollments_data = []
    module_progress_data = []
    
    enrollment_id = 1
    progress_id = 1
    base_date = datetime(2023, 6, 1)
    
    for customer in customers_data:
        customer_id = customer[0]
        onboarding_tier = customer[5]
        
        # Everyone gets mandatory programs
        mandatory_programs = [p[0] for p in programs_data if p[7]]  # is_mandatory
        
        # Additional programs based on tier
        additional_count = {
            'SELF_SERVICE': 1,
            'STANDARD': 3,
            'PREMIUM': 5,
            'WHITE_GLOVE': 8
        }[onboarding_tier]
        
        optional_programs = [p[0] for p in programs_data if not p[7]]
        selected_programs = mandatory_programs + rng.sample(
            optional_programs, 
            min(additional_count, len(optional_programs))
        )
        
        # Create enrollments
        for prog_id in selected_programs[:ENROLLMENTS_PER_CUSTOMER]:
            enrolled_at = base_date + timedelta(days=rng.randint(0, 180))
            
            # Determine completion status
            if rng.random() < COMPLETION_RATE:
                status = 'COMPLETED'
                started_at = enrolled_at + timedelta(days=rng.randint(0, 7))
                completed_at = started_at + timedelta(days=rng.randint(7, 60))
                progress = 100
            else:
                if rng.random() < 0.5:
                    status = 'IN_PROGRESS'
                    started_at = enrolled_at + timedelta(days=rng.randint(0, 14))
                    completed_at = None
                    progress = rng.randint(10, 90)
                else:
                    status = rng.choice(['ENROLLED', 'DROPPED'])
                    started_at = enrolled_at + timedelta(days=rng.randint(0, 30)) if status == 'DROPPED' else None
                    completed_at = None
                    progress = rng.randint(0, 30) if status == 'DROPPED' else 0
            
            assigned_by = 'System' if prog_id in mandatory_programs else rng.choice(['Manager', 'Self', 'Admin'])
            
            enrollments_data.append((
                enrollment_id,
                customer_id,
                prog_id,
                enrolled_at.strftime('%Y-%m-%d %H:%M:%S'),
                started_at.strftime('%Y-%m-%d %H:%M:%S') if started_at else None,
                completed_at.strftime('%Y-%m-%d %H:%M:%S') if completed_at else None,
                status,
                progress,
                assigned_by
            ))
            
            # Create module progress if started
            if started_at:
                # Get modules for this program
                program_modules = [m for m in modules_data if m[1] == prog_id]
                modules_to_complete = int(len(program_modules) * (progress / 100))
                
                for idx, module in enumerate(program_modules[:modules_to_complete + 1]):
                    module_started = started_at + timedelta(days=idx * 2)
                    
                    if idx < modules_to_complete:
                        module_completed = module_started + timedelta(hours=rng.randint(1, 48))
                        score = rng.randint(70, 100) if module[6] else None  # passing_score exists
                        attempts = 1 if not score or score >= 70 else rng.randint(2, 3)
                    else:
                        module_completed = None
                        score = None
                        attempts = 1
                    
                    time_spent = module[5] * rng.uniform(0.8, 1.5)  # duration +/- 20%
                    
                    module_progress_data.append((
                        progress_id,
                        enrollment_id,
                        module[0],
                        module_started.strftime('%Y-%m-%d %H:%M:%S'),
                        module_completed.strftime('%Y-%m-%d %H:%M:%S') if module_completed else None,
                        score,
                        attempts,
                        int(time_spent)
                    ))
                    progress_id += 1
            
            enrollment_id += 1
    
    # Batch insert all data
    for chunk in batch(enrollments_data, 1000):
        conn.executemany("INSERT INTO enrollments VALUES (?,?,?,?,?,?,?,?,?)", chunk)
    
    for chunk in batch(module_progress_data, 1000):
        conn.executemany("INSERT INTO module_progress VALUES (?,?,?,?,?,?,?,?)", chunk)
    
    # Create evidence table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_kv (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    conn.commit()
    
    # Create indexes after bulk loading
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(onboarding_tier)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_programs_type ON training_programs(program_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_customer ON enrollments(customer_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_status ON enrollments(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_enrolled ON enrollments(enrolled_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_modules_program ON modules(program_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_module_progress_enrollment ON module_progress(enrollment_id)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()