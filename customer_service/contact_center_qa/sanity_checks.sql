-- turn count per convo
SELECT conversation_id, COUNT(*) FROM turns GROUP BY conversation_id;

-- resolution rate
SELECT AVG(resolved) FROM resolutions;

-- intents used
SELECT intent_id, COUNT(*) FROM turns GROUP BY intent_id;
