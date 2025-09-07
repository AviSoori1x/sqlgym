-- Template: Sanity checks for retail CPG subdomains
-- INSTRUCTIONS: Copy this template and adapt for each subdomain

-- REFERENTIAL INTEGRITY CHECKS (adapt table/column names)
-- 1. All child records reference valid parent records
SELECT COUNT(*) FROM child_table c LEFT JOIN parent_table p ON c.parent_id = p.id WHERE p.id IS NULL;

-- 2. All foreign key relationships are valid
SELECT COUNT(*) FROM table_a a LEFT JOIN table_b b ON a.foreign_key = b.id WHERE a.foreign_key IS NOT NULL AND b.id IS NULL;

-- ENUM VALIDATION CHECKS (adapt enum values for each domain)
-- 3. Status enum validation
SELECT COUNT(*) FROM main_table WHERE status NOT IN ('VALUE1', 'VALUE2', 'VALUE3');

-- 4. Type enum validation  
SELECT COUNT(*) FROM main_table WHERE type NOT IN ('TYPE1', 'TYPE2', 'TYPE3');

-- 5. Category enum validation
SELECT COUNT(*) FROM main_table WHERE category NOT IN ('CAT1', 'CAT2', 'CAT3');

-- DATA QUALITY CHECKS
-- 6. Required fields are not null
SELECT COUNT(*) FROM main_table WHERE required_field IS NULL;

-- 7. Numeric ranges are valid
SELECT COUNT(*) FROM main_table WHERE numeric_field < 0 OR numeric_field > 100;

-- 8. Email format validation (if applicable)
SELECT COUNT(*) FROM main_table WHERE email IS NOT NULL AND email NOT LIKE '%@%.%';

-- 9. Date logic validation
SELECT COUNT(*) FROM main_table WHERE end_date IS NOT NULL AND end_date <= start_date;

-- UNIQUENESS CONSTRAINTS
-- 10. Unique identifiers
SELECT identifier, COUNT(*) FROM main_table GROUP BY identifier HAVING COUNT(*) > 1;

-- 11. Composite unique constraints
SELECT field1, field2, COUNT(*) FROM main_table GROUP BY field1, field2 HAVING COUNT(*) > 1;

-- JSON VALIDATION (if applicable)
-- 12. JSON fields are valid
SELECT COUNT(*) FROM main_table WHERE json_field IS NOT NULL AND json_valid(json_field) = 0;

-- BUSINESS LOGIC VALIDATION
-- 13. Business rule validation (adapt to domain)
SELECT COUNT(*) FROM main_table WHERE business_condition_violated;

-- 14. Cross-table consistency
SELECT COUNT(*) FROM table_a a JOIN table_b b ON a.id = b.foreign_id WHERE inconsistent_condition;

-- PERFORMANCE INDEX VERIFICATION
-- 15. EXPLAIN - Verify index usage for primary queries
EXPLAIN QUERY PLAN SELECT * FROM main_table WHERE indexed_field = 'value';

-- 16. EXPLAIN - Verify index usage for date range queries  
EXPLAIN QUERY PLAN SELECT * FROM main_table WHERE date_field >= '2024-01-01' AND date_field < '2024-02-01';

-- ADD MORE CHECKS SPECIFIC TO YOUR DOMAIN (aim for 20-25 total)
