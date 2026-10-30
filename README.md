# SpaceX Falcon 9 First-Stage Landing Prediction

IBM Applied Data Science Capstone. The **modeling dataset** is the supplied 90-row cleaned CSV (`Class`: 0 unsuccessful, 1 successful). The separate **scraped launch-history dataset** now covers the full published Falcon 9 flight list through October 2026.

**GitHub repository:** [bridrane168/SpaceX_capstone](https://github.com/bridrane168/SpaceX_capstone) · Clone URL: `https://github.com/bridrane168/SpaceX_capstone.git`

## Methodology links

- [Main capstone notebook](SpaceX_Capstone_Basics_Final.ipynb)
- [SpaceX API collector](web/collect_spacex_api.py) · [Wikipedia scraper](web/scrape_launches.py)
- [Data wrangling quality output](outputs/data_quality_summary.txt) · [EDA analysis](web/eda_analysis.py) · [EDA findings](outputs/eda_findings.json)
- [SQL runner](web/sql_analysis.py) · [SQL source and results](sql_output/)
- [Folium map](web/spacex_launch_sites.html) · [Genuine map screenshot](screenshots/folium_map.png)
- [Model training](web/train_models.py) · [Aggregate metrics](outputs/model_metrics.csv) · [Per-class reports](outputs/classification_reports.csv)
- [Plotly Dash source](dashboard/dash_app.py) · [Dash verification](outputs/dashboard_validation.txt)
- [Final evidence report PDF](Final_Capstone_Report.pdf)

## Verified findings

- Modeling CSV: 90 rows × 18 columns; 30 unsuccessful and 60 successful outcomes; 0 exact duplicate rows; 26 missing values, all in `LandingPad`.
- Stratified 75/25 split (67 train, 23 test; random state 42): Decision Tree accuracy 86.96%, precision 0.875, recall 0.933, F1 0.903, ROC-AUC 0.842. Logistic Regression accuracy 82.61%, precision 0.789, recall 1.000, F1 0.882, ROC-AUC 0.850. Detailed per-class and macro/weighted metrics and confusion matrices are saved in the project. The small test set, outcome imbalance, and possible post-launch feature leakage limit conclusions.
- SQL executes seven SQLite queries and saves matching SQL and CSV files under `sql_output/`.
- Orbit and booster-reuse comparisons are descriptive; sample sizes and mission mix differ, so they do not establish causality.
- Live Wikipedia scrape: five pages, HTTP 200 for each; 113 tables inspected, 36 launch-history tables selected, 699 unique Falcon 9 flight/time records (flight numbers 1–699), zero duplicate keys, and 57 missing payload masses. The extract spans 2010–2026; 2011 had no listed Falcon 9 launch. `scraping_output/launch_counts_by_year.csv` gives the year counts. The refreshed workbook contains 113 worksheets. The previous 285-record 2025–2026 extract is retained and labeled `falcon_launch_history_partial_2025_2026.csv`.
- Live API collection remains unsuccessful. The original two attempts recorded DNS failure and no HTTP status; a later genuine request returned HTTP 522 with an HTML error body, not JSON. No API launch records or CSV are claimed. See `api_output/collection_status.json` and `outputs/external_retry_evidence.json`.

## Dashboard and screenshots

The genuine Plotly Dash application is `dashboard/dash_app.py`; it reads the preserved 90-row modeling CSV. All-data, site, orbit, and empty-filter callbacks, four KPI values, five charts, and three Dash routes were verified. Genuine Dash screenshots are still pending because the browser in this environment cannot connect to the local server. `figures/dashboard_preview.png` is a static preview and is not runtime evidence. The Folium screenshot is genuine and saved at `screenshots/folium_map.png`.

To capture the remaining evidence on a machine where localhost works:

1. Run `python dashboard/dash_app.py` and open `http://127.0.0.1:8050/`.
2. Save genuine captures as `screenshots/dash_overview.png`, `screenshots/dash_filter_launch_site.png` (KSC LC 39A), and `screenshots/dash_filter_orbit.png` (GTO).
3. Run `python web/build_final_report.py` after installing ReportLab, then commit and push the three captures and regenerated PDF.

## Reproduce

```powershell
python -m pip install -r requirements.txt
python web/sql_analysis.py
python web/train_models.py
python web/eda_analysis.py
python web/scrape_launches.py
python web/collect_spacex_api.py
python web/verify_dashboard.py
```

The scraper follows the live Wikipedia page to its year archive pages, and caches each page for repeatable offline use. It records per-page HTTP statuses in `scraping_output/scraping_summary.json`. The OpenStreetMap basemap in the Folium HTML requires internet; its Leaflet scripts and styles are bundled locally.

## Main project files

- `spacex_cleaned_data.csv`: preserved 90-row modeling and dashboard input.
- `scraping_output/falcon_launch_history.csv`: current full 699-record Wikipedia history extract.
- `web/`: SQL, API, scraper, EDA, model, map, and export scripts.
- `dashboard/`: genuine Dash application and HTML fallback.
- `outputs/`, `figures/`, `sql_output/`, `api_output/`, `scraping_output/`, `screenshots/`: result data, execution evidence, and screenshots.
- `SpaceX_Capstone_Final_Report.pdf`: preserved earlier report. `Final_Capstone_Report.pdf` is the updated evidence report; it keeps Dash screenshots marked pending until genuine captures exist.
