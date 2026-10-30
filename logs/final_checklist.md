# Final quality checklist

## COMPLETED AND VERIFIED
- Preserved modeling input: 90 rows × 18 columns; 30 class 0, 60 class 1; no exact duplicates; 26 missing LandingPad values.
- Executed seven SQLite queries and exported SQL/CSV results.
- Refit Logistic Regression and Decision Tree on a stratified 67/23 split (random state 42); saved held-out metrics, confusion matrices, classification reports, and ROC curves.
- Fetched five live Wikipedia pages (all HTTP 200), parsed 113 tables/36 selected history tables, and exported 699 distinct numeric Falcon 9 flights (1–699) spanning 2010–2026; zero duplicate flight/time keys; 57 unknown payload masses. Refreshed the 113-sheet workbook and per-year counts.
- Preserved the earlier 285-row 2025–2026 extract as a separately labeled partial CSV.
- Verified notebook JSON and code outputs; executed scraper and API evidence cells reflect current files.
- Verified Folium page with locally vendored JavaScript and captured genuine screenshot `screenshots/folium_map.png`.
- Verified Dash 4.5.0 callbacks, KPI updates, empty-filter behavior, charts, CSV path, and Flask routes.
- Generated and visually reviewed `Final_Capstone_Report.pdf`; it links the repository and methodology files and reports detailed EDA/SQL/ML results.
- Pushed the project to GitHub branch `main`.

## PENDING
- Capture genuine Dash overview, launch-site filter, and orbit filter screenshots in a browser that can connect to localhost.
- Retry the SpaceX API when its endpoint is reachable. The latest request returned HTTP 522 with an HTML response and no records.

## FAILED IN THIS ENVIRONMENT
- Chrome navigation to `http://127.0.0.1:8050/` returned `ERR_CONNECTION_TIMED_OUT`; no Dash screenshots were created.
- Original two API requests failed DNS resolution before an HTTP status was received; the later HTTP 522 attempt is separately preserved.
