SELECT Class, COUNT(*) AS launches, ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM spacex),1) AS pct FROM spacex GROUP BY Class ORDER BY Class;
