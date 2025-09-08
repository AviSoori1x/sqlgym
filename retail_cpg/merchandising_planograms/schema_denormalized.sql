-- Denormalized merchandising planograms analytics
-- Trade-off: Pre-calculated shelf performance and space optimization vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS planogram_performance (
    planogram_id INTEGER PRIMARY KEY,
    planogram_name TEXT NOT NULL,
    store_code TEXT NOT NULL,
    category_name TEXT NOT NULL,
    total_facings INTEGER NOT NULL,
    products_placed INTEGER NOT NULL,
    total_sales_30d REAL NOT NULL,
    sales_per_facing REAL NOT NULL,
    space_efficiency_score REAL NOT NULL,
    last_updated_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS product_placement_analysis (
    product_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    stores_placed INTEGER NOT NULL,
    total_facings INTEGER NOT NULL,
    eye_level_facings INTEGER NOT NULL,
    end_cap_placements INTEGER NOT NULL,
    total_sales REAL NOT NULL,
    sales_per_facing REAL NOT NULL,
    placement_effectiveness_score REAL,
    PRIMARY KEY(product_id, month)
);

CREATE TABLE IF NOT EXISTS store_category_performance (
    store_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    allocated_facings INTEGER NOT NULL,
    sales_volume REAL NOT NULL,
    sales_per_sqft REAL NOT NULL,
    inventory_turns REAL,
    out_of_stock_rate REAL,
    PRIMARY KEY(store_id, category_id, month)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_planogram_performance_efficiency ON planogram_performance(space_efficiency_score DESC);
CREATE INDEX IF NOT EXISTS idx_product_analysis_effectiveness ON product_placement_analysis(placement_effectiveness_score DESC);
CREATE INDEX IF NOT EXISTS idx_store_category_month ON store_category_performance(month);