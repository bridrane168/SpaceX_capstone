"""Build the evidence-based capstone PDF from current project outputs."""
import csv
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Final_Capstone_Report.pdf"
REPO_URL = "https://github.com/bridrane168/SpaceX_capstone"
REPO_FILES = [
    "SpaceX_Capstone_Basics_Final.ipynb",
    "web/collect_spacex_api.py",
    "web/scrape_launches.py",
    "web/eda_analysis.py",
    "web/sql_analysis.py",
    "web/spacex_launch_sites.html",
    "web/train_models.py",
    "dashboard/dash_app.py",
]
NAVY = colors.HexColor("#0B1D3A")
TEAL = colors.HexColor("#0F766E")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Section2", parent=styles["Heading1"], fontSize=16, leading=20, textColor=NAVY, spaceBefore=8, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle(name="Sub2", parent=styles["Heading2"], fontSize=11, leading=14, textColor=TEAL, spaceBefore=7, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontSize=8.7, leading=12, spaceAfter=5))
styles.add(ParagraphStyle(name="Caption2", parent=styles["BodyText"], fontSize=8, leading=10, alignment=1, textColor=colors.HexColor("#475569"), spaceAfter=7))
styles.add(ParagraphStyle(name="Warning2", parent=styles["BodyText"], fontSize=9, leading=13, textColor=colors.HexColor("#8A4B08"), backColor=colors.HexColor("#FFF7E6"), borderColor=colors.HexColor("#E7B34B"), borderWidth=.8, borderPadding=7, spaceBefore=5, spaceAfter=8))
styles.add(ParagraphStyle(name="CoverTitle2", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=colors.white, alignment=1))
styles.add(ParagraphStyle(name="CoverSub2", parent=styles["Normal"], fontSize=11, leading=16, textColor=colors.HexColor("#DCE7F2"), alignment=1))

