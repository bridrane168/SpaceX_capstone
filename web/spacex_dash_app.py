"""Interactive Dash dashboard. Install: pip install dash plotly pandas"""
from pathlib import Path
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

CSV = Path(__file__).parent / "data" / "spacex_cleaned_data.csv"
df = pd.read_csv(CSV)
app = Dash(__name__)
sites = sorted(df["LaunchSite"].dropna().unique())
orbits = sorted(df["Orbit"].dropna().unique())
app.layout = html.Div([
    html.H1("SpaceX Falcon 9 — Landing Analysis"),
    html.Div([
        html.Label("Launch site"),
        dcc.Dropdown(["All"] + sites, value="All", id="site-filter", clearable=False),
        html.Label("Orbit"),
        dcc.Dropdown(["All"] + orbits, value="All", id="orbit-filter", clearable=False),
    ], style={"maxWidth":"700px","margin":"auto"}),
    dcc.Graph(id="outcomes"),
    dcc.Graph(id="payload"),
    dcc.Graph(id="site-success"),
], style={"fontFamily":"Arial","padding":"24px"})

@app.callback(
    Output("outcomes","figure"), Output("payload","figure"), Output("site-success","figure"),
    Input("site-filter","value"), Input("orbit-filter","value")
)
def update(site, orbit):
    d = df.copy()
    if site != "All": d = d[d["LaunchSite"] == site]
    if orbit != "All": d = d[d["Orbit"] == orbit]
    outcomes = px.histogram(d, x="Class", title="Landing outcome counts", category_orders={"Class":[0,1]})
    payload = px.box(d, x="Class", y="PayloadMass", title="Payload mass by landing outcome")
    by_site = d.groupby("LaunchSite",as_index=False).agg(launches=("Class","size"),success_rate=("Class","mean"))
    success = px.bar(by_site,x="LaunchSite",y="success_rate",hover_data=["launches"],title="Observed success rate by launch site",range_y=[0,1])
    return outcomes,payload,success

if __name__ == "__main__":
    app.run(debug=True, port=8050)
