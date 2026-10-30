"""Collect and normalize Falcon 9 launch history from the live Wikipedia year pages."""
from __future__ import annotations
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
import json
import re
import time
import unicodedata

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scraping_output"
OUT.mkdir(exist_ok=True)
BASE = "https://en.wikipedia.org/wiki/"
PAGES = [
    ("main_2025_2026", BASE + "List_of_Falcon_9_and_Falcon_Heavy_launches", "wikipedia_launches.html"),
    ("2010_2019", BASE + "List_of_Falcon_9_and_Falcon_Heavy_launches_(2010%E2%80%932019)", "falcon_launches_2010_2019.html"),
    ("2020_2022", BASE + "List_of_Falcon_9_and_Falcon_Heavy_launches_(2020%E2%80%932022)", "falcon_launches_2020_2022.html"),
    ("2023", BASE + "List_of_Falcon_9_and_Falcon_Heavy_launches_(2023)", "falcon_launches_2023.html"),
    ("2024", BASE + "List_of_Falcon_9_and_Falcon_Heavy_launches_(2024)", "falcon_launches_2024.html"),
]
# The current page contains 2025/2026; archive pages above cover 2010-2024.
HEADERS = {"User-Agent": "SpaceXCapstoneStudentResearch/1.0 (educational project)"}

