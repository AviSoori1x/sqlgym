# chatbot_deflection

## Overview
This subdomain models chatbot interactions, intent detection, and escalation patterns for customer service automation.

## Entities

### Normalized Schema
- **customers**: Customer accounts with unique emails
- **intent_categories**: Bot-recognizable intents with deflection capability and priority
- **conversations**: Chat sessions across multiple channels (web, mobile, SMS, voice)
- **messages**: Individual messages with sender type, content, and confidence scores
- **escalations**: Records when bots hand off to human agents with reasons

### Denormalized Schema
- **conversation_analytics**: Pre-aggregated conversation metrics for reporting
- **daily_deflection_metrics**: Daily performance metrics by channel
- **intent_performance**: Monthly intent-level success rates

## Key Indexes
- `idx_conversations_status`: Fast status filtering for deflection calculations
- `idx_conversations_started`: Efficient date range queries
- `idx_messages_conversation`: Quick message retrieval by conversation
- `idx_escalations_reason`: Analysis of escalation patterns

## Efficiency Notes
- Indexes created after bulk data loading for optimal insert performance
- Evidence loaded via JSON1 functions for policy/guideline queries
- Denormalized tables pre-aggregate metrics to avoid expensive runtime calculations
- Fast/slow query pairs demonstrate index usage vs table scans
