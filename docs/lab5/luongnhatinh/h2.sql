-- H2: Reliability and performance audit per intent
-- Aggregates total requests, failure (unresolved) rate, degraded responses, and latency metrics.

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
