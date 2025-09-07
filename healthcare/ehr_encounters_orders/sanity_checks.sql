-- encounter counts
SELECT patient_id, COUNT(*) FROM encounters GROUP BY patient_id;

-- order to result lag
SELECT o.id, JULIANDAY(r.result_time)-JULIANDAY(o.order_time) AS lag
FROM orders o JOIN results r ON o.id=r.order_id;

-- pending results
SELECT COUNT(*) FROM results WHERE status='PENDING';
