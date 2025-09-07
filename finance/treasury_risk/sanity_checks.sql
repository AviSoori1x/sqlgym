-- aggregate exposures by desk
SELECT d.name, SUM(e.amount) AS total_exposure
FROM desks d JOIN exposures e ON d.id=e.desk_id
GROUP BY d.id;

-- join breaches with limits
SELECT b.id, l.limit_type, b.breached_on
FROM breaches b JOIN limits l ON b.limit_id=l.id;

-- scenario averages
SELECT s.name, AVG(e.amount) AS avg_exp
FROM scenarios s JOIN exposures e ON s.id=e.scenario_id
GROUP BY s.id;
