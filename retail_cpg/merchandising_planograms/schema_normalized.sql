PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY,
    store_code TEXT NOT NULL UNIQUE,
    store_name TEXT NOT NULL,
    store_format TEXT NOT NULL CHECK(store_format IN ('SUPERMARKET', 'CONVENIENCE', 'HYPERMARKET', 'SPECIALTY', 'DISCOUNT')),
    location TEXT NOT NULL,
    square_footage INTEGER NOT NULL,
    opened_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS product_categories (
    id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE,
    parent_category_id INTEGER REFERENCES product_categories(id),
    category_level INTEGER NOT NULL CHECK(category_level BETWEEN 1 AND 4),
    space_allocation_percentage REAL CHECK(space_allocation_percentage BETWEEN 0 AND 100)
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES product_categories(id),
    brand TEXT NOT NULL,
    unit_cost REAL NOT NULL,
    retail_price REAL NOT NULL,
    package_dimensions TEXT, -- JSON with length, width, height
    velocity_rank TEXT NOT NULL CHECK(velocity_rank IN ('A', 'B', 'C', 'D'))
);

CREATE TABLE IF NOT EXISTS planograms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    store_id INTEGER NOT NULL REFERENCES stores(id),
    category_id INTEGER NOT NULL REFERENCES product_categories(id),
    effective_date TEXT NOT NULL,
    expiry_date TEXT,
    total_facings INTEGER NOT NULL,
    shelf_count INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('DRAFT', 'APPROVED', 'ACTIVE', 'EXPIRED'))
);

CREATE TABLE IF NOT EXISTS product_placements (
    id INTEGER PRIMARY KEY,
    planogram_id INTEGER NOT NULL REFERENCES planograms(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    shelf_number INTEGER NOT NULL,
    position_start INTEGER NOT NULL,
    position_end INTEGER NOT NULL,
    facings_count INTEGER NOT NULL CHECK(facings_count > 0),
    eye_level BOOLEAN NOT NULL DEFAULT 0,
    end_cap BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE(planogram_id, product_id)
);

CREATE TABLE IF NOT EXISTS sales_performance (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL REFERENCES stores(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    date TEXT NOT NULL,
    units_sold INTEGER NOT NULL DEFAULT 0,
    revenue REAL NOT NULL DEFAULT 0,
    inventory_level INTEGER NOT NULL DEFAULT 0,
    out_of_stock_hours INTEGER NOT NULL DEFAULT 0,
    UNIQUE(store_id, product_id, date)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_stores_format ON stores(store_format);
CREATE INDEX IF NOT EXISTS idx_product_categories_parent ON product_categories(parent_category_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_velocity ON products(velocity_rank);
CREATE INDEX IF NOT EXISTS idx_planograms_store ON planograms(store_id);
CREATE INDEX IF NOT EXISTS idx_planograms_category ON planograms(category_id);
CREATE INDEX IF NOT EXISTS idx_product_placements_planogram ON product_placements(planogram_id);
CREATE INDEX IF NOT EXISTS idx_sales_performance_store_date ON sales_performance(store_id, date);
CREATE INDEX IF NOT EXISTS idx_sales_performance_product ON sales_performance(product_id);