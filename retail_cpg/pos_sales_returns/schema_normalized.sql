PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('OPEN','CLOSED')),
    opened_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK(price_cents>0)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL REFERENCES stores(id),
    ordered_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PLACED','SHIPPED','CANCELLED')),
    promo_code TEXT
);
CREATE INDEX IF NOT EXISTS idx_orders_store_date ON orders(store_id, ordered_at);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK(quantity>0)
);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);

CREATE TABLE IF NOT EXISTS returns (
    id INTEGER PRIMARY KEY,
    order_item_id INTEGER NOT NULL REFERENCES order_items(id),
    returned_at TEXT NOT NULL,
    reason TEXT NOT NULL CHECK(reason IN ('DEFECT','DISSATISFIED','LATE_RETURN'))
);
CREATE INDEX IF NOT EXISTS idx_returns_item_date ON returns(order_item_id, returned_at);
