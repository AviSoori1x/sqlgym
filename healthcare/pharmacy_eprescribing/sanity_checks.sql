-- fills per prescription
SELECT prescription_id, COUNT(*) FROM fills GROUP BY prescription_id;
