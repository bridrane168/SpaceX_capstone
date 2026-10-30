"""Run reproducible SQLite analysis against the project 90-row CSV."""
from pathlib import Path
import sqlite3, pandas as pd
ROOT=Path(__file__).resolve().parent.parent
CSV=ROOT/"spacex_cleaned_data.csv"; OUT=ROOT/"sql_output"; OUT.mkdir(exist_ok=True)
df=pd.read_csv(CSV)
conn=sqlite3.connect(":memory:"); df.to_sql("spacex",conn,index=False,if_exists="replace")
queries={
"total_launches":"SELECT COUNT(*) AS total_launches FROM spacex",
"outcome_counts":"SELECT Class, COUNT(*) AS launches, ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM spacex),1) AS pct FROM spacex GROUP BY Class ORDER BY Class",
"launches_by_site":"SELECT LaunchSite, COUNT(*) AS total_launches FROM spacex GROUP BY LaunchSite ORDER BY total_launches DESC",
"success_by_site":"SELECT LaunchSite, COUNT(*) AS total_launches, ROUND(AVG(CAST(Class AS REAL)),3) AS success_rate FROM spacex GROUP BY LaunchSite ORDER BY success_rate DESC",
"payload_by_outcome":"SELECT Class, COUNT(PayloadMass) AS records_with_payload, ROUND(AVG(PayloadMass),2) AS mean_payload_kg, ROUND(MIN(PayloadMass),2) AS min_payload_kg, ROUND(MAX(PayloadMass),2) AS max_payload_kg FROM spacex GROUP BY Class ORDER BY Class",
"launch_outcomes":"SELECT Outcome, Class, COUNT(*) AS launches FROM spacex GROUP BY Outcome, Class ORDER BY Outcome, Class",
"orbit_analysis":"SELECT Orbit, COUNT(*) AS launches, ROUND(AVG(CAST(Class AS REAL)),3) AS success_rate, ROUND(AVG(PayloadMass),2) AS mean_payload_kg FROM spacex GROUP BY Orbit ORDER BY launches DESC"
}
for name,query in queries.items():
 result=pd.read_sql_query(query,conn); result.to_csv(OUT/f"{name}.csv",index=False); (OUT/f"{name}.sql").write_text(query+";\n",encoding="utf8"); print(f"\n{name}\n{result.to_string(index=False)}")
conn.close()
