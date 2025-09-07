-- appointments per provider
SELECT provider_id, COUNT(*) FROM appointments GROUP BY provider_id;
