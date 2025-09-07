# [subdomain_name]

## Overview
[Brief description of what this subdomain models - 2-3 sentences about the business domain and key use cases]

## Entities

### Normalized Schema
- **[table1]**: [Brief description of purpose and key fields]
- **[table2]**: [Brief description of purpose and key fields]  
- **[table3]**: [Brief description of purpose and key fields]
- **[table4]**: [Brief description of purpose and key fields]
- **[table5]**: [Brief description of purpose and key fields]

### Denormalized Schema
- **[analytical_table1]**: [Description of pre-calculated metrics and analysis purpose]
- **[analytical_table2]**: [Description of aggregations and reporting use cases]
- **[analytical_table3]**: [Description of performance metrics and KPIs]
- **[analytical_table4]**: [Description of time-series or cohort analysis]

## Key Indexes
- `idx_[table]_[field]`: [Description of what queries this optimizes]
- `idx_[table]_[field]`: [Description of query patterns this supports]
- `idx_[table]_[field]`: [Description of performance benefits]
- `idx_[table]_[field]`: [Description of analytical query optimization]
- `idx_[table]_[field]`: [Description of reporting query efficiency]

## Efficiency Notes
- [Key design decision 1 and its performance impact]
- [Key design decision 2 and its scalability benefit]  
- [Important constraint or business rule implementation]
- [Evidence file integration and JSON usage patterns]
- [Fast/slow pair examples demonstrating index usage vs table scans]

---

## TEMPLATE INSTRUCTIONS:

1. **Replace all bracketed placeholders** with actual content:
   - [subdomain_name] → actual subdomain name
   - [table1], [table2] → actual table names
   - [Brief description] → actual descriptions

2. **Normalized Schema section**:
   - List 3-5 main tables
   - Focus on business entities and relationships
   - Mention key constraints and business rules

3. **Denormalized Schema section**:
   - List 3-4 analytical tables
   - Emphasize pre-calculated metrics
   - Highlight reporting and dashboard use cases

4. **Key Indexes section**:
   - List 5-7 most important indexes
   - Explain query patterns they optimize
   - Focus on performance-critical operations

5. **Efficiency Notes**:
   - Highlight 4-5 key design decisions
   - Mention JSON usage for flexibility
   - Reference evidence file integration
   - Note index usage patterns in fast/slow pairs

6. **Keep it concise** - aim for ~30-40 lines total
