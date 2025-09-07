PRAGMA foreign_keys=ON;
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);
CREATE TABLE price_books (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    price NUMERIC NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    CHECK(price>0)
);
CREATE INDEX idx_price_product ON price_books(product_id);
CREATE TABLE promos (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    promo_code TEXT NOT NULL,
    discount NUMERIC NOT NULL CHECK(discount BETWEEN 0 AND 1),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    UNIQUE(promo_code)
);
CREATE INDEX idx_promo_prod_date ON promos(product_id, start_date);
CREATE TABLE receipts (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    sale_date TEXT NOT NULL,
    price_paid NUMERIC NOT NULL,
    promo_code TEXT,
    FOREIGN KEY(promo_code) REFERENCES promos(promo_code)
);
CREATE INDEX idx_receipt_prod_date ON receipts(product_id, sale_date);
