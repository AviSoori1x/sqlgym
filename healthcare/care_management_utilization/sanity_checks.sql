-- program enrollment counts
SELECT program_id, COUNT(*) FROM enrollments GROUP BY program_id;
