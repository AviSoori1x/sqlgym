-- Sanity checks for fund accounting
SELECT CASE WHEN COUNT(*)=3 THEN 1 ELSE 1/0 END FROM funds;
SELECT CASE WHEN COUNT(*)=5 THEN 1 ELSE 1/0 END FROM investors;
SELECT CASE WHEN COUNT(*)=5 THEN 1 ELSE 1/0 END FROM securities;
SELECT CASE WHEN COUNT(*)=0 THEN 1 ELSE 1/0 END FROM holdings WHERE quantity<=0;
SELECT CASE WHEN COUNT(*)=0 THEN 1 ELSE 1/0 END FROM holdings h LEFT JOIN funds f ON h.fund_id=f.id WHERE f.id IS NULL;
SELECT CASE WHEN COUNT(*)=0 THEN 1 ELSE 1/0 END FROM investors WHERE tier NOT IN ('RETAIL','INSTITUTIONAL');
SELECT CASE WHEN COUNT(*)=0 THEN 1 ELSE 1/0 END FROM securities WHERE type NOT IN ('EQUITY','BOND','CASH');
SELECT CASE WHEN COUNT(*)=5 THEN 1 ELSE 1/0 END FROM subscriptions;
SELECT CASE WHEN COUNT(*)=0 THEN 1 ELSE 1/0 END FROM subscriptions s LEFT JOIN investors i ON s.investor_id=i.id WHERE i.id IS NULL;
SELECT CASE WHEN COUNT(*)=0 THEN 1 ELSE 1/0 END FROM funds f LEFT JOIN subscriptions s ON f.id=s.fund_id GROUP BY f.id HAVING COUNT(s.id)=0;
SELECT CASE WHEN COUNT(*)=0 THEN 1 ELSE 1/0 END FROM (SELECT fund_id, security_id, position_date, COUNT(*) c FROM holdings GROUP BY fund_id, security_id, position_date HAVING c>1);
SELECT CASE WHEN MIN(position_date)>='2024-01-01' THEN 1 ELSE 1/0 END FROM holdings;
