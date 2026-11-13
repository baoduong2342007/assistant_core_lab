-- Lab 5 Part F & H2: Queries for the assistant database.

-- Q1 (F1): requests per intent
SELECT intent, COUNT(*) AS request_count
FROM interaction
GROUP BY intent
ORDER BY request_count DESC;

-- Q2 (F2): average latency per intent (in milliseconds, rounded to 2 decimals)
SELECT intent, ROUND(AVG(latency_ms), 2) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC;

-- Q3 (F3): topics with the most thumbs-down ratings (JOIN feedback with interaction)
SELECT i.topic, COUNT(*) AS thumbs_down_count
FROM feedback f
JOIN interaction i ON f.request_id = i.request_id
WHERE f.rating = -1 AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down_count DESC;

-- H2: Reliability and performance audit per intent (total requests, unresolved rate, degraded count, average latency)
SELECT
    intent,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN resolved = 0 THEN 1 ELSE 0 END) AS unresolved_count,
    ROUND(AVG(CASE WHEN resolved = 0 THEN 1.0 ELSE 0.0 END) * 100, 2) AS unresolved_rate_pct,
    SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) AS degraded_count,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY total_requests DESC;