def clean_text(value):
    if pd.isna(value):
        return None
    if isinstance(value, (int,)):
        value = str(value)
    elif isinstance(value, float) and value.is_integer():
        value = str(int(value))
    value = unicodedata.normalize("NFC", str(value)).replace("\xa0", " ")
    value = re.sub(r"\[\s*[a-zA-Z0-9]+\s*\]", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    if value in {"", "—", "–", "-", "Unknown", "unknown"}:
        return None if value not in {"Unknown", "unknown"} else "Unknown"
    return value

def pick_column(columns, exact=None, prefix=None):
    if exact and exact in columns:
        return exact
    if prefix:
        return next((c for c in columns if str(c).startswith(prefix)), None)
    return None

source_statuses = []
all_tables = []
all_candidates = []
launch_rows = []
for source_id, url, filename in PAGES:
    cache_path = OUT / filename
    try:
        response = requests.get(url, headers=HEADERS, timeout=(10, 30))
        response.raise_for_status()
        html = response.text
        cache_path.write_text(html, encoding="utf-8")
        source_statuses.append({"source_id": source_id, "url": url, "http_status": response.status_code,
                               "content_type": response.headers.get("content-type"), "source": "live HTTP response",
                               "bytes": len(response.content)})
    except requests.RequestException as exc:
        if not cache_path.is_file():
            source_statuses.append({"source_id": source_id, "url": url, "http_status": getattr(getattr(exc, "response", None), "status_code", None),
                                   "source": "unavailable", "error": f"{type(exc).__name__}: {exc}", "records": 0})
            continue
        html = cache_path.read_text(encoding="utf-8")
        source_statuses.append({"source_id": source_id, "url": url, "http_status": getattr(getattr(exc, "response", None), "status_code", None),
                               "source": "saved source cache", "error": f"{type(exc).__name__}: {exc}", "cache_file": filename})
    try:
        tables = pd.read_html(StringIO(html))
        soup = BeautifulSoup(html, "lxml")
    except Exception as exc:
        source_statuses[-1]["parse_error"] = f"{type(exc).__name__}: {exc}"
        continue
    source_statuses[-1]["tables_found"] = len(tables)
    html_tables = soup.find_all("table")
    for index, table in enumerate(tables):
        page_table_id = f"{source_id}_table_{index}"
        all_tables.append((page_table_id, table))
        columns = list(table.columns)
        flight_col = pick_column(columns, prefix="Flight No.")
        date_col = pick_column(columns, prefix="Date and time (UTC)")
        required = [flight_col, date_col, "Launch site", "Payload mass", "Orbit", "Customer", "Launch outcome", "Booster landing"]
        signature = sum(c is not None and c in columns for c in required)
        tag = html_tables[index] if index < len(html_tables) else None
        heading_node = tag.find_previous(["h2", "h3", "h4"]) if tag else None
        section = heading_node.get_text(" ", strip=True) if heading_node else ""
        candidate = signature == 8 and len(table) >= 1
        all_candidates.append({"source_id": source_id, "table_index": index, "section": section, "shape": list(table.shape),
                              "columns": [str(c) for c in columns], "launch_history_signature_matches": signature,
                              "selected": candidate})
        if not candidate:
            continue
        parsed = pd.to_datetime(table[date_col].map(clean_text).str.replace(r"\[\s*[a-zA-Z0-9]+\s*\]", "", regex=True),
                                format="mixed", errors="coerce", utc=True, dayfirst=False)
        details = table.loc[parsed.notna()].copy()
        details["_launch_datetime_utc"] = parsed.loc[parsed.notna()]
        notes = table.loc[parsed.isna()].copy()
        descriptions = {}
        for _, row in notes.iterrows():
            flight_id = clean_text(row.get(flight_col))
            note = clean_text(row.get(date_col))
            if flight_id and note:
                descriptions.setdefault(flight_id, [])
                if note not in descriptions[flight_id]: descriptions[flight_id].append(note)
        for (raw_flight, launch_dt), rows in details.groupby([flight_col, "_launch_datetime_utc"], dropna=False, sort=False):
            flight_id = clean_text(raw_flight)
            # Numeric flight identifiers are Falcon 9. Exclude Falcon Heavy (FH n) rows.
            if not flight_id or not re.fullmatch(r"\d+", flight_id):
                continue
            record = {"flight_number": flight_id, "launch_datetime_utc": launch_dt.isoformat(),
                      "source_year": int(launch_dt.year), "source_page": source_id,
                      "source_table_index": int(index)}
            fields = {
                "booster_version": pick_column(columns, prefix="Version, booster"),
                "launch_site": "Launch site", "payloads": pick_column(columns, prefix="Payload"),
                "payload_mass_raw": "Payload mass", "orbit": "Orbit", "customer": "Customer",
                "launch_outcome": "Launch outcome", "booster_landing": "Booster landing",
            }
            for out_col, source_col in fields.items():
                values = []
                if source_col:
                    for value in rows[source_col].tolist():
                        cleaned_value = clean_text(value)
                        if cleaned_value and cleaned_value not in values: values.append(cleaned_value)
                record[out_col] = "; ".join(values) if out_col == "payloads" and values else (values[0] if values else None)
            mass = record.get("payload_mass_raw")
            match = re.search(r"([\d,]+(?:\.\d+)?)\s*kg\b", mass or "", re.IGNORECASE)
            record["payload_mass_kg"] = float(match.group(1).replace(",", "")) if match else None
            record["description"] = " | ".join(descriptions.get(flight_id, [])) or None
            launch_rows.append(record)

if not launch_rows:
    raise SystemExit("No launch records were parsed from live or cached Wikipedia sources.")
cleaned = pd.DataFrame(launch_rows)
cleaned = cleaned.drop_duplicates(subset=["flight_number", "launch_datetime_utc"], keep="last")
cleaned = cleaned.sort_values(["launch_datetime_utc", "flight_number"], kind="stable").reset_index(drop=True)
cleaned["flight_number"] = cleaned["flight_number"].astype("string")
cleaned["source_year"] = cleaned["source_year"].astype("int64")
cleaned["source_table_index"] = cleaned["source_table_index"].astype("int64")
cleaned["payload_mass_kg"] = pd.to_numeric(cleaned["payload_mass_kg"], errors="coerce")
cleaned.to_csv(OUT / "falcon_launch_history.csv", index=False)

# Refresh a workbook with every table inspected from all five current/archive source pages.
with pd.ExcelWriter(OUT / "launch_tables.xlsx", engine="openpyxl") as writer:
    for page_table_id, table in all_tables:
        table.to_excel(writer, sheet_name=page_table_id[:31], index=False)

summary = {
    "url": PAGES[0][1], "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "source": "live Wikipedia page family with saved per-page caches", "http_status": source_statuses[0].get("http_status"),
    "pages": source_statuses, "tables_found": sum(p.get("tables_found", 0) for p in source_statuses),
    "candidate_tables_selected": sum(1 for c in all_candidates if c["selected"]),
    "years_in_sources": sorted(int(y) for y in cleaned["source_year"].dropna().unique()),
    "records_exported": int(len(cleaned)), "unique_launch_keys": int(cleaned[["flight_number", "launch_datetime_utc"]].drop_duplicates().shape[0]),
    "flight_number_range": [int(cleaned.flight_number.astype(int).min()), int(cleaned.flight_number.astype(int).max())],
    "duplicate_rows_after_deduplication": int(len(launch_rows) - len(cleaned)),
    "excel_export": f"refreshed with {len(all_tables)} inspected tables across {len(PAGES)} source pages using openpyxl",
    "missing_by_column": {k: int(v) for k, v in cleaned.isna().sum().items()},
    "column_dtypes": {k: str(v) for k, v in cleaned.dtypes.items()},
    "notes": "The live Wikipedia page family was fetched and parsed. The year archive pages cover 2010-2019, 2020-2022, 2023, and 2024; the current page provides the 2025 and 2026 tables. Only numeric Falcon 9 flight numbers are retained; Falcon Heavy identifiers are excluded. Multiple payload rows per flight/time are aggregated. Coverage represents the published past-launch tables available on the capture date, not future launches.",
    "candidate_tables": all_candidates,
}
(OUT / "scraping_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps({k:v for k,v in summary.items() if k!="candidate_tables"},indent=2))
