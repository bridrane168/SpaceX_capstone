# Final quality checklist

## COMPLETED
- Preserved the original 90-row, 18-column cleaned CSV; verified 30 unsuccessful, 60 successful, zero exact duplicate rows, and 26 missing `LandingPad` values.
- Executed seven SQLite queries from the project CSV and exported matching `.sql` and `.csv` files.
- Refit logistic regression and decision tree on a stratified 67/23 train/test split (random state 42); exported metrics, actual-prediction confusion matrices, classification reports, and ROC curves.
- Parsed 19 candidate tables from the existing Wikipedia HTML capture using a launch-history column signature; exported a 331-row selected CSV and a detailed candidate summary.
- Confirmed both notebooks are valid notebook JSON; updated the primary notebook's execution notes and section sequence.
- Compiled the Python scripts and verified the existing Folium HTML contains marker clustering.
- Wrote updated README and report content source; preserved the original PDF backup.

## PENDING
- Install the project requirements in an environment that can resolve external hosts; refresh API and Wikipedia from live endpoints.
- Install `openpyxl` and refresh/verify the candidate-table workbook.
- Open `dashboard/index.html` directly in a browser, verify site/orbit/empty filters, and capture genuine screenshots. The single-file dashboard is implemented with embedded project data; browser verification is still pending.
- Render `outputs/report_source.html` to `Final_Capstone_Report.pdf` and visually inspect the PDF. The headless browser export did not produce a file in this environment; the original PDF remains preserved.

## FAILED
- SpaceX API request: two bounded attempts failed DNS resolution before an HTTP status was received. Details are preserved in `api_output/collection_status.json`.
- Live Wikipedia request: DNS resolution failed. The scraper successfully used the pre-existing HTML capture; it did not collect a fresh page in this run.
- Headless Edge/Chrome PDF render attempt: no output PDF was created. No dashboard screenshots were fabricated. The agent environment could not verify the local server response from the browser.
