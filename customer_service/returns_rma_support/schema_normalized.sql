PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    loyalty_tier TEXT NOT NULL CHECK(loyalty_tier IN ('BASIC', 'SILVER', 'GOLD', 'PLATINUM')),
    lifetime_value INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('ELECTRONICS', 'APPAREL', 'HOME', 'SPORTS', 'TOYS', 'BEAUTY')),
    unit_price REAL NOT NULL,
    warranty_days INTEGER NOT NULL DEFAULT 365,
    returnable BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_date TEXT NOT NULL,
    total_amount REAL NOT NULL,
    shipping_address TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL,
    discount_amount REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS rma_requests (
    id INTEGER PRIMARY KEY,
    order_item_id INTEGER NOT NULL REFERENCES order_items(id),
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    request_date TEXT NOT NULL,
    reason TEXT NOT NULL CHECK(reason IN ('DEFECTIVE', 'WRONG_ITEM', 'NOT_AS_DESCRIBED', 'DAMAGED', 'CHANGED_MIND', 'BETTER_PRICE', 'OTHER')),
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'APPROVED', 'REJECTED', 'SHIPPED', 'RECEIVED', 'INSPECTED', 'PROCESSED', 'CLOSED')),
    return_method TEXT CHECK(return_method IN ('PREPAID_LABEL', 'CUSTOMER_SHIP', 'PICKUP', 'DROP_OFF')),
    tracking_number TEXT,
    notes TEXT,
    UNIQUE(order_item_id)
);

CREATE TABLE IF NOT EXISTS rma_inspections (
    id INTEGER PRIMARY KEY,
    rma_id INTEGER NOT NULL REFERENCES rma_requests(id),
    inspection_date TEXT NOT NULL,
    inspector_id TEXT NOT NULL,
    condition TEXT NOT NULL CHECK(condition IN ('NEW', 'LIKE_NEW', 'GOOD', 'FAIR', 'POOR', 'DAMAGED')),
    functionality TEXT NOT NULL CHECK(functionality IN ('WORKING', 'PARTIALLY_WORKING', 'NOT_WORKING', 'NOT_TESTED')),
    recommendation TEXT NOT NULL CHECK(recommendation IN ('FULL_REFUND', 'PARTIAL_REFUND', 'EXCHANGE', 'REPAIR', 'REJECT')),
    deduction_percentage INTEGER DEFAULT 0 CHECK(deduction_percentage BETWEEN 0 AND 100),
    UNIQUE(rma_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(loyalty_tier);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_rma_customer ON rma_requests(customer_id);
CREATE INDEX IF NOT EXISTS idx_rma_status ON rma_requests(status);
CREATE INDEX IF NOT EXISTS idx_rma_date ON rma_requests(request_date);