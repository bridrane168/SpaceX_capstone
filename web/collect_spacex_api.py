"""Collect SpaceX API v4 launches with bounded retries and auditable status."""
from pathlib import Path
from datetime import datetime, timezone
import json, time, requests, pandas as pd
ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/"api_output"; OUT.mkdir(exist_ok=True)
URL="https://api.spacexdata.com/v4/launches"; stamp=datetime.now(timezone.utc).isoformat()
status=None; error=None; response_body=None
for attempt in range(1,3):
 try:
  r=requests.get(URL,timeout=(5,20)); status=r.status_code; response_body=r.text
  if r.ok: break
  error=f"HTTP {status}: {r.reason}"
 except requests.RequestException as exc:
  error=f"{type(exc).__name__}: {exc}"
 if attempt<2: time.sleep(2)
if status is not None and 200<=status<300:
 raw=r.json(); (OUT/"launches_raw.json").write_text(json.dumps(raw,indent=2),encoding="utf8")
 pd.json_normalize(raw).to_csv(OUT/"launches.csv",index=False)
else:
 (OUT/"launches_error.txt").write_text(response_body or error or "Request failed without a response body",encoding="utf8")
record={"url":URL,"timestamp_utc":stamp,"http_status":status,"attempts":attempt,"success":status is not None and 200<=status<300,"error":error}
(OUT/"collection_status.json").write_text(json.dumps(record,indent=2),encoding="utf8")
print(json.dumps(record,indent=2))
if not record["success"]: print("API collection failed; no launch data was fabricated.")
