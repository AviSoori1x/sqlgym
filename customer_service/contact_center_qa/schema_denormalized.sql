PRAGMA foreign_keys=OFF;
CREATE TABLE convo_turns AS
SELECT c.id AS convo_id, c.customer_id, t.speaker, t.utterance, t.ts,
       r.resolved, r.resolution_time
FROM conversations c
JOIN turns t ON t.conversation_id=c.id
LEFT JOIN resolutions r ON r.conversation_id=c.id;