def readcsv(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def para(s, style="Body2"):
    s = str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(s, styles[style])

def tbl(rows, widths=None):
    t = Table([[para(c) for c in r] for r in rows], colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0),NAVY), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#EAF2F7")]),
        ("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),5),
        ("RIGHTPADDING",(0,0),(-1,-1),5), ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    return t

def pic(p, h=75*mm):
    p=Path(p)
    if not p.is_file(): return None
    x=Image(str(p)); scale=min(170*mm/x.imageWidth,h/x.imageHeight,1)
    x.drawWidth=x.imageWidth*scale; x.drawHeight=x.imageHeight*scale; x.hAlign="CENTER"
    return x

def footer(canvas, doc):
    if doc.page>1:
        canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#CBD5E1")); canvas.line(20*mm,14*mm,190*mm,14*mm)
        canvas.setFont("Helvetica",8); canvas.setFillColor(colors.HexColor("#475569"))
        canvas.drawString(20*mm,9*mm,"IBM Applied Data Science Capstone | Evidence report")
        canvas.drawRightString(190*mm,9*mm,f"Page {doc.page}"); canvas.restoreState()

data=readcsv(ROOT/"spacex_cleaned_data.csv")
scraped=readcsv(ROOT/"scraping_output/falcon_launch_history.csv")
scrape=json.loads((ROOT/"scraping_output/scraping_summary.json").read_text(encoding="utf-8"))
api=json.loads((ROOT/"api_output/collection_status.json").read_text(encoding="utf-8"))
eda=json.loads((ROOT/"outputs/eda_findings.json").read_text(encoding="utf-8"))
metrics=readcsv(ROOT/"outputs/model_metrics.csv")
keys={(r["flight_number"],r["launch_datetime_utc"]) for r in scraped}
missing_mass=sum(not r.get("payload_mass_kg","").strip() for r in scraped)
shotdir=ROOT/"screenshots"
shotnames=["dash_overview.png","dash_filter_launch_site.png","dash_filter_orbit.png","folium_map.png"]
dash_shots=shotnames[:3]
missing_dash_shots=[n for n in dash_shots if not (shotdir/n).is_file()]
map_shot=shotdir/"folium_map.png"

story=[]
cover=Table([[para("IBM APPLIED DATA SCIENCE CAPSTONE","CoverSub2")],[Spacer(1,18*mm)],[para("Falcon 9 First Stage Landing Prediction","CoverTitle2")],[para("Launch analysis, data collection, SQL, classification, and dashboard evidence","CoverSub2")],[Spacer(1,20*mm)],[para("EVIDENCE STATUS: INCOMPLETE - genuine Dash overview and filter screenshots are pending.","Warning2")],[para("Prepared from current project files | 30 October 2026","CoverSub2")]],colWidths=[170*mm],rowHeights=[18*mm,18*mm,28*mm,22*mm,16*mm,26*mm,18*mm])
cover.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER"),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10)]))
story += [Spacer(1,14*mm),cover,PageBreak()]

story += [para("1. Introduction and objectives","Section2"),para("This project analyzes the provided 90-launch Falcon 9 dataset and predicts the binary first-stage outcome in Class (0 = unsuccessful, 1 = successful). Objectives are to audit and prepare the supplied data; describe outcomes by site, payload, orbit, flight number, and booster reuse; execute SQL summaries; build a Folium map; compare two classifiers; and provide a Plotly Dash dashboard with verifiable outputs.")]
story += [para("Project repository and methodology links", "Sub2"), Paragraph(f'GitHub repository: <link href="{REPO_URL}">{REPO_URL}</link>', styles["Body2"])]
for repo_file in REPO_FILES:
    story.append(Paragraph(f'<link href="{REPO_URL}/blob/main/{repo_file}">{repo_file}</link>', styles["Body2"]))
story += [para("2. Data cleaning and preparation","Section2"),para("The preserved cleaned source contains 90 rows and 18 columns. There are 30 unsuccessful and 60 successful outcomes, zero exact duplicate rows, and 26 missing values, all in LandingPad. Those rows were retained. The model pipeline imputes numeric values by median, imputes categorical values by most frequent value, scales numeric features, and one-hot encodes categories inside the training pipeline."),tbl([["Quality item","Verified value"],["Rows / columns","90 / 18"],["Class 0 / Class 1","30 / 60"],["Exact duplicates","0"],["Missing values","26, all LandingPad"],["Model split","67 train / 23 test; stratified; random_state=42"]],[55*mm,115*mm])]

story += [para("3. Data collection: API and web scraping","Section2"),para("SpaceX API","Sub2"),para(f"Endpoint: {api.get('url')}. The collector made its recorded bounded attempts. The saved HTTP status is {api.get('http_status')}; DNS resolution failed, so no HTTP response or API records were obtained. launches_raw.json is empty and launches.csv is absent. The status JSON and error log preserve the actual failure; no response data or status was fabricated."),para("Wikipedia scrape","Sub2"),para(f"The live request also failed DNS resolution. The scraper used the saved HTML capture, inspected {scrape.get('tables_found')} tables, and selected history tables {scrape.get('candidate_table_indices')} for the 2025 and 2026 sections present in that capture. The cleaned CSV has {len(scraped)} rows and {len(keys)} distinct flight/time keys; exact duplicate keys/rows: {len(scraped)-len(keys)}. Missing payload_mass_kg: {missing_mass}; all other exported columns have no missing values. In the exported CSV, flight_number, payload_mass_raw, and other descriptors are text/object fields; source_year and source_table_index are integers; payload_mass_kg is floating-point numeric."),para("Coverage is partial: the cached page contains 2025-2026 sections only, not the complete historical launch list. The CSV is scraping_output/falcon_launch_history.csv. The refreshed Excel file opens successfully with openpyxl and contains 19 worksheets; raw history tables 1 and 2 contain 331 and 250 source rows before launch-level aggregation.")]

story += [para("4. Exploratory data analysis and visualization","Section2"),para("In the model dataset, overall landing success is 66.7%. Launch counts are CCAFS SLC 40: 55, KSC LC 39A: 22, and VAFB SLC 4E: 13. Successful launches have higher mean payload mass than unsuccessful launches in this sample; this is descriptive, not causal."),para("Orbit and reuse findings","Sub2")]
orows=[["Orbit","Launches","Observed success"]]
for r in sorted(eda["by_orbit"],key=lambda x:-int(x["launches"])): orows.append([r["Orbit"],str(r["launches"]),f"{float(r['success_rate']):.1%}"])
story.append(tbl(orows,[70*mm,40*mm,60*mm]))
story.append(para("For the orbits with at least five records: GTO has 27 launches and 51.9% success; ISS has 21 and 61.9%; VLEO has 14 and 85.7%. Previously flown boosters show 78.4% success over 37 launches, compared with 58.5% over 53 not-reused launches. Unequal group sizes and mission mix prevent causal interpretation."))
for name,cap in [("outcome_distribution.png","Landing outcome distribution"),("success_by_site.png","Success rate by launch site"),("payload_by_outcome.png","Payload mass by outcome"),("success_by_flight_group.png","Success by flight-number group"),("orbit_success_rate.png","Success rate by orbit"),("booster_reuse_success_rate.png","Success rate by booster reuse")]:
    im=pic(ROOT/"figures"/name,60*mm)
    if im: story += [im,para(cap,"Caption2")]

story += [PageBreak(),para("5. SQL analysis","Section2"),para("Seven SQLite queries were executed after loading the cleaned CSV. SQL source and result CSVs are in sql_output/. They cover total launches, outcomes, launch sites, success rate by site, payload mass, and orbit."),tbl([["Query result","Verified output"],["Total launches","90"],["Outcomes","Class 0: 30; Class 1: 60"],["Launches by site","CCAFS: 55; KSC: 22; VAFB: 13"],["KSC LC 39A success","77.3% (17 of 22)"],["Mean payload, class 0 / 1","4,784.56 kg / 6,765.16 kg"]],[65*mm,105*mm])]
story += [para("6. Folium interactive map","Section2"),para("web/spacex_launch_sites.html contains three launch-site markers, MarkerCluster, and popup summaries. Leaflet 1.9.3, jQuery 3.7.1, and MarkerCluster 1.1.0 are vendored under web/vendor/leaflet so the map scripts and styles load locally; the OpenStreetMap basemap tiles still require network access." )]
if map_shot.is_file():
    map_image=pic(map_shot,92*mm)
    if map_image: story += [map_image,para("Genuine browser capture of the Folium map with loaded tiles, two visible marker icons, and one cluster containing the two Florida launch sites.","Caption2")]
else:
    story.append(para("PENDING - the genuine Folium browser screenshot is not present.","Warning2"))
story += [para("7. Machine-learning methodology and verified metrics","Section2"),para("Target: Class. Features: FlightNumber, PayloadMass, Flights, GridFins, Reused, Legs, Block, ReusedCount, Orbit, LaunchSite, and Serial. A stratified 75/25 split uses 67 train and 23 test records (random_state=42). Both pipelines fit preprocessing on training data only. Logistic Regression and a depth-5 Decision Tree use class_weight='balanced'. Metrics are from the saved held-out predictions." )]
mrows=[["Model","Accuracy","Precision","Recall","F1","ROC-AUC","TN FP FN TP"]]
for r in metrics: mrows.append([r["Model"],f"{float(r['Accuracy']):.2%}",f"{float(r['Precision']):.3f}",f"{float(r['Recall']):.3f}",f"{float(r['F1 score']):.3f}",f"{float(r['ROC-AUC']):.3f}",f"{r['TN']} {r['FP']} {r['FN']} {r['TP']}"])
story.append(tbl(mrows,[38*mm,23*mm,23*mm,20*mm,18*mm,19*mm,29*mm]))
story.append(para("The Decision Tree is selected by test F1 (0.903 vs. 0.882). The test set has only 23 records (15 successful, 8 unsuccessful), so estimates are unstable. Predictors such as landing configuration may not be available at prediction time; this creates leakage risk for a future-launch use case."))
for name,cap in [("confusion_logistic_regression.png","Logistic Regression confusion matrix: TN=4, FP=4, FN=0, TP=15"),("confusion_decision_tree.png","Decision Tree confusion matrix: TN=6, FP=2, FN=1, TP=14"),("roc_curves.png","ROC curves from held-out predictions")]:
    im=pic(ROOT/"figures"/name,67*mm)
    if im: story += [im,para(cap,"Caption2")]

story += [PageBreak(),para("8. Plotly Dash application verification","Section2"),para("The genuine Dash app is dashboard/dash_app.py, uses Dash 4.5.0, and loads spacex_cleaned_data.csv from a source-relative path. The app started at http://127.0.0.1:8050/. Verified callback outputs: All = 90 / 60 / 30 / 66.7%; KSC LC 39A = 22 / 17 / 5 / 77.3%; GTO = 27 / 14 / 13 / 51.9%; empty KSC/GEO = 0 / 0 / 0 / 0.0%. Each callback returned five charts, including explicit empty-state chart titles. Flask test-client requests to /, /_dash-layout, and /_dash-dependencies returned HTTP 200."),para("Genuine Dash screenshot status","Sub2")]
for name in dash_shots:
    if (shotdir/name).is_file():
        im=pic(shotdir/name,90*mm)
        if im: story += [im,para(name,"Caption2")]
if missing_dash_shots:
    story.append(para("PENDING - genuine Dash browser screenshots are still missing: "+", ".join(missing_dash_shots)+". Headless Chrome could not open the local Dash server in this environment (direct TCP to localhost is blocked). The static dashboard preview is not used as evidence.","Warning2"))

story += [
    para("9. Findings, limitations, and conclusion", "Section2"),
    para("The descriptive analysis shows different landing rates across sites, orbits, payloads, flight numbers, and booster reuse. The Decision Tree is the strongest baseline by held-out F1, but the 23-row test set and 2:1 outcome imbalance make results uncertain. Additional launches, repeated stratified validation, uncertainty estimates, calibration checks, and predictors restricted to pre-launch information are needed before operational interpretation."),
    para("External collection remains incomplete: the API and live Wikipedia requests failed DNS resolution. The cached scrape is limited to 2025-2026 sections and must not be called complete history. Dash callbacks and routes are verified, but genuine Dash browser screenshots remain pending. The Folium screenshot is captured using the existing interactive map with locally vendored JavaScript assets."),
    tbl([
        ["Status", "Component", "Evidence / remaining action"],
        ["COMPLETED AND VERIFIED", "Cleaned CSV, cached scrape CSV/XLSX, EDA, SQL, ML metrics, Dash callbacks/routes", "Current generated project artifacts"],
        ["COMPLETED AND VERIFIED", "Folium browser screenshot", "screenshots/folium_map.png; map tiles and marker cluster rendered"],
        ["PENDING", "Dash overview/site/orbit screenshots", "Capture in a local browser with localhost access enabled"],
        ["PENDING", "Live SpaceX API and Wikipedia refresh", "Retry when DNS/network access is available"],
        ["FAILED IN THIS ENVIRONMENT", "Headless browser to localhost", "Local browser TCP traffic is blocked; Dash screenshots still require a normal local browser"],
    ], [38*mm, 57*mm, 75*mm]),
]

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=18*mm,bottomMargin=22*mm,title="Final Capstone Report - SpaceX Falcon 9 Landing Prediction",author="IBM Applied Data Science Capstone")
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(f"Created {OUT} ({OUT.stat().st_size} bytes); missing_dash_screenshots={missing_dash_shots}; folium_screenshot={map_shot.is_file()}")
