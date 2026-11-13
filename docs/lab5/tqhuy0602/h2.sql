-- Which handbook topics have the highest rate of degraded responses?
SELECT
    topic,
    COUNT(*) AS requests,
    SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) AS degraded_requests,
    ROUND(100.0 * SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS degraded_pct,
    ROUND(AVG(CASE WHEN degraded = 0 THEN latency_ms END), 2) AS regular_avg_ms,
    ROUND(AVG(CASE WHEN degraded = 1 THEN latency_ms END), 2) AS degraded_avg_ms
FROM interaction
WHERE intent = 'rule' AND topic IS NOT NULL
GROUP BY topic
ORDER BY degraded_pct DESC, requests DESC, topic;
