PRAGMA foreign_keys=OFF;
CREATE TABLE product_catalog (
    product_id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category_name TEXT NOT NULL,
    supplier_name TEXT NOT NULL,
    status TEXT NOT NULL,
    price_cents INTEGER NOT NULL
);
CREATE INDEX idx_pc_category ON product_catalog(category_name);
CREATE INDEX idx_pc_supplier ON product_catalog(supplier_name);
