PRAGMA foreign_keys=OFF;
CREATE TABLE claim_summary AS
SELECT c.id AS claim_id, p.name AS patient_name, c.claim_date, c.status,
       cl.code, cl.amount, a.status AS adj_status, d.reason
FROM claims c
JOIN patients p ON c.patient_id=p.id
JOIN claim_lines cl ON cl.claim_id=c.id
LEFT JOIN adjudications a ON a.claim_line_id=cl.id
LEFT JOIN denials d ON d.claim_id=c.id;
