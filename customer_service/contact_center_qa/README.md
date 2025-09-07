# contact_center_qa

## Entities
- conversations
- turns
- intents
- resolutions

## Distinctiveness
Evaluates conversation quality and compliance to scripts.

## Indexes
- `turns(conversation_id, ts)`
- `resolutions(conversation_id)`

## Expected Row Counts
- conversations: 1k
- turns: 50k

## Efficiency Notes
Time-based index supports quick turn retrievals.
