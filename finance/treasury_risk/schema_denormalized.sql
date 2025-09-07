PRAGMA foreign_keys=OFF;
CREATE TABLE exposure_limits AS
SELECT e.id AS exposure_id, d.name AS desk_name, s.name AS scenario_name,
       e.as_of, e.amount AS exposure_amount, l.limit_type, l.amount AS limit_amount
FROM exposures e
JOIN desks d ON e.desk_id=d.id
JOIN scenarios s ON e.scenario_id=s.id
JOIN limits l ON l.desk_id=e.desk_id;
