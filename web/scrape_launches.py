"""Scrape and normalize Falcon launch history from Wikipedia or the saved HTML cache."""
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

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scraping_output"
OUT.mkdir(exist_ok=True)
URL = "https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches"
HTML_PATH = OUT / "wikipedia_launches.html"

try:
    response = requests.get(
        URL,
        headers={"User-Agent": "SpaceXCapstoneStudentResearch/1.0 (educational project)"},
        timeout=(10, 30),
    )
    response.raise_for_status()
    html = response.text
    http_status = response.status_code
    source = "live HTTP response"
    network_error = None
    HTML_PATH.write_text(html, encoding="utf-8")
except requests.RequestException as exc:
    http_status = None
    source = "previously saved HTML cache"
    network_error = f"{type(exc).__name__}: {exc}"
    if not HTML_PATH.exists():
        summary = {
            "url": URL,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "http_status": None,
            "source": source,
            "error": network_error,
            "tables_found": 0,
            "records_exported": 0,
            "notes": "Live request failed and no cached HTML was available; no data exported.",
        }
        (OUT / "scraping_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        raise SystemExit(f"Scrape unavailable: {network_error}")
    html = HTML_PATH.read_text(encoding="utf-8")

soup = BeautifulSoup(html, "lxml")
tables = pd.read_html(StringIO(html))
html_tables = soup.find_all("table")
column_map = {
    "Flight No.": "flight_number",
    "Date and time (UTC)": "launch_datetime_utc",
    "Version, booster[i]": "booster_version",
    "Launch site": "launch_site",
    "Payload[j]": "payloads",
    "Payload mass": "payload_mass_raw",
    "Orbit": "orbit",
    "Customer": "customer",
    "Launch outcome": "launch_outcome",
    "Booster landing": "booster_landing",
}

def clean_text(value):
    if pd.isna(value):
        return None
    value = unicodedata.normalize("NFC", str(value)).replace("\xa0", " ")
    value = re.sub(r"\[\d+\]", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    if value in {"", "—", "–", "-", "Unknown", "unknown"}:
        return None if value != "Unknown" and value != "unknown" else "Unknown"
    return value

candidates = []
selected_tables = []
for index, (tag, table) in enumerate(zip(html_tables, tables)):
    caption_node = tag.find("caption")
    heading_node = tag.find_previous(["h2", "h3"])
    caption = caption_node.get_text(" ", strip=True) if caption_node else ""
    section = heading_node.get_text(" ", strip=True) if heading_node else ""
    columns = [str(column).strip() for column in table.columns]
    required = {"Flight No.", "Date and time (UTC)", "Launch site", "Payload mass", "Orbit"}
    signature = len(required.intersection(columns))
    year_match = re.search(r"\b(20\d{2})\b", section)
    year = year_match.group(1) if year_match else None
    is_candidate = signature == len(required) and len(table) >= 20 and year is not None
    candidates.append({
        "table_index": index,
        "section": section,
        "year": year,
        "shape": list(table.shape),
        "caption": caption,
        "columns": columns,
        "launch_history_signature_matches": signature,
        "selected": is_candidate,
    })
    if is_candidate:
        selected_tables.append((index, year, table.copy()))

launch_rows = []
for table_index, year, table in selected_tables:
    table = table.rename(columns={c: c for c in table.columns})
    date_column = "Date and time (UTC)"
    flight_column = "Flight No."
    if date_column not in table or flight_column not in table:
        continue
    cleaned_dates = table[date_column].map(clean_text)
    # Wikipedia attaches numbered references to timestamps; remove them before parsing.
    parsed_dates = pd.to_datetime(
        cleaned_dates.str.replace(r"\[\d+\]", "", regex=True),
        format="%B %d, %Y %H:%M",
        errors="coerce",
        utc=True,
    )
    details = table.loc[parsed_dates.notna()].copy()
    details["_launch_datetime_utc"] = parsed_dates.loc[parsed_dates.notna()]
    notes = table.loc[parsed_dates.isna()].copy()
    descriptions = {}
    for _, row in notes.iterrows():
        flight_id = clean_text(row.get(flight_column))
        note = clean_text(row.get(date_column))
        if flight_id and note:
            descriptions.setdefault(flight_id, [])
            if note not in descriptions[flight_id]:
                descriptions[flight_id].append(note)

    for (flight_id, launch_dt), rows in details.groupby([flight_column, "_launch_datetime_utc"], dropna=False, sort=False):
        record = {"flight_number": clean_text(flight_id), "launch_datetime_utc": launch_dt.isoformat(), "source_year": year, "source_table_index": table_index}
        for source_col, output_col in column_map.items():
            if source_col not in rows.columns or output_col in {"flight_number", "launch_datetime_utc"}:
                continue
            values = []
            for value in rows[source_col].tolist():
                text = clean_text(value)
                if text and text not in values:
                    values.append(text)
            record[output_col] = "; ".join(values) if output_col == "payloads" and values else (values[0] if values else None)
        raw_mass = record.get("payload_mass_raw")
        mass_match = re.search(r"([\d,]+(?:\.\d+)?)\s*kg\b", raw_mass or "", flags=re.IGNORECASE)
        record["payload_mass_kg"] = float(mass_match.group(1).replace(",", "")) if mass_match else None
        record["description"] = " | ".join(descriptions.get(record["flight_number"], [])) or None
        launch_rows.append(record)

cleaned = pd.DataFrame(launch_rows)
if not cleaned.empty:
    cleaned = cleaned.drop_duplicates(subset=["flight_number", "launch_datetime_utc"]).sort_values(
        ["launch_datetime_utc", "flight_number"], kind="stable"
    ).reset_index(drop=True)
    cleaned.to_csv(OUT / "falcon_launch_history.csv", index=False)

def export_excel(source_tables, destination):
    try:
        with pd.ExcelWriter(destination, engine="openpyxl") as writer:
            for index, table in enumerate(source_tables):
                table.to_excel(writer, sheet_name=f"table_{index}"[:31], index=False)
        return "refreshed with all extracted candidate and non-candidate tables using openpyxl"
    except ImportError:
        # Windows Excel COM is a local fallback when openpyxl is not installed.
        try:
            import win32com.client
        except ImportError as exc:
            return f"not refreshed because neither openpyxl nor win32com is available: {exc}"
        excel = workbook = None
        try:
            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            workbook = excel.Workbooks.Add(1)
            for index, table in enumerate(source_tables):
                sheet = workbook.Worksheets.Item(1) if index == 0 else workbook.Worksheets.Add(After=workbook.Worksheets.Item(workbook.Worksheets.Count))
                sheet.Name = f"table_{index}"[:31]
                matrix = [list(table.columns)]
                for row in table.itertuples(index=False, name=None):
                    matrix.append([None if pd.isna(value) else value.item() if hasattr(value, "item") else value for value in row])
                rows, columns = len(matrix), len(matrix[0])
                sheet.Range(sheet.Cells(1, 1), sheet.Cells(rows, columns)).Value = tuple(tuple(row) for row in matrix)
                sheet.Rows(1).Font.Bold = True
                sheet.UsedRange.Columns.AutoFit()
            workbook.SaveAs(str(Path(destination).resolve()), FileFormat=51)
            workbook.Close(SaveChanges=True)
            return "refreshed with all extracted candidate and non-candidate tables using local Excel COM"
        except Exception as exc:
            com_error = f"{type(exc).__name__}: {exc}"
            try:
                from xlsx_export import write_xlsx
                write_xlsx(source_tables, destination)
                return f"refreshed with all extracted tables using standard-library XLSX fallback after Excel COM failed ({com_error})"
            except Exception as xlsx_exc:
                return f"not refreshed; Excel COM failed ({com_error}) and standard-library XLSX fallback failed ({type(xlsx_exc).__name__}: {xlsx_exc})"
        finally:
            if workbook is not None:
                try: workbook.Close(SaveChanges=False)
                except Exception: pass
            if excel is not None:
                try: excel.Quit()
                except Exception: pass

excel_status = export_excel(tables, OUT / "launch_tables.xlsx")

available_years = sorted({item[1] for item in selected_tables})
first_flight = cleaned["flight_number"].iloc[0] if not cleaned.empty else None
last_flight = cleaned["flight_number"].iloc[-1] if not cleaned.empty else None
summary = {
    "url": URL,
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "http_status": http_status,
    "source": source,
    "network_error": network_error,
    "tables_found": len(tables),
    "candidate_table_indices": [index for index, _, _ in selected_tables],
    "years_in_cached_or_live_capture": available_years,
    "records_exported": len(cleaned),
    "unique_launch_keys": int(cleaned[["flight_number", "launch_datetime_utc"]].drop_duplicates().shape[0]) if not cleaned.empty else 0,
    "flight_number_range_by_row": [first_flight, last_flight],
    "excel_export": excel_status,
    "missing_by_column": cleaned.isna().sum().to_dict() if not cleaned.empty else {},
    "notes": (
        "Launch-detail rows were selected by parsing timestamps. Rows with a flight number but no timestamp were treated as continuation descriptions and attached to the launch. Multiple payload rows for the same flight/time were aggregated. "
        "The saved capture contains only the listed year sections; it does not contain the complete historical launch list, so this CSV is a partial year extract, not a complete Falcon 9 history."
    ),
    "candidates": candidates,
}
(OUT / "scraping_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "candidates"}, indent=2))
