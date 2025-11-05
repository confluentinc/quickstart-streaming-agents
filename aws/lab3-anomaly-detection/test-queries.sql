-- ============================================================
-- Lab3 Anomaly Detection - Test Queries for ShadowTraffic
-- ============================================================
-- These queries test whether the dropAndCreate policy is working
-- and that both ride_requests and vessel_catalog are being populated
-- ============================================================

-- CREATE TABLE statements (run these first if tables don't exist)
-- ============================================================

CREATE TABLE `ride_requests` (
  `request_id` VARCHAR(2147483647) NOT NULL,
  `customer_email` VARCHAR(2147483647) NOT NULL,
  `pickup_zone` VARCHAR(2147483647) NOT NULL,
  `drop_off_zone` VARCHAR(2147483647) NOT NULL,
  `price` DOUBLE NOT NULL,
  `number_of_passengers` INT NOT NULL,
  `request_ts` TIMESTAMP(3) WITH LOCAL TIME ZONE NOT NULL,
  WATERMARK FOR `request_ts` AS `request_ts` - INTERVAL '5' SECOND
);

CREATE TABLE `vessel_catalog` (
  `vessel_id` VARCHAR(2147483647) NOT NULL,
  `vessel_name` VARCHAR(2147483647) NOT NULL,
  `base_zone` VARCHAR(2147483647) NOT NULL,
  `availability` VARCHAR(2147483647) NOT NULL,
  `capacity` INT NOT NULL
);

-- 1. Verify tables exist
-- ============================================================
SHOW TABLES;


-- 2. Check ride_requests table structure and data
-- ============================================================

-- View sample ride requests
SELECT
    request_id,
    customer_email,
    pickup_zone,
    drop_off_zone,
    price,
    number_of_passengers,
    request_ts
FROM ride_requests
LIMIT 10;

-- Count total ride requests
SELECT COUNT(*) as total_ride_requests
FROM ride_requests;

-- Check ride request distribution by pickup zone
SELECT
    pickup_zone,
    COUNT(*) as request_count,
    AVG(price) as avg_price,
    AVG(number_of_passengers) as avg_passengers
FROM ride_requests
GROUP BY pickup_zone
ORDER BY request_count DESC;

-- Check latest ride requests (verify fresh data)
SELECT
    request_id,
    customer_email,
    pickup_zone,
    drop_off_zone,
    request_ts
FROM ride_requests
ORDER BY request_ts DESC
LIMIT 10;


-- 3. Check vessel_catalog table structure and data
-- ============================================================

-- View all vessels
SELECT
    vessel_id,
    vessel_name,
    base_zone,
    availability,
    capacity
FROM vessel_catalog
LIMIT 50;

-- Count total vessels (should be 50 based on maxEvents)
SELECT COUNT(*) as total_vessels
FROM vessel_catalog;

-- Check vessel distribution by base zone
SELECT
    base_zone,
    COUNT(*) as vessel_count,
    AVG(capacity) as avg_capacity
FROM vessel_catalog
GROUP BY base_zone
ORDER BY vessel_count DESC;

-- Check vessel availability status
SELECT
    availability,
    COUNT(*) as count,
    AVG(capacity) as avg_capacity
FROM vessel_catalog
GROUP BY availability;


-- 4. Join queries to verify data relationships
-- ============================================================

-- Find vessels in the same zone as ride pickups
SELECT
    r.request_id,
    r.pickup_zone,
    r.number_of_passengers,
    v.vessel_id,
    v.vessel_name,
    v.availability,
    v.capacity
FROM ride_requests r
JOIN vessel_catalog v ON r.pickup_zone = v.base_zone
WHERE v.availability = 'available'
  AND v.capacity >= r.number_of_passengers
LIMIT 20;

-- Count available vessels per zone with active ride requests
SELECT
    r.pickup_zone,
    COUNT(DISTINCT r.request_id) as ride_count,
    COUNT(DISTINCT v.vessel_id) as available_vessel_count
FROM ride_requests r
LEFT JOIN vessel_catalog v
    ON r.pickup_zone = v.base_zone
    AND v.availability = 'available'
GROUP BY r.pickup_zone
ORDER BY ride_count DESC;


-- 5. Data quality checks
-- ============================================================

-- Verify price ranges (should be 50-150)
SELECT
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(price) as avg_price
FROM ride_requests;

-- Verify passenger counts (should be 1-5)
SELECT
    MIN(number_of_passengers) as min_passengers,
    MAX(number_of_passengers) as max_passengers,
    AVG(number_of_passengers) as avg_passengers
FROM ride_requests;

-- Verify vessel capacity ranges (should be 5-10)
SELECT
    MIN(capacity) as min_capacity,
    MAX(capacity) as max_capacity,
    AVG(capacity) as avg_capacity
FROM vessel_catalog;

-- Check for NULL values in critical fields
SELECT
    COUNT(*) as total_rows,
    SUM(CASE WHEN request_id IS NULL THEN 1 ELSE 0 END) as null_request_ids,
    SUM(CASE WHEN customer_email IS NULL THEN 1 ELSE 0 END) as null_emails,
    SUM(CASE WHEN pickup_zone IS NULL THEN 1 ELSE 0 END) as null_pickup_zones,
    SUM(CASE WHEN request_ts IS NULL THEN 1 ELSE 0 END) as null_timestamps
FROM ride_requests;


-- 6. Real-time monitoring queries
-- ============================================================

-- Monitor ride requests per minute
SELECT
    TUMBLE_START(request_ts, INTERVAL '1' MINUTE) as window_start,
    COUNT(*) as requests_per_minute,
    AVG(price) as avg_price
FROM ride_requests
GROUP BY TUMBLE(request_ts, INTERVAL '1' MINUTE)
ORDER BY window_start DESC
LIMIT 10;

-- Find high-value rides (potential anomalies)
SELECT
    request_id,
    customer_email,
    pickup_zone,
    drop_off_zone,
    price,
    request_ts
FROM ride_requests
WHERE price > 130
ORDER BY price DESC
LIMIT 10;

-- Find zones with capacity constraints
SELECT
    v.base_zone,
    COUNT(DISTINCT v.vessel_id) FILTER (WHERE v.availability = 'available') as available_vessels,
    COUNT(DISTINCT v.vessel_id) as total_vessels,
    COUNT(DISTINCT r.request_id) as pending_requests
FROM vessel_catalog v
LEFT JOIN ride_requests r ON v.base_zone = r.pickup_zone
GROUP BY v.base_zone
HAVING COUNT(DISTINCT r.request_id) > COUNT(DISTINCT v.vessel_id) FILTER (WHERE v.availability = 'available')
ORDER BY pending_requests DESC;
