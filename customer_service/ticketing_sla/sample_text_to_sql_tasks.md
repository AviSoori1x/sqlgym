# Sample Tasks for ticketing_sla

## Task 1: open tickets count
**User**: How many open tickets exist?
**Assistant**: Count tickets with status OPEN.
```sql
SELECT COUNT(*) FROM tickets WHERE status='OPEN';
```

## Task 2: evidence SLA hours
**User**: What is gold response time per sla_policy.json?
**Assistant**: Fetch from evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='sla_policy'), '$.gold_response_hours');
```

## Task 3: efficiency pair date filter
**User**: List tickets opened on 2024-01-02.
**Assistant**: Fast uses index; slow uses substr.
```sql fast
SELECT id FROM tickets WHERE opened_at='2024-01-02';
```
```sql slow
SELECT id FROM tickets WHERE substr(opened_at,1,10)='2024-01-02';
```

## Task 4: evidence closing guidelines
**User**: What must agents verify before closing?
**Assistant**: Read closing_guidelines.md.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='closing_guidelines'), '$');
```

## Task 5: agent ticket load
**User**: Tickets handled by agent 1?
**Assistant**: Filter tickets by agent_id.
```sql
SELECT COUNT(*) FROM tickets WHERE agent_id=1;
```

## Task 6: priority distribution
**User**: Show count by priority.
**Assistant**: group by priority.
```sql
SELECT priority, COUNT(*) FROM tickets GROUP BY priority;
```

## Task 7: efficiency pair status filter
**User**: Count closed tickets.
**Assistant**: Index vs LIKE.
```sql fast
SELECT COUNT(*) FROM tickets WHERE status='CLOSED';
```
```sql slow
SELECT COUNT(*) FROM tickets WHERE status LIKE 'CLOSED';
```

## Task 8: evidence standard SLA
**User**: What's the standard response SLA?
**Assistant**: Query JSON.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='sla_policy'), '$.standard_response_hours');
```

## Task 9: tickets without agent
**User**: List tickets with no assigned agent.
**Assistant**: agent_id IS NULL.
```sql
SELECT id FROM tickets WHERE agent_id IS NULL;
```

## Task 10: interactions count
**User**: How many interactions per ticket?
**Assistant**: aggregate interactions.
```sql
SELECT ticket_id, COUNT(*) FROM interactions GROUP BY ticket_id;
```

## Task 11: evidence guidelines text
**User**: Return closing guidelines text.
**Assistant**: json_extract.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='closing_guidelines'), '$');
```

## Task 12: efficiency pair interaction order
**User**: Get interactions for ticket 1 ordered by time.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM interactions WHERE ticket_id=1 ORDER BY interacted_at;
```
```sql slow
SELECT * FROM interactions WHERE ticket_id=1 ORDER BY substr(interacted_at,1,19);
```

## Task 13: tickets per SLA
**User**: Count tickets per SLA.
**Assistant**: join service_levels.
```sql
SELECT s.name, COUNT(*) FROM tickets t JOIN service_levels s ON t.sl_id=s.id GROUP BY s.id;
```

## Task 14: evidence SLA comparison
**User**: Is gold faster than standard per policy?
**Assistant**: Compare values.
```sql
SELECT json_extract(v.value,'$.gold_response_hours') < json_extract(v.value,'$.standard_response_hours')
FROM evidence_kv v WHERE v.key='sla_policy';
```

## Task 15: unresolved high priority
**User**: List HIGH priority tickets not closed.
**Assistant**: filter status!='CLOSED'.
```sql
SELECT id FROM tickets WHERE priority='HIGH' AND status!='CLOSED';
```
