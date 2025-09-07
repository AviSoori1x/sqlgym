# Workflow Tasks for ticketing_sla

## Workflow 1: create ticket and log interaction
1. Insert ticket row.
2. Insert interaction by agent.
3. Query open ticket count.

## Workflow 2: close ticket
1. Update ticket status to CLOSED.
2. Set closed_at timestamp.
3. Verify via query it is closed.
