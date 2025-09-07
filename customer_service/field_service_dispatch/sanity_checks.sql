-- Sanity checks for field service dispatch domain

-- 1. All service requests reference valid customers
SELECT COUNT(*) FROM service_requests sr LEFT JOIN customers c ON sr.customer_id = c.id WHERE c.id IS NULL;

-- 2. All appointments reference valid service requests
SELECT COUNT(*) FROM appointments a LEFT JOIN service_requests sr ON a.service_request_id = sr.id WHERE sr.id IS NULL;

-- 3. All appointments reference valid technicians
SELECT COUNT(*) FROM appointments a LEFT JOIN technicians t ON a.technician_id = t.id WHERE t.id IS NULL;

-- 4. All dispatch events reference valid appointments
SELECT COUNT(*) FROM dispatch_events de LEFT JOIN appointments a ON de.appointment_id = a.id WHERE a.id IS NULL;

-- 5. Customer service level enum validation
SELECT COUNT(*) FROM customers WHERE service_level NOT IN ('STANDARD', 'PRIORITY', 'VIP');

-- 6. Technician certification level enum validation
SELECT COUNT(*) FROM technicians WHERE certification_level NOT IN ('APPRENTICE', 'JOURNEYMAN', 'MASTER');

-- 7. Technician status enum validation
SELECT COUNT(*) FROM technicians WHERE status NOT IN ('ACTIVE', 'ON_LEAVE', 'TERMINATED');

-- 8. Service request type enum validation
SELECT COUNT(*) FROM service_requests WHERE request_type NOT IN ('INSTALL', 'REPAIR', 'MAINTENANCE', 'INSPECTION', 'EMERGENCY');

-- 9. Service request priority enum validation
SELECT COUNT(*) FROM service_requests WHERE priority NOT IN ('LOW', 'MEDIUM', 'HIGH', 'EMERGENCY');

-- 10. Service request status enum validation
SELECT COUNT(*) FROM service_requests WHERE status NOT IN ('PENDING', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');

-- 11. Time window enum validation
SELECT COUNT(*) FROM service_requests WHERE time_window NOT IN ('MORNING', 'AFTERNOON', 'EVENING', 'ANYTIME');

-- 12. Appointment status enum validation
SELECT COUNT(*) FROM appointments WHERE status NOT IN ('SCHEDULED', 'EN_ROUTE', 'ON_SITE', 'COMPLETED', 'MISSED', 'RESCHEDULED');

-- 13. Dispatch event type enum validation
SELECT COUNT(*) FROM dispatch_events WHERE event_type NOT IN ('ASSIGNED', 'REASSIGNED', 'STARTED_TRAVEL', 'ARRIVED', 'COMPLETED', 'CUSTOMER_NOT_HOME', 'RESCHEDULED');

-- 14. Valid coordinates check
SELECT COUNT(*) FROM customers WHERE latitude < -90 OR latitude > 90 OR longitude < -180 OR longitude > 180;

-- 15. Technician coordinates check
SELECT COUNT(*) FROM technicians WHERE home_latitude < -90 OR home_latitude > 90 OR home_longitude < -180 OR home_longitude > 180;

-- 16. One appointment per service request
SELECT service_request_id, COUNT(*) FROM appointments GROUP BY service_request_id HAVING COUNT(*) > 1;

-- 17. Scheduled appointments should have scheduled times
SELECT COUNT(*) FROM appointments WHERE status = 'SCHEDULED' AND (scheduled_start_time IS NULL OR scheduled_end_time IS NULL);

-- 18. Completed appointments should have actual times
SELECT COUNT(*) FROM appointments WHERE status = 'COMPLETED' AND (actual_start_time IS NULL OR actual_end_time IS NULL);

-- 19. Skills required should be valid JSON
SELECT COUNT(*) FROM service_requests WHERE json_valid(skills_required) = 0;

-- 20. Technician skill set should be valid JSON
SELECT COUNT(*) FROM technicians WHERE json_valid(skill_set) = 0;

-- 21. EXPLAIN - Verify index usage for date range queries
EXPLAIN QUERY PLAN SELECT * FROM service_requests WHERE requested_date = '2024-01-15';

-- 22. EXPLAIN - Verify index usage for technician schedule lookup
EXPLAIN QUERY PLAN SELECT * FROM appointments WHERE technician_id = 50 AND scheduled_date = '2024-01-15';

-- 23. EXPLAIN - Verify spatial index usage
EXPLAIN QUERY PLAN SELECT * FROM customers WHERE latitude BETWEEN 37.5 AND 37.6 AND longitude BETWEEN -122.0 AND -121.9;