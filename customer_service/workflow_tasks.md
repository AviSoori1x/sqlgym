# Workflow Tasks

## Task: conversation quality rollup
```sql
-- step: base
CREATE TEMP TABLE base AS
SELECT conversation_id, AVG(score) s FROM qa_scores GROUP BY conversation_id;
```
```sql
-- step: flag
-- depends: base
CREATE TEMP TABLE flag AS
SELECT conversation_id FROM base WHERE s<0.8;
```
```sql
-- step: final
-- depends: flag
SELECT COUNT(*) FROM flag;
```

## Task: ticket aging
```sql
-- step: open
CREATE TEMP TABLE open AS
SELECT id, opened_at FROM tickets WHERE status='OPEN';
```
```sql
-- step: aged
-- depends: open
SELECT id FROM open WHERE opened_at<'2024-01-05';
```

