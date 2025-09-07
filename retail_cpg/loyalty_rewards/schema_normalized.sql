PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    tier_id INTEGER NOT NULL REFERENCES tiers(id),
    enrollment_date TEXT NOT NULL,
    total_points_earned INTEGER NOT NULL DEFAULT 0,
    current_points_balance INTEGER NOT NULL DEFAULT 0,
    lifetime_spend REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'CHURNED'))
);

CREATE TABLE IF NOT EXISTS tiers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    tier_order INTEGER NOT NULL UNIQUE,
    min_spend_threshold REAL NOT NULL,
    min_points_threshold INTEGER NOT NULL,
    benefits TEXT NOT NULL, -- JSON array of benefits
    point_multiplier REAL NOT NULL DEFAULT 1.0,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS point_transactions (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('EARN', 'REDEEM', 'EXPIRE', 'ADJUSTMENT')),
    points_amount INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    reference_order_id TEXT,
    expiration_date TEXT,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rewards_catalog (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('DISCOUNT', 'FREE_PRODUCT', 'FREE_SHIPPING', 'EXPERIENCE', 'CASHBACK')),
    points_cost INTEGER NOT NULL,
    monetary_value REAL,
    tier_restriction INTEGER REFERENCES tiers(id),
    stock_quantity INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    valid_from TEXT NOT NULL,
    valid_until TEXT
);

CREATE TABLE IF NOT EXISTS redemptions (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    reward_id INTEGER NOT NULL REFERENCES rewards_catalog(id),
    redemption_date TEXT NOT NULL,
    points_redeemed INTEGER NOT NULL,
    order_id TEXT,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'PROCESSED', 'CANCELLED', 'EXPIRED'))
);

CREATE TABLE IF NOT EXISTS tier_movements (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    from_tier_id INTEGER REFERENCES tiers(id),
    to_tier_id INTEGER NOT NULL REFERENCES tiers(id),
    movement_date TEXT NOT NULL,
    reason TEXT NOT NULL CHECK(reason IN ('SPEND_THRESHOLD', 'POINTS_THRESHOLD', 'MANUAL_UPGRADE', 'ANNUAL_RESET', 'DOWNGRADE'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_members_tier ON members(tier_id);
CREATE INDEX IF NOT EXISTS idx_members_status ON members(status);
CREATE INDEX IF NOT EXISTS idx_point_transactions_member ON point_transactions(member_id);
CREATE INDEX IF NOT EXISTS idx_point_transactions_date ON point_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_redemptions_member ON redemptions(member_id);
CREATE INDEX IF NOT EXISTS idx_redemptions_date ON redemptions(redemption_date);
CREATE INDEX IF NOT EXISTS idx_tier_movements_member ON tier_movements(member_id);