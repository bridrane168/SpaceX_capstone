SELECT Orbit, COUNT(*) AS launches, ROUND(AVG(CAST(Class AS REAL)),3) AS success_rate, ROUND(AVG(PayloadMass),2) AS mean_payload_kg FROM spacex GROUP BY Orbit ORDER BY launches DESC;
