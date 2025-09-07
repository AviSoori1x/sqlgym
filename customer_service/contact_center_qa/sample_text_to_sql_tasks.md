# Sample Tasks for contact_center_qa

## Task 1: unresolved conversations
**User**: List unresolved conversations.
**Assistant**: Join conversations with resolutions.
```sql
SELECT c.id FROM conversations c LEFT JOIN resolutions r ON c.id=r.conversation_id WHERE r.resolved=0;
```

## Task 2: evidence script
**User**: What script should agents follow?
**Assistant**: Read agent_scripts.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='agent_scripts'), '$');
```

## Task 3: efficiency turn lookup
**User**: Get turns for conversation 5 on a date.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM turns WHERE conversation_id=5 AND ts>'2024-01-01';
```
```sql slow
SELECT * FROM turns WHERE conversation_id=5 AND substr(ts,1,10)>'2024-01-01';
```
