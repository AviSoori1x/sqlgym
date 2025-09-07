-- claim totals
SELECT claim_id, SUM(amount) FROM claim_lines GROUP BY claim_id;

-- adjudication status counts
SELECT status, COUNT(*) FROM adjudications GROUP BY status;

-- denials per plan
SELECT c.plan_id, COUNT(d.id) FROM claims c LEFT JOIN denials d ON c.id=d.claim_id GROUP BY c.plan_id;
