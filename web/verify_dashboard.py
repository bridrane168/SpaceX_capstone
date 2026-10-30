"""Verify the Plotly Dash data path, callback outputs, empty states, and routes."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dashboard.dash_app import app, df, update


assert len(df) == 90, f"Expected 90 dashboard rows, got {len(df)}"
assert (ROOT / "spacex_cleaned_data.csv").is_file()

cases = [
    ("All", "All", ["90", "60", "30", "66.7%"]),
    ("KSC LC 39A", "All", ["22", "17", "5", "77.3%"]),
    ("All", "GTO", ["27", "14", "13", "51.9%"]),
    ("KSC LC 39A", "GEO", ["0", "0", "0", "0.0%"]),
]
for site, orbit, expected_kpis in cases:
    kpis, *figures = update(site, orbit)
    actual_kpis = [str(card.children[-1].children) for card in kpis]
    assert actual_kpis == expected_kpis, (site, orbit, actual_kpis)
    assert len(figures) == 5
    if site == "KSC LC 39A" and orbit == "All":
        assert list(figures[1].data[0].x) == ["KSC LC 39A"]
    if site == "All" and orbit == "GTO":
        assert list(figures[3].data[0].x) == ["GTO"]
    if expected_kpis[0] == "0":
        titles = [figure.layout.title.text for figure in figures]
        assert titles == [
            "No launches for the selected filters",
            "No launches for the selected filters",
            "No payload data for the selected filters",
            "No launches for the selected filters",
            "No launches for the selected filters",
        ]
    print(f"PASS site={site!r} orbit={orbit!r}: KPIs={actual_kpis}, charts={len(figures)}")

client = app.server.test_client()
for route in ("/", "/_dash-layout", "/_dash-dependencies"):
    response = client.get(route)
    assert response.status_code == 200, (route, response.status_code)
    print(f"PASS Dash route {route}: HTTP {response.status_code}")

print(f"PASS CSV: {ROOT / 'spacex_cleaned_data.csv'} ({len(df)} rows)")
