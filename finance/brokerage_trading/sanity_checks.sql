-- 1. count instruments
SELECT COUNT(*) FROM instruments;
-- 2. unique symbols
SELECT COUNT(DISTINCT symbol) FROM instruments;
-- 3. orders per instrument
SELECT instrument_id, COUNT(*) FROM orders GROUP BY instrument_id;
-- 4. executions join orders
SELECT COUNT(*) FROM executions e JOIN orders o ON e.order_id=o.id;
-- 5. trades join executions
SELECT COUNT(*) FROM trades t JOIN executions e ON t.execution_id=e.id;
-- 6. open orders
SELECT COUNT(*) FROM orders WHERE status='OPEN';
-- 7. trades per day
SELECT substr(trade_time,1,10) d, COUNT(*) FROM trades GROUP BY d;
-- 8. venue order counts
SELECT venue_id, COUNT(*) FROM orders GROUP BY venue_id;
-- 9. check fk violation attempt (should return 0 rows)
SELECT COUNT(*) FROM trades WHERE instrument_id NOT IN (SELECT id FROM instruments);
--10. total traded quantity per instrument
SELECT instrument_id, SUM(quantity) FROM trades GROUP BY instrument_id;
