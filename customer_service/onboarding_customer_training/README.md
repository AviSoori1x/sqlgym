# docusign_onboarding

## Overview
This subdomain models customer onboarding workflows, training program management, and learning progress tracking across different service tiers.

## Entities

### Normalized Schema
- **customers**: Customer records with company size and onboarding tier assignments
- **training_programs**: Courses with types, delivery methods, and prerequisites
- **enrollments**: Links customers to programs with progress tracking
- **modules**: Individual learning units within programs
- **module_progress**: Detailed progress tracking including scores and attempts

### Denormalized Schema
- **customer_training_summary**: Per-customer training metrics and completion status
- **program_effectiveness**: Program performance metrics by month
- **cohort_analysis**: Time-based cohort retention and progress analysis
- **learning_path_analytics**: Personalized learning journey tracking

## Key Indexes
- `idx_customers_tier`: Tier-based segmentation queries
- `idx_enrollments_customer`: Customer training history lookups
- `idx_enrollments_status`: Active learner identification
- `idx_modules_program`: Program content navigation
- `idx_module_progress_enrollment`: Progress tracking queries

## Efficiency Notes
- Prerequisites stored as JSON arrays for flexible dependency management
- Progress percentage pre-calculated at enrollment level
- Module attempts tracked for difficulty analysis
- Evidence files define learning paths and tier-specific targets
- Fast/slow pairs demonstrate index usage vs full scans