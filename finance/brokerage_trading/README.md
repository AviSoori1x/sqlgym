# brokerage_trading

Normalized schema captures instruments, venues, orders, executions and trades for
a brokerage platform. Orders enforce side/type/status via CHECK constraints and
use composite indexes for query efficiency.

## Entities
- `instruments`: tradable symbols, UNIQUE symbol.
- `venues`: market venues, UNIQUE name.
- `orders`: client orders with side/type/status lifecycle.
- `executions`: partial fills of orders.
- `trades`: executions tied to instruments.

## Indexes
- `idx_orders_instr_time` on `(instrument_id, created_at)`
- `idx_exec_order` on `(order_id)`
- `idx_trade_instr_time` on `(instrument_id, trade_time)`

## Scale
SCALE constants target ~5 instruments, 2 venues, 20 orders and 40 executions.

## Efficiency Notes
Queries filter by instrument and time; indexes above support fast access while
slow queries demonstrate sequential scans.

