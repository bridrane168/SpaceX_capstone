SELECT LaunchSite, COUNT(*) AS total_launches, ROUND(AVG(CAST(Class AS REAL)),3) AS success_rate FROM spacex GROUP BY LaunchSite ORDER BY success_rate DESC;
