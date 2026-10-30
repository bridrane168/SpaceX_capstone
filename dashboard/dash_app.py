"""Interactive SpaceX launch analytics dashboard. Run: python dashboard/app.py"""
from pathlib import Path
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

BASE = Path(__file__).resolve().parent.parent
CSV = BASE / "spacex_cleaned_data.csv"
df = pd.read_csv(CSV)
REQUIRED = {"Class", "LaunchSite", "Orbit"}
missing = REQUIRED - set(df.columns)
if missing:
    raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
df["Class"] = pd.to_numeric(df["Class"], errors="coerce")
df["PayloadMass"] = pd.to_numeric(df["PayloadMass"], errors="coerce") if "PayloadMass" in df else float("nan")
df = df.dropna(subset=["Class"])

app = Dash(__name__)
app.title = "SpaceX Launch Analytics"
DARK = {"template": "plotly_dark", "paper_bgcolor": "#1f2937", "plot_bgcolor": "#1f2937", "font_color": "#f9fafb"}
options = lambda col: [{"label": "All", "value": "All"}] + [{"label": str(v), "value": str(v)} for v in sorted(df[col].dropna().astype(str).unique())]
app.layout = html.Main([
 html.H1("SpaceX Falcon 9 Launch Analytics"),
 html.P("First stage landing outcomes across 90 historical launch records."),
 html.Div([html.Div([html.Label("Launch site"), dcc.Dropdown(id="site-filter", options=options("LaunchSite"), value="All", clearable=False)], style={"flex":"1","minWidth":"240px"}), html.Div([html.Label("Orbit"), dcc.Dropdown(id="orbit-filter", options=options("Orbit"), value="All", clearable=False)], style={"flex":"1","minWidth":"240px"})], className="filters", style={"display":"flex","flexWrap":"wrap","gap":"20px","margin":"20px 0"}),
 html.Div(id="kpis", className="kpis"),
 html.Div([dcc.Graph(id="outcome-chart"), dcc.Graph(id="site-chart"), dcc.Graph(id="payload-chart"), dcc.Graph(id="orbit-chart"), dcc.Graph(id="flight-chart")], className="charts", style={"display":"grid","gridTemplateColumns":"repeat(auto-fit,minmax(380px,1fr))","gap":"18px"})
], style={"background":"#111827","color":"#f9fafb","minHeight":"100vh","padding":"24px","fontFamily":"Arial,sans-serif"})
app.layout.style.update({"maxWidth":"1400px","margin":"auto"})

@app.callback(Output("kpis","children"), Output("outcome-chart","figure"), Output("site-chart","figure"), Output("payload-chart","figure"), Output("orbit-chart","figure"), Output("flight-chart","figure"), Input("site-filter","value"), Input("orbit-filter","value"))
def update(site, orbit):
 d=df.copy()
 if site != "All": d=d[d["LaunchSite"].astype(str)==site]
 if orbit != "All": d=d[d["Orbit"].astype(str)==orbit]
 n=len(d); yes=int((d.Class==1).sum()); no=int((d.Class==0).sum()); rate=100*yes/n if n else 0
 def card(label,value): return html.Div([html.Div(label,style={"color":"#9ca3af"}),html.H2(value)],style={"background":"#1f2937","padding":"16px","borderRadius":"10px","flex":"1","minWidth":"150px"})
 kpis=[card("Total launches",str(n)),card("Successful landings",str(yes)),card("Unsuccessful landings",str(no)),card("Landing success rate",f"{rate:.1f}%")]
 if n:
  outcomes=d.assign(Outcome=d.Class.map({0:"Unsuccessful",1:"Successful"})).groupby("Outcome",as_index=False).size()
  fig1=px.pie(outcomes,names="Outcome",values="size",hole=.45,title="Landing outcome distribution")
  sites=d.groupby("LaunchSite",as_index=False).agg(launches=("Class","size"),success_rate=("Class","mean")); sites.success_rate*=100
  fig2=px.bar(sites,x="LaunchSite",y="success_rate",hover_data=["launches"],title="Success rate by launch site",labels={"success_rate":"Success rate (%)"})
  payload=d.dropna(subset=["PayloadMass"]).assign(Outcome=d.Class.map({0:"Unsuccessful",1:"Successful"}))
  fig3=px.box(payload,x="Outcome",y="PayloadMass",color="Outcome",title="Payload mass versus landing outcome") if len(payload) else px.scatter(title="Payload mass unavailable")
  orbit_data=d.groupby("Orbit",as_index=False).agg(launches=("Class","size"),success_rate=("Class","mean")); orbit_data.success_rate*=100
  fig4=px.bar(orbit_data,x="Orbit",y="success_rate",hover_data=["launches"],title="Success rate by orbit",labels={"success_rate":"Success rate (%)"})
  if "FlightNumber" in d:
   flight=d.groupby("FlightNumber",as_index=False).agg(success_rate=("Class","mean")); fig5=px.scatter(flight,x="FlightNumber",y="success_rate",title="Landing outcomes by flight number",labels={"success_rate":"Observed success (0/1)"})
  else: fig5=px.scatter(title="Flight number is not present")
 else:
  fig1=px.pie(title="No launches for the selected filters")
  fig2=px.bar(title="No launches for the selected filters"); fig3=px.scatter(title="No payload data for the selected filters"); fig4=px.bar(title="No launches for the selected filters"); fig5=px.scatter(title="No launches for the selected filters")
 for f in [fig1,fig2,fig3,fig4,fig5]: f.update_layout(**DARK)
 return kpis,fig1,fig2,fig3,fig4,fig5

if __name__ == "__main__": app.run(debug=False,host="127.0.0.1",port=8050)
