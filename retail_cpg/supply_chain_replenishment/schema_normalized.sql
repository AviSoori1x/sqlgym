PRAGMA foreign_keys=ON;
CREATE TABLE stores (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE skus (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE store_sku_stock (
    store_id INTEGER NOT NULL REFERENCES stores(id),
    sku_id INTEGER NOT NULL REFERENCES skus(id),
    date TEXT NOT NULL,
    on_hand INTEGER NOT NULL,
    PRIMARY KEY(store_id, sku_id, date)
);
CREATE INDEX idx_stock_store_sku_date ON store_sku_stock(store_id, sku_id, date);
CREATE TABLE replen_orders (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL REFERENCES stores(id),
    sku_id INTEGER NOT NULL REFERENCES skus(id),
    order_date TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity>0),
    status TEXT NOT NULL CHECK(status IN ('PENDING','RECEIVED'))
);
CREATE INDEX idx_order_store_sku_date ON replen_orders(store_id, sku_id, order_date);
CREATE TABLE lead_times (
    sku_id INTEGER PRIMARY KEY REFERENCES skus(id),
    avg_days INTEGER NOT NULL CHECK(avg_days>0)
);
