-- Toyota Quality System Denormalized Analytics
-- Trade-off: Pre-calculated quality metrics and NCR analysis vs real-time accuracy
PRAGMA foreign_keys=OFF;

-- Quality performance summary by product line
CREATE TABLE IF NOT EXISTS quality_summary (
    product_line_id INTEGER PRIMARY KEY,
    product_line_name TEXT NOT NULL,
    total_inspections INTEGER NOT NULL,
    passed_inspections INTEGER NOT NULL,
    ncr_count INTEGER NOT NULL,
    defect_rate REAL NOT NULL,
    first_pass_yield REAL NOT NULL,
    cost_of_quality REAL NOT NULL,
    customer_satisfaction REAL NOT NULL,
    quality_score REAL NOT NULL,
    sigma_level REAL NOT NULL,
    improvement_projects INTEGER NOT NULL
);

-- Monthly quality trends
CREATE TABLE IF NOT EXISTS monthly_quality_trends (
    year_month TEXT PRIMARY KEY,
    total_inspections INTEGER NOT NULL,
    total_ncrs INTEGER NOT NULL,
    defect_rate REAL NOT NULL,
    cost_of_quality REAL NOT NULL,
    customer_complaints INTEGER NOT NULL,
    quality_audits INTEGER NOT NULL,
    corrective_actions INTEGER NOT NULL,
    preventive_actions INTEGER NOT NULL
);

-- Analytical indexes
CREATE INDEX IF NOT EXISTS idx_quality_summary_score ON quality_summary(quality_score);
CREATE INDEX IF NOT EXISTS idx_quality_summary_defect_rate ON quality_summary(defect_rate);
CREATE INDEX IF NOT EXISTS idx_monthly_quality_date ON monthly_quality_trends(year_month);
