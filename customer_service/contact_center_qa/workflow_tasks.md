# Workflow for contact_center_qa

```sql
-- step: convo_duration
CREATE TEMP TABLE durations AS
SELECT c.id, MIN(t.ts) AS start, MAX(t.ts) AS end FROM conversations c JOIN turns t ON c.id=t.conversation_id GROUP BY c.id;

-- step: joined
-- depends: convo_duration
SELECT d.id, d.start, d.end, r.resolved FROM durations d LEFT JOIN resolutions r ON d.id=r.conversation_id;
```
