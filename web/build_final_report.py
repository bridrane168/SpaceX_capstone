"""Build a detailed, evidence-linked IBM capstone report from saved project outputs."""
import csv, json, math
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Final_Capstone_Report.pdf"
REPO="https://github.com/bridrane168/SpaceX_capstone"
REPO_FILES=["SpaceX_Capstone_Basics_Final.ipynb","web/collect_spacex_api.py","web/scrape_launches.py","web/eda_analysis.py","web/sql_analysis.py","web/spacex_launch_sites.html","web/train_models.py","dashboard/dash_app.py"]
NAVY=colors.HexColor("#0B1D3A"); TEAL=colors.HexColor("#0F766E"); PALE=colors.HexColor("#EAF2F7")
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name="Sec",parent=styles["Heading1"],fontSize=16,leading=19,textColor=NAVY,spaceBefore=8,spaceAfter=6,keepWithNext=True))
styles.add(ParagraphStyle(name="Sub",parent=styles["Heading2"],fontSize=11,leading=14,textColor=TEAL,spaceBefore=6,spaceAfter=4,keepWithNext=True))
styles.add(ParagraphStyle(name="Body2",parent=styles["BodyText"],fontSize=8.5,leading=11,spaceAfter=5))
styles.add(ParagraphStyle(name="Small2",parent=styles["BodyText"],fontSize=7.4,leading=9,spaceAfter=3))
styles.add(ParagraphStyle(name="Cap",parent=styles["BodyText"],fontSize=7.7,leading=9,alignment=1,textColor=colors.HexColor("#475569"),spaceAfter=5))
styles.add(ParagraphStyle(name="Warn",parent=styles["BodyText"],fontSize=8.5,leading=12,textColor=colors.HexColor("#854D0E"),backColor=colors.HexColor("#FFF7E6"),borderColor=colors.HexColor("#E7B34B"),borderWidth=.7,borderPadding=6,spaceBefore=4,spaceAfter=6))
styles.add(ParagraphStyle(name="CoverSub",parent=styles["BodyText"],fontSize=10,leading=13,textColor=colors.HexColor("#DCE7F2"),alignment=1))
styles.add(ParagraphStyle(name="CoverMeta",parent=styles["BodyText"],fontSize=8,leading=10,textColor=colors.HexColor("#DCE7F2"),alignment=1))

