PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY,
    part_number TEXT NOT NULL UNIQUE,
    part_name TEXT NOT NULL,
    part_category TEXT NOT NULL CHECK(part_category IN ('RAW_MATERIAL', 'COMPONENT', 'ASSEMBLY', 'FINISHED_GOOD')),
    unit_of_measure TEXT NOT NULL,
    standard_cost REAL NOT NULL,
    lead_time_days INTEGER NOT NULL,
    supplier_id TEXT,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'OBSOLETE', 'DISCONTINUED'))
);

CREATE TABLE IF NOT EXISTS bill_of_materials (
    id INTEGER PRIMARY KEY,
    bom_id TEXT NOT NULL UNIQUE,
    parent_part_id INTEGER NOT NULL REFERENCES parts(id),
    child_part_id INTEGER NOT NULL REFERENCES parts(id),
    quantity_required REAL NOT NULL,
    scrap_factor REAL DEFAULT 0,
    effective_date TEXT NOT NULL,
    expiry_date TEXT,
    UNIQUE(parent_part_id, child_part_id)
);

CREATE TABLE IF NOT EXISTS work_orders (
    id INTEGER PRIMARY KEY,
    work_order_number TEXT NOT NULL UNIQUE,
    part_id INTEGER NOT NULL REFERENCES parts(id),
    quantity_ordered INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
    status TEXT NOT NULL CHECK(status IN ('PLANNED', 'RELEASED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS inventory_movements (
    id INTEGER PRIMARY KEY,
    part_id INTEGER NOT NULL REFERENCES parts(id),
    movement_date TEXT NOT NULL,
    movement_type TEXT NOT NULL CHECK(movement_type IN ('RECEIPT', 'ISSUE', 'TRANSFER', 'ADJUSTMENT', 'SCRAP')),
    quantity REAL NOT NULL,
    reference_document TEXT,
    location_from TEXT,
    location_to TEXT,
    unit_cost REAL
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_parts_category ON parts(part_category);
CREATE INDEX IF NOT EXISTS idx_bom_parent ON bill_of_materials(parent_part_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_part ON work_orders(part_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_date ON work_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_part ON inventory_movements(part_id);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_date ON inventory_movements(movement_date);