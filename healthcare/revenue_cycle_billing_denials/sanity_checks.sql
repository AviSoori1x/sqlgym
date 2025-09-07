-- bill item totals
SELECT bill_id, SUM(amount) FROM bill_items GROUP BY bill_id;
