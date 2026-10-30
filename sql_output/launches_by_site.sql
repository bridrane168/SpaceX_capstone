SELECT LaunchSite, COUNT(*) AS total_launches FROM spacex GROUP BY LaunchSite ORDER BY total_launches DESC;
