# SpaceX Falcon 9 First Stage Landing Prediction

IBM Applied Data Science Capstone project using the preserved 90-record cleaned dataset (`Class`: 0 unsuccessful, 1 successful). The project includes analysis notebooks and reproducible SQL, model, API, scraping, map, and dashboard artifacts.

**GitHub repository:** [bridrane168/SpaceX_capstone](https://github.com/bridrane168/SpaceX_capstone) · Clone URL: `https://github.com/bridrane168/SpaceX_capstone.git`

## Methodology links

- [Main capstone notebook](SpaceX_Capstone_Basics_Final.ipynb)
- [SpaceX API collector](web/collect_spacex_api.py) · [Wikipedia scraper](web/scrape_launches.py)
- [Data wrangling and quality outputs](outputs/data_quality_summary.txt) · [EDA analysis](web/eda_analysis.py) · [EDA findings](outputs/eda_findings.json)
- [SQL runner](web/sql_analysis.py) · [SQL source and results](sql_output/)
- [Folium map](web/spacex_launch_sites.html) · [Map screenshot](screenshots/folium_map.png)
- [Model training and evaluation](web/train_models.py) · [Metrics](outputs/model_metrics.csv) · [Classification reports](outputs/classification_reports.csv)
- [Plotly Dash app](dashboard/dash_app.py) · [Dash verification results](outputs/dashboard_validation.txt)
- [Final evidence report PDF](Final_Capstone_Report.pdf)

## Verified analysis

- The cleaned dataset has 90 rows and 18 columns: 30 unsuccessful and 60 successful outcomes, 0 duplicate rows, and 26 missing values (all in `LandingPad`).
- On a stratified 75/25 split (67 train, 23 test; random state 42), Decision Tree achieved 86.96% accuracy, 0.875 precision, 0.933 recall, 0.903 F1, and 0.842 ROC-AUC. Logistic Regression achieved 82.61% accuracy, 0.789 precision, 1.000 recall, 0.882 F1, and 0.850 ROC-AUC. Metrics and confusion matrices were recomputed from held-out predictions.
- Orbit and booster-reuse summaries and figures are in `outputs/eda_summary.csv`, `outputs/eda_findings.json`, and `figures/`. Group rates are descriptive, based on uneven samples, and do not establish causality.
- Seven executed SQLite queries and their outputs are in `sql_output/`.
- `web/spacex_launch_sites.html` is the interactive Folium map, with clustered launch markers and site popups.

## Open the dashboard

For a direct view, open `dashboard/index.html` in a browser. This self-contained interactive page embeds the 90-row dataset and offers site and orbit filters, four KPIs, and five charts.

The Python entry point is `python dashboard/app.py`. If Plotly Dash is installed, this starts `dashboard/dash_app.py`; otherwise it serves the standalone page at `http://127.0.0.1:8050`. If the server cannot bind to that port, the launcher opens `dashboard/index.html` directly. Install project dependencies with:

```powershell
python -m pip install -r requirements.txt
```

Dash 4.5.0 is installed in the project Python. The real app was started, the CSV path was verified, and its four KPIs/five charts were exercised for all data, KSC, GTO, and a zero-result KSC/GEO selection. Dash routes returned HTTP 200 through Flask's test client. Headless Chrome cannot reach localhost in this managed environment, so the genuine Dash overview/site/orbit screenshots remain pending. `outputs/dashboard_validation.txt` records the checks. `figures/dashboard_preview.png` is only a static matplotlib preview and is not submitted as runtime evidence. The Folium HTML now uses vendored Leaflet, jQuery, and MarkerCluster assets; its genuine browser screenshot is `screenshots/folium_map.png`.

To finish the remaining Dash screenshot evidence on a machine where localhost access is available:

1. From this folder, run `python dashboard/app.py` and open `http://127.0.0.1:8050/`.
2. Save genuine browser captures as `screenshots/dash_overview.png`, `screenshots/dash_filter_launch_site.png` (select KSC LC 39A), and `screenshots/dash_filter_orbit.png` (select GTO).
3. The Folium map screenshot is already saved. Open `web/spacex_launch_sites.html` to inspect the interactive map; its OpenStreetMap tiles require internet access.
4. Run `python web/build_final_report.py` after ReportLab is installed to regenerate the report with the new Dash captures. The current report includes the map screenshot and marks the three missing Dash screenshots as pending.

## Reproduce

Use Python 3.10 or newer:

```powershell
python web/sql_analysis.py
python web/train_models.py
python web/eda_analysis.py
python web/scrape_launches.py
python web/collect_spacex_api.py
python web/verify_dashboard.py
```

The API collector attempted two bounded requests, but DNS resolution failed: no HTTP status or API records were obtained. See `api_output/collection_status.json` and `api_output/launches_error.txt`.

The Wikipedia request also failed DNS resolution. The scraper therefore analyzed the saved HTML capture: 19 tables were inspected; history tables 1 and 2 were selected; 285 unique launch-time records were exported for the 2025 and 2026 sections present in that capture. The data are a partial extract, not a complete launch history. The CSV, refreshed Excel workbook, and coverage note are in `scraping_output/`; `scraping_summary.json` records the null live HTTP status and source limitation.

## Main project files

- `SpaceX_Capstone_Basics_Final.ipynb`: primary analysis notebook.
- `spacex_cleaned_data.csv`: preserved 90-row model and dashboard input.
- `web/`: SQL, collection, scraper, EDA, model, map, and spreadsheet export scripts.
- `dashboard/`: Dash source and interactive standalone HTML fallback.
- `outputs/`, `figures/`, `sql_output/`, `api_output/`, `scraping_output/`: generated results and execution evidence.
- `outputs/report_source.html`: report source. `SpaceX_Capstone_Final_Report.pdf` is the preserved original; `Final_Capstone_Report.pdf` is the updated evidence report, includes the genuine Folium screenshot and GitHub/methodology links, and marks missing Dash screenshots as pending.