def readcsv(path):
    with open(ROOT/path,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def para(s,style="Body2"):
    s=str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return Paragraph(s,styles[style])
def tbl(rows,widths=None,small=False):
    st="Small2" if small else "Body2"
    t=Table([[para(x,st) for x in row] for row in rows],colWidths=widths,repeatRows=1,hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#CBD5E1")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,PALE]),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return t
def pic(path,height=60*mm):
    path=ROOT/path
    if not path.is_file(): return None
    im=Image(str(path)); scale=min(165*mm/im.imageWidth,height/im.imageHeight,1)
    im.drawWidth=im.imageWidth*scale; im.drawHeight=im.imageHeight*scale; im.hAlign="CENTER"
    return im
def footer(c,doc):
    if doc.page>1:
        c.saveState(); c.setStrokeColor(colors.HexColor("#CBD5E1")); c.line(20*mm,14*mm,190*mm,14*mm); c.setFont("Helvetica",7.5); c.setFillColor(colors.HexColor("#475569")); c.drawString(20*mm,9*mm,"IBM Applied Data Science Capstone | Evidence report"); c.drawRightString(190*mm,9*mm,f"Page {doc.page}"); c.restoreState()

data=readcsv(Path("spacex_cleaned_data.csv"))
metrics=readcsv(Path("outputs/model_metrics.csv")); reports=readcsv(Path("outputs/classification_reports.csv"))
eda=json.loads((ROOT/"outputs/eda_findings.json").read_text(encoding="utf-8"))
scrape=json.loads((ROOT/"scraping_output/scraping_summary.json").read_text(encoding="utf-8"))
api=json.loads((ROOT/"api_output/collection_status.json").read_text(encoding="utf-8"))
retries=json.loads((ROOT/"outputs/external_retry_evidence.json").read_text(encoding="utf-8"))
year_counts=readcsv(Path("scraping_output/launch_counts_by_year.csv"))
scraped=readcsv(Path("scraping_output/falcon_launch_history.csv"))
miss_dash=[n for n in ["dash_overview.png","dash_filter_launch_site.png","dash_filter_orbit.png"] if not (ROOT/"screenshots"/n).is_file()]
map_exists=(ROOT/"screenshots/folium_map.png").is_file()
api_retry=next((r for r in retries if r.get("source")=="spacex_api"),{})
wiki_rows=[r for r in retries if r.get("source")=="wikipedia"]
site_rows=[r for r in eda["by_launch_site"]]
reuse_rows=[r for r in eda["by_booster_reused"]]
flight_rows=[r for r in eda["by_flight_group"]]

story=[]
# Cover
cover=Table([[Paragraph("IBM APPLIED DATA SCIENCE CAPSTONE",styles["CoverSub"])],[Spacer(1,18*mm)],[Paragraph("Falcon 9 First-Stage<br/>Landing Prediction",ParagraphStyle("Cover",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=25,leading=30,textColor=colors.white,alignment=1))],[Paragraph("Data collection, analysis, model results, and interactive evidence",styles["CoverSub"])],[Spacer(1,20*mm)],[Paragraph("EVIDENCE STATUS: Scrape coverage complete through the published October 2026 history; live API data unavailable; genuine Dash screenshots pending.",ParagraphStyle("CoverWarn",parent=styles["BodyText"],fontSize=8.5,leading=12,textColor=colors.HexColor("#854D0E"),backColor=colors.HexColor("#FFF7E6"),borderColor=colors.HexColor("#E7B34B"),borderWidth=.7,borderPadding=6,alignment=1))],[Paragraph("Prepared from project execution outputs | 30 October 2026",styles["CoverMeta"])]],colWidths=[170*mm],rowHeights=[20*mm,15*mm,38*mm,19*mm,15*mm,31*mm,18*mm])
cover.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER"),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10)]))
story += [Spacer(1,12*mm),cover,PageBreak()]

story += [para("Executive summary","Sec"),para("The capstone preserves a 90-launch modeling dataset and separately completes a live Wikipedia collection of 699 unique Falcon 9 flights (flight numbers 1–699) across 2010–2026. The model dataset has a 66.7% landing-success rate. A stratified 23-record test set gave Decision Tree 86.96% accuracy and 0.903 F1; Logistic Regression scored 82.61% accuracy and 0.882 F1. Seven SQLite queries, EDA figures, a Folium map capture, and verified Dash callbacks/routes are included."),para("Limits are explicit: 57 of the 699 scraped launches have unknown payload mass; the SpaceX API returned no JSON on the latest attempt (HTTP 522); the 90-row model sample is small and imbalanced; and genuine Dash browser screenshots could not be captured because Chrome timed out connecting to localhost.","Warn")]
story += [para("1. Introduction and objectives","Sec"),para("The objective is to examine the supplied Falcon 9 first-stage landing dataset and evaluate baseline classifiers for `Class` (0 = unsuccessful, 1 = successful). Work includes data quality checks, outcome analysis by site/payload/orbit/flight/reuse, SQL summaries, interactive mapping, model comparison, and a Plotly Dash application."),para("Repository and methodology sources","Sub"),Paragraph(f'GitHub repository: <link href="{REPO}">{REPO}</link>',styles["Body2"])]
for f in REPO_FILES: story.append(Paragraph(f'<link href="{REPO}/blob/main/{f}">{f}</link>',styles["Small2"]))

story += [PageBreak(),para("2. Data collection and data-wrangling methodology","Sec"),para("SpaceX API collection","Sub"),para(f"The collector targets {api.get('url')} using bounded requests and JSON normalization. Its preserved initial run made {api.get('attempts')} attempts; DNS resolution failed before an HTTP response, so the saved status is null, `api_output/launches_raw.json` is 0 bytes, and `api_output/launches.csv` is absent. A later network-enabled GET returned HTTP {api_retry.get('http_status')} with an HTML error body ({api_retry.get('response_bytes')} bytes), so JSON parsing and data export were not performed. The exact response is `api_output/live_retry_response.txt`; the initial DNS error remains in `api_output/collection_status.json` and `api_output/launches_error.txt`."),para("Wikipedia web scraping","Sub"),para(f"The scraper sends a student-project User-Agent and parses the main current page plus four linked archive pages. All five live requests returned HTTP 200. It inspected {scrape['tables_found']} HTML tables and selected {scrape['candidate_tables_selected']} tables matching the launch-history schema. The page family covers published past Falcon 9 launches from 2010 through the current 2026 section; year 2011 has no listed launch. The data are Falcon 9 only: nonnumeric Falcon Heavy identifiers are excluded."),tbl([["Collection check","Verified result"],["Pages / HTTP status","5 pages; HTTP 200 for each"],["Inspected / selected tables",f"{scrape['tables_found']} / {scrape['candidate_tables_selected']}"],["Launch rows / unique keys",f"{len(scraped)} / {scrape['unique_launch_keys']}"],["Flight number range",f"{scrape['flight_number_range'][0]}–{scrape['flight_number_range'][1]}"],["Duplicate keys / rows",f"{scrape['duplicate_rows_after_deduplication']} / 0"],["Missing payload mass",str(scrape['missing_by_column']['payload_mass_kg'])],["Excel workbook",f"113 sheets; {scrape['excel_export']}"]],[60*mm,110*mm])]
# Per-year record count table
story += [para("Records by launch year","Sub")]
row=["Year","Launches","Year","Launches"]
for i in range(0,len(year_counts),2):
 a=year_counts[i]; b=year_counts[i+1] if i+1<len(year_counts) else {"source_year":"","launches":""}
 if i==0: yr_rows=[row]
 yr_rows.append([a["source_year"],a["launches"],b["source_year"],b["launches"]])
story.append(tbl(yr_rows,[32*mm,40*mm,32*mm,40*mm]))
story += [para("Normalization removes reference markers, parses UTC launch timestamps, attaches continuation descriptions to their launch rows, aggregates multiple payload rows per flight/time, derives numeric payload mass where reported, and removes duplicate flight/time keys. `source_year` and `source_table_index` are integers, `flight_number` is string, `payload_mass_kg` is float, and descriptors are text. The 57 null payload masses remain missing; no value is imputed in the scraped-history export. The earlier 285-row 2025–2026 partial extract is retained as `falcon_launch_history_partial_2025_2026.csv` for traceability.")]

story += [PageBreak(),para("3. Data quality and modeling preparation","Sec"),para("The model and dashboard use the preserved `spacex_cleaned_data.csv`, not the 699-row scrape. This keeps the prediction analysis aligned with the provided capstone dataset. It contains 90 rows × 18 columns: 30 class-0 and 60 class-1 records, no exact duplicate rows, and 26 missing values confined to `LandingPad`. Rows were retained. Numeric predictors use median imputation and standard scaling; categorical predictors use most-frequent imputation and one-hot encoding, fitted inside each training pipeline.")]

story += [para("4. EDA and data-visualization methodology","Sec"),para("Executed summaries compare binary outcomes and success rates across launch site, payload mass, orbit, flight-number bands, and whether the booster was previously flown. Counts accompany rates so small groups remain visible. Histograms and bar charts describe the observed 90-row sample; associations are descriptive, not causal."),para("Launch sites","Sub")]
srows=[["Site","Launches","Successful","Observed success"]]
for r in site_rows:
 n=int(r["launches"]); rate=float(r["success_rate"]); srows.append([r["LaunchSite"],str(n),str(round(n*rate)),f"{rate:.1%}"])
story.append(tbl(srows,[65*mm,30*mm,35*mm,40*mm]))
story += [para("Payload mass by observed outcome","Sub")]
pay=readcsv(Path("sql_output/payload_by_outcome.csv")); prows=[["Class","Records with mass","Mean kg","Minimum kg","Maximum kg"]]
for r in pay: prows.append([r["Class"],r["records_with_payload"],r["mean_payload_kg"],r["min_payload_kg"],r["max_payload_kg"]])
story.append(tbl(prows,[25*mm,42*mm,32*mm,32*mm,32*mm],small=True))
# Three descriptive figures
for f,cap in [("figures/outcome_distribution.png","Outcome distribution: 60 successful and 30 unsuccessful launches."),("figures/success_by_site.png","Observed landing-success rate by site; KSC 17/22, VAFB 10/13, CCAFS 33/55."),("figures/payload_by_outcome.png","Payload mass distributions by outcome; the group means are descriptive.")]:
    im=pic(f,46*mm)
    if im: story += [im,para(cap,"Cap")]
story += [PageBreak(),para("Orbit, flight-number, and booster-reuse findings","Sec")]
orows=[["Orbit","Launches","Successes","Rate","Mean payload kg"]]
for r in sorted(eda["by_orbit"],key=lambda x:-int(x["launches"])):
 n=int(r["launches"]); rate=float(r["success_rate"]); orows.append([r["Orbit"],str(n),str(round(n*rate)),f"{rate:.1%}",f"{float(r['mean_payload_kg']):,.0f}"])
story.append(tbl(orows,[35*mm,27*mm,28*mm,28*mm,45*mm],small=True))
story.append(para("For orbit groups with at least five records, GTO has 27 launches (14 successes; 51.9%), ISS 21 (13; 61.9%), VLEO 14 (12; 85.7%), PO 9 (6; 66.7%), LEO 7 (5; 71.4%), and SSO 5 (5; 100%). The 100% rate in SSO is based on only five records. Previously flown boosters: 29/37 successes (78.4%); first-use/not-reused: 31/53 (58.5%). Flight groups 1–30, 31–60, 61–90: 13/30 (43.3%), 22/30 (73.3%), 25/30 (83.3%). Changing mission mix and small samples prevent causal claims."))
for f,cap in [("figures/orbit_success_rate.png","Observed landing-success rate by orbit; count labels indicate group size."),("figures/booster_reuse_success_rate.png","Observed outcomes by booster reuse; sample counts are shown."),("figures/success_by_flight_group.png","Observed success by flight-number group.")]:
 im=pic(f,42*mm)
 if im: story += [im,para(cap,"Cap")]

story += [PageBreak(),para("5. EDA with SQL analysis","Sec"),para("The SQL runner creates an in-memory SQLite database from the cleaned 90-row CSV, loads the table, executes seven queries, and writes paired `.sql` and `.csv` outputs under `sql_output/`. These are executed results, not query text alone.")]
site_sql=readcsv(Path("sql_output/success_by_site.csv")); sqlsite=[["Launch site","Total launches","Success rate"]]+[[r["LaunchSite"],r["total_launches"],f"{100*float(r['success_rate']):.1f}%"] for r in site_sql]
story += [para("Key SQL results","Sub"),tbl([["Query","Verified result"],["Total launches","90"],["Binary outcomes","Class 0: 30 (33.3%); Class 1: 60 (66.7%)"],["Launches by site","CCAFS: 55; KSC: 22; VAFB: 13"],["Mean payload by outcome","Class 0: 4,784.56 kg; Class 1: 6,765.16 kg"],["Landing outcome × booster recovery","8 groups; see launch_outcomes.csv"],["Orbit-level launches, success, and mean mass","11 groups; see orbit_analysis.csv"]],[68*mm,102*mm])]
story += [para("Success rates by site","Sub"),tbl(sqlsite,[80*mm,45*mm,45*mm])]
story += [para("Payload analysis","Sub")]
story.append(tbl([["Class","Records with payload","Mean kg","Min kg","Max kg"]]+[[r["Class"],r["records_with_payload"],r["mean_payload_kg"],r["min_payload_kg"],r["max_payload_kg"]] for r in pay],[25*mm,42*mm,32*mm,32*mm,32*mm],small=True))
outcomes=readcsv(Path("sql_output/launch_outcomes.csv"))
story += [para("Landing outcome by recovery result","Sub"),tbl([["Outcome","Class","Launches"]]+[[r["Outcome"],r["Class"],r["launches"]] for r in outcomes],[80*mm,35*mm,35*mm],small=True)]
sqlorbit=readcsv(Path("sql_output/orbit_analysis.csv"))
story += [para("SQL orbit output","Sub"),tbl([["Orbit","Launches","Success rate","Mean payload kg"]]+[[r["Orbit"],r["launches"],f"{100*float(r['success_rate']):.1f}%",f"{float(r['mean_payload_kg']):,.2f}"] for r in sqlorbit],[45*mm,35*mm,40*mm,60*mm],small=True)]

story += [PageBreak(),para("6. Folium interactive map","Sec"),para("The Folium HTML uses the project launch-site coordinates, clustered markers, popup counts, and observed site success rates. Leaflet 1.9.3, jQuery 3.7.1, and MarkerCluster 1.1.0 are bundled locally; OpenStreetMap basemap tiles still require internet. Browser verification observed Leaflet loaded, two visible marker icons, one cluster containing two Florida sites, 30 loaded map tiles, and no script errors.")]
if map_exists:
 im=pic("screenshots/folium_map.png",125*mm)
 if im: story += [im,para("Genuine browser capture of the interactive Folium map; California marker and Florida two-site cluster are visible.","Cap")]
else: story.append(para("PENDING: genuine Folium screenshot is missing.","Warn"))
story += [para("7. Predictive analysis: classification methodology","Sec"),para("The target is `Class`; selected inputs are FlightNumber, PayloadMass, Flights, GridFins, Reused, Legs, Block, ReusedCount, Orbit, LaunchSite, and Serial. A stratified 75/25 split produced 67 training and 23 test observations (random state 42). Numeric and categorical preprocessing is fit within each model pipeline on the training subset only. Logistic Regression and a depth-5 Decision Tree use class balancing. Held-out predictions supply the metrics; the test set contains 15 successful and 8 unsuccessful cases. Possible leakage remains because some features, such as landing configuration, may not be known before launch.")]
mrows=[["Model","Accuracy","Precision","Recall","F1","ROC-AUC","TN FP FN TP"]]
for r in metrics: mrows.append([r["Model"],f"{100*float(r['Accuracy']):.2f}%",f"{float(r['Precision']):.3f}",f"{float(r['Recall']):.3f}",f"{float(r['F1 score']):.3f}",f"{float(r['ROC-AUC']):.3f}",f"{r['TN']} {r['FP']} {r['FN']} {r['TP']}"])
story += [para("Verified predictive results","Sub"),tbl(mrows,[38*mm,23*mm,23*mm,20*mm,18*mm,20*mm,28*mm],small=True),para("Decision Tree was selected by held-out F1 (0.903 vs. 0.882). Logistic Regression had higher ROC-AUC (0.850 vs. 0.842). Both estimates are uncertain because the test set has only 23 records.")]
cr=[{"Model":r["Model"],"Class":r["Class"],"precision":r["precision"],"recall":r["recall"],"f1-score":r["f1-score"],"support":r["support"]} for r in reports]
crows=[["Model","Class / average","Precision","Recall","F1","Support"]]
for r in cr: crows.append([r["Model"],r["Class"],f"{float(r['precision']):.3f}",f"{float(r['recall']):.3f}",f"{float(r['f1-score']):.3f}",str(int(float(r["support"])))])
story += [para("Per-class, macro, and weighted classification results","Sub"),tbl(crows,[43*mm,38*mm,27*mm,24*mm,22*mm,16*mm],small=True)]
for f,cap in [("figures/confusion_logistic_regression.png","Logistic Regression confusion matrix (TN=4, FP=4, FN=0, TP=15)."),("figures/confusion_decision_tree.png","Decision Tree confusion matrix (TN=6, FP=2, FN=1, TP=14)."),("figures/roc_curves.png","ROC curves computed from held-out predictions.")]:
 im=pic(f,53*mm)
 if im: story += [im,para(cap,"Cap")]

story += [PageBreak(),para("8. Plotly Dash interactive dashboard","Sec"),para("`dashboard/dash_app.py` is the Plotly Dash application, separate from the standalone HTML fallback. It loads the preserved 90-row CSV from a path relative to the app source. The layout provides four KPI cards (total launches, successful landings, unsuccessful landings, success rate), site and orbit filters, and five charts (outcome, site success, payload, orbit, and flight number)."),tbl([["Verified callback selection","Total / success / unsuccessful / rate","Chart behavior"],["All","90 / 60 / 30 / 66.7%","5 charts"],["KSC LC 39A","22 / 17 / 5 / 77.3%","5 charts"],["GTO","27 / 14 / 13 / 51.9%","5 charts"],["KSC LC 39A + GEO (empty)","0 / 0 / 0 / 0.0%","5 explicit empty-state charts"]],[53*mm,67*mm,50*mm],small=True),para("Dash 4.5.0 was installed; `/`, `/_dash-layout`, and `/_dash-dependencies` returned HTTP 200 through Flask's test client. KPI and chart callbacks were directly exercised. Chrome was pointed at the running local app but returned `ERR_CONNECTION_TIMED_OUT` for `127.0.0.1:8050`; therefore, no genuine Dash browser screenshot exists. The static matplotlib preview is not used as runtime evidence.","Warn")]
for n in ["dash_overview.png","dash_filter_launch_site.png","dash_filter_orbit.png"]:
 p=ROOT/"screenshots"/n
 if p.is_file():
  im=pic(Path("screenshots")/n,88*mm)
  if im: story += [im,para(n,"Cap")]
if miss_dash: story.append(para("PENDING genuine Dash browser screenshots: "+", ".join(miss_dash)+". Capture them from the running app on a machine/browser that can reach localhost.","Warn"))

story += [PageBreak(),para("9. Findings, limitations, and conclusion","Sec"),para("The supplied 90-row model sample shows 60 successes and 30 unsuccessful outcomes. The Decision Tree had the highest held-out F1, while Logistic Regression had slightly higher ROC-AUC. Rates vary by site, orbit, flight group, and booster reuse; these patterns are descriptive and confounded by changing missions and sample size. The larger 699-flight scrape improves historical coverage, but it is a separate web-sourced dataset and was not substituted into the course model."),para("Data-collection scope is improved: live Wikipedia data were fetched from five pages (HTTP 200 each) and combined into 699 distinct Falcon 9 flights spanning 2010–2026. Fifty-seven payload masses remain unknown. The SpaceX API is not represented as successful: earlier requests failed DNS and a later live request got HTTP 522 without JSON. Dash callbacks and routes work, while genuine browser screenshots remain pending due localhost transport failure."),tbl([["Status","Component","Evidence / remaining action"],["COMPLETED AND VERIFIED","Full published Wikipedia scrape","699 unique records; five pages; 113 tables; HTTP 200"],["COMPLETED AND VERIFIED","EDA, SQL, model results","Executed outputs and verified predictions in project"],["COMPLETED AND VERIFIED","Folium map screenshot","screenshots/folium_map.png; rendered tiles and cluster"],["COMPLETED AND VERIFIED","Dash source, callbacks, KPIs, routes","Dash 4.5.0 and outputs/dashboard_validation.txt"],["PENDING","Three genuine Dash screenshots","Capture in a browser with localhost access"],["PENDING","SpaceX API JSON/CSV","Latest HTTP 522 returned HTML; retry when endpoint is reachable"],["FAILED IN THIS ENVIRONMENT","Chrome to local Dash host","ERR_CONNECTION_TIMED_OUT at 127.0.0.1:8050"]],[37*mm,59*mm,74*mm],small=True)]

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=17*mm,bottomMargin=22*mm,title="Final Capstone Report - SpaceX Falcon 9 Landing Prediction",author="IBM Applied Data Science Capstone")
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(f"Created {OUT} ({OUT.stat().st_size} bytes); scraped_rows={len(scraped)}; API_retry_http={api_retry.get('http_status')}; missing_dash_screenshots={miss_dash}; folium_screenshot={map_exists}")
