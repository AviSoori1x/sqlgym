PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY,
    supplier_code TEXT NOT NULL UNIQUE,
    supplier_name TEXT NOT NULL,
    supplier_type TEXT NOT NULL CHECK(supplier_type IN ('STRATEGIC', 'PREFERRED', 'APPROVED', 'CONDITIONAL', 'BLACKLISTED')),
    business_category TEXT NOT NULL CHECK(business_category IN ('MATERIALS', 'SERVICES', 'EQUIPMENT', 'CONSULTING', 'LOGISTICS')),
    country TEXT NOT NULL,
    certification_status TEXT NOT NULL CHECK(certification_status IN ('ISO_9001', 'ISO_14001', 'ISO_45001', 'MULTIPLE', 'NONE')),
    risk_rating TEXT NOT NULL CHECK(risk_rating IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    onboarding_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'TERMINATED'))
);

CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY,
    contract_number TEXT NOT NULL UNIQUE,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    contract_type TEXT NOT NULL CHECK(contract_type IN ('MASTER_AGREEMENT', 'SPOT_PURCHASE', 'BLANKET_ORDER', 'FRAMEWORK')),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    total_value REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    payment_terms_days INTEGER NOT NULL,
    performance_guarantees TEXT, -- JSON array
    status TEXT NOT NULL CHECK(status IN ('DRAFT', 'ACTIVE', 'EXPIRED', 'TERMINATED'))
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY,
    po_number TEXT NOT NULL UNIQUE,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    contract_id INTEGER REFERENCES contracts(id),
    order_date TEXT NOT NULL,
    requested_delivery_date TEXT NOT NULL,
    actual_delivery_date TEXT,
    total_amount REAL NOT NULL,
    order_status TEXT NOT NULL CHECK(order_status IN ('PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'INVOICED', 'PAID', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS supplier_performance_metrics (
    id INTEGER PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    evaluation_period TEXT NOT NULL, -- YYYY-MM format
    on_time_delivery_rate REAL NOT NULL CHECK(on_time_delivery_rate BETWEEN 0 AND 1),
    quality_score REAL NOT NULL CHECK(quality_score BETWEEN 0 AND 100),
    cost_competitiveness_score REAL NOT NULL CHECK(cost_competitiveness_score BETWEEN 0 AND 100),
    responsiveness_score REAL NOT NULL CHECK(responsiveness_score BETWEEN 0 AND 100),
    overall_score REAL NOT NULL CHECK(overall_score BETWEEN 0 AND 100),
    evaluated_by TEXT NOT NULL,
    evaluation_date TEXT NOT NULL,
    UNIQUE(supplier_id, evaluation_period)
);

CREATE TABLE IF NOT EXISTS supplier_audits (
    id INTEGER PRIMARY KEY,
    audit_id TEXT NOT NULL UNIQUE,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    audit_date TEXT NOT NULL,
    audit_type TEXT NOT NULL CHECK(audit_type IN ('QUALITY', 'COMPLIANCE', 'FINANCIAL', 'OPERATIONAL')),
    auditor_name TEXT NOT NULL,
    audit_score REAL CHECK(audit_score BETWEEN 0 AND 100),
    findings TEXT,
    corrective_actions_required INTEGER DEFAULT 0,
    next_audit_due_date TEXT,
    status TEXT NOT NULL CHECK(status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'FOLLOW_UP_REQUIRED'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_suppliers_type ON suppliers(supplier_type);
CREATE INDEX IF NOT EXISTS idx_suppliers_risk ON suppliers(risk_rating);
CREATE INDEX IF NOT EXISTS idx_contracts_supplier ON contracts(supplier_id);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_supplier ON purchase_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_date ON purchase_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_supplier ON supplier_performance_metrics(supplier_id);
CREATE INDEX IF NOT EXISTS idx_supplier_audits_supplier ON supplier_audits(supplier_id);