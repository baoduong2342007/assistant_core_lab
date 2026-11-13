-- Lab05 F1-F3 and H2. Read-only queries on the assistant metadata database.
-- Counts refer to interactions except F3, which counts feedback events.

-- Q1 (F1): requests per intent, most first; ties by intent.
SELECT intent, COUNT(*) AS request_count
FROM interaction
GROUP BY intent
ORDER BY request_count DESC, intent;

-- Q2 (F2): mean latency per intent in milliseconds, slowest first.
SELECT intent, ROUND(AVG(latency_ms), 2) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC, intent;

-- Q3 (F3): known topics with the most thumbs-down feedback events.
-- NULL topics are excluded; repeated ratings on a request remain separate events.
SELECT i.topic, COUNT(*) AS thumbs_down_count
FROM feedback AS f
JOIN interaction AS i ON i.request_id = f.request_id
WHERE f.rating = -1 AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down_count DESC, i.topic;

-- H2: which intents have the highest unresolved rate, and how slow are they?
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
