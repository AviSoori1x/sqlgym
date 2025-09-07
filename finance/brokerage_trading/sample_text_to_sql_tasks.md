# Sample Tasks for brokerage_trading

## Task 1: open orders
**User**: Show open orders for instrument 1 at venue 1.
**Assistant**: Filter orders by instrument, venue and status.
```sql
SELECT id, quantity FROM orders WHERE instrument_id=1 AND venue_id=1 AND status='OPEN';
```

## Task 2: evidence policy
**User**: What is the settlement rule?
**Assistant**: Read trade_policy.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='trade_policy'), '$');
```

## Task 3: efficiency trade lookup
**User**: Trades for instrument 2 on 2024-01-03.
**Assistant**: Fast query uses composite index; slow uses function.
```sql fast
SELECT * FROM trades WHERE instrument_id=2 AND trade_time='2024-01-03';
```
```sql slow
SELECT * FROM trades WHERE instrument_id=2 AND substr(trade_time,1,10)='2024-01-03';
```

