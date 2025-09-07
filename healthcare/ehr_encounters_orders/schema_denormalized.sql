PRAGMA foreign_keys=OFF;
CREATE TABLE order_results AS
SELECT o.id AS order_id, e.patient_id, o.order_time, o.status AS order_status,
       r.result_time, r.status AS result_status
FROM orders o
JOIN encounters e ON o.encounter_id=e.id
LEFT JOIN results r ON r.order_id=o.id;
