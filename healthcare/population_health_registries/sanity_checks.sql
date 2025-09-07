-- registry enrollment counts
SELECT registry_id, COUNT(*) FROM enrollments GROUP BY registry_id;
