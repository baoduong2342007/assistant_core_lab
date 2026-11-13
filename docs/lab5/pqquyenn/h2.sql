-- No feedback JOIN: requests with zero/multiple ratings each contribute once.
SELECT
    intent,
    COUNT(*) AS request_count,
    SUM(CASE WHEN resolved = 0 THEN 1 ELSE 0 END) AS unresolved_count,
    ROUND(100.0 * SUM(CASE WHEN resolved = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS unresolved_rate_pct,
    SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) AS degraded_count,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY unresolved_rate_pct DESC, request_count DESC, intent;
