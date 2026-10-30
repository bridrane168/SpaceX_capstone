"""Regenerate missing EDA tables and charts from the preserved 90-launch CSV."""
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
OUT = ROOT / "outputs"
FIG.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)
df = pd.read_csv(ROOT / "spacex_cleaned_data.csv")
df["Class"] = pd.to_numeric(df["Class"], errors="coerce")

orbit = df.groupby("Orbit", dropna=False).agg(
    launches=("Class", "size"), success_rate=("Class", "mean"), mean_payload_kg=("PayloadMass", "mean")
).reset_index().sort_values(["success_rate", "launches"], ascending=[False, False])
reuse = df.groupby("Reused", dropna=False).agg(
    launches=("Class", "size"), success_rate=("Class", "mean"), mean_payload_kg=("PayloadMass", "mean")
).reset_index().sort_values("Reused")
reuse["booster_reused"] = reuse["Reused"].map({False: "First-use / not reused", True: "Previously flown"})
flight = df.copy()
flight["flight_group"] = pd.cut(flight["FlightNumber"], [0, 30, 60, 90], labels=["1-30", "31-60", "61-90"], include_lowest=True)
flight_summary = flight.groupby("flight_group", observed=False).agg(launches=("Class", "size"), success_rate=("Class", "mean")).reset_index()
site = df.groupby("LaunchSite").agg(launches=("Class", "size"), success_rate=("Class", "mean")).reset_index()
payload = df.groupby("Class").agg(launches=("Class", "size"), mean_payload_kg=("PayloadMass", "mean"), median_payload_kg=("PayloadMass", "median"), min_payload_kg=("PayloadMass", "min"), max_payload_kg=("PayloadMass", "max")).reset_index()

# Orbit success-rate chart
plot = orbit.sort_values("success_rate")
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh(plot["Orbit"].astype(str), plot["success_rate"] * 100, color="#2563eb")
ax.set(xlabel="Observed landing success rate (%)", ylabel="Orbit", title="Landing success rate by orbit")
ax.set_xlim(0, 110)
for bar, (_, row) in zip(bars, plot.iterrows()):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f"{row.success_rate:.0%} (n={int(row.launches)})", va="center", fontsize=8)
fig.tight_layout(); fig.savefig(FIG / "orbit_success_rate.png", dpi=170); plt.close(fig)

# Reuse chart, with sample counts visible
fig, ax = plt.subplots(figsize=(7, 5))
labels = reuse["booster_reused"].tolist()
values = (reuse["success_rate"] * 100).tolist()
bars = ax.bar(labels, values, color=["#0f766e", "#f59e0b"])
ax.set(ylabel="Observed landing success rate (%)", title="Landing outcome by booster reuse", ylim=(0, 100))
for bar, (_, row) in zip(bars, reuse.iterrows()):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, f"{row.success_rate:.1%} (n={int(row.launches)})", ha="center", fontsize=9)
fig.tight_layout(); fig.savefig(FIG / "booster_reuse_success_rate.png", dpi=170); plt.close(fig)

# Compact, reproducible analysis table
parts = []
for name, table, group_col in [("site", site, "LaunchSite"), ("orbit", orbit, "Orbit"), ("booster_reuse", reuse, "Reused"), ("flight_group", flight_summary, "flight_group")]:
    copy = table.copy(); copy.insert(0, "analysis", name); copy = copy.rename(columns={group_col: "group"}); parts.append(copy)
summary_table = pd.concat(parts, ignore_index=True, sort=False)
summary_table.to_csv(OUT / "eda_summary.csv", index=False)
findings = {
    "source": "spacex_cleaned_data.csv",
    "records": int(len(df)),
    "launch_success_rate": float(df["Class"].mean()),
    "by_orbit": orbit.to_dict("records"),
    "by_booster_reused": reuse[["Reused", "launches", "success_rate", "mean_payload_kg"]].to_dict("records"),
    "by_launch_site": site.to_dict("records"),
    "by_flight_group": flight_summary.to_dict("records"),
    "interpretation": "These are descriptive rates from a 90-record dataset; groups have different sample sizes and the comparisons do not establish causal effects."
}
(OUT / "eda_findings.json").write_text(json.dumps(findings, indent=2, default=str), encoding="utf-8")
print("Dataset records:", len(df), "| overall success:", f"{df['Class'].mean():.1%}")
print("Orbit summary:\n", orbit.to_string(index=False))
print("Booster reuse summary:\n", reuse[["booster_reused", "launches", "success_rate"]].to_string(index=False))
print("Saved orbit_success_rate.png, booster_reuse_success_rate.png, eda_summary.csv, eda_findings.json")
