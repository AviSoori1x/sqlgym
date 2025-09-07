# Sample Tasks for asset_mgmt_fund_accounting

## Task 1: list funds
**User**: Show all fund names.
**Assistant**: Simple select.
```sql
SELECT name FROM funds;
```

## Task 2: evidence NAV method
**User**: What's the NAV method per valuation_policy.json?
**Assistant**: Read from evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='valuation_policy'), '$.nav_method');
```

## Task 3: indexed holdings lookup
**User**: Get holdings for fund 1 on 2024-01-02.
**Assistant**: Fast uses composite index; slow uses substr.
```sql fast
SELECT * FROM holdings WHERE fund_id=1 AND position_date='2024-01-02';
```
```sql slow
SELECT * FROM holdings WHERE fund_id||''='1' AND substr(position_date,1,10)='2024-01-02';
```

## Task 4: investor tiers
**User**: List institutional investors.
**Assistant**: Filter by tier.
```sql
SELECT name FROM investors WHERE tier='INSTITUTIONAL';
```

## Task 5: fund subscriptions
**User**: Which investors are in fund 2?
**Assistant**: Join subscriptions and investors.
```sql
SELECT i.name FROM subscriptions s JOIN investors i ON s.investor_id=i.id WHERE s.fund_id=2;
```

## Task 6: evidence valuation time
**User**: When do valuations occur?
**Assistant**: Retrieve from JSON.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='valuation_policy'), '$.valuation_time');
```

## Task 7: efficiency investor count
**User**: How many retail investors?
**Assistant**: Fast uses indexed tier; slow uses LIKE.
```sql fast
SELECT name FROM investors WHERE tier='RETAIL';
```
```sql slow
SELECT name FROM investors WHERE substr(tier,1,6)='RETAIL';
```

## Task 8: security list
**User**: List equity securities.
**Assistant**: Filter by type.
```sql
SELECT symbol FROM securities WHERE type='EQUITY';
```

## Task 9: holdings quantity sum
**User**: Total quantity of SEC001 across funds.
**Assistant**: Sum quantities.
```sql
SELECT SUM(quantity) FROM holdings h JOIN securities s ON h.security_id=s.id WHERE s.symbol='SEC001';
```

## Task 10: evidence asset types
**User**: Which asset types are allowed?
**Assistant**: Use evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='valuation_policy'), '$.allowed_asset_types');
```

## Task 11: monthly holdings range
**User**: Show fund 1 holdings for January.
**Assistant**: Fast uses BETWEEN; slow uses strftime.
```sql fast
SELECT * FROM holdings WHERE fund_id=1 AND position_date BETWEEN '2024-01-01' AND '2024-01-31';
```
```sql slow
SELECT * FROM holdings WHERE fund_id||''='1' AND strftime('%m', position_date)='01';
```

## Task 12: efficiency symbol search
**User**: Show holdings for SEC002.
**Assistant**: Fast equality vs slow pattern.
```sql fast
SELECT * FROM holdings h JOIN securities s ON h.security_id=s.id WHERE s.symbol='SEC002';
```
```sql slow
SELECT * FROM holdings h JOIN securities s ON h.security_id=s.id WHERE substr(s.symbol,1,6)='SEC002';
```

## Task 13: unsubscribed investors
**User**: Which investors have no subscriptions?
**Assistant**: Left join and filter null.
```sql
SELECT i.name FROM investors i LEFT JOIN subscriptions s ON i.id=s.investor_id GROUP BY i.id HAVING COUNT(s.id)=0;
```

## Task 14: fund domiciles
**User**: Count funds by domicile.
**Assistant**: Group by.
```sql
SELECT domicile, COUNT(*) FROM funds GROUP BY domicile;
```

## Task 15: evidence raw policy
**User**: Return raw valuation policy text.
**Assistant**: Extract entire JSON.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='valuation_policy'), '$');
```
