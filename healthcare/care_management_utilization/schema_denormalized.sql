PRAGMA foreign_keys=OFF;
CREATE TABLE care_summary AS
SELECT m.name AS member_name, p.name AS program_name,
       i.intervention_date, i.type, o.outcome
FROM enrollments e
JOIN members m ON m.id=e.member_id
JOIN care_programs p ON p.id=e.program_id
JOIN interventions i ON i.enrollment_id=e.id
JOIN outcomes o ON o.intervention_id=i.id;
CREATE INDEX idx_care_summary_member ON care_summary(member_name);
