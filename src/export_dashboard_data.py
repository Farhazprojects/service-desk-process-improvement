"""Export the ticket table with the extra columns the dashboards need.

Run:  python src/export_dashboard_data.py
Output: dashboard/data/tickets_dashboard.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dashboard" / "data"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ROOT / "data" / "tickets.csv", parse_dates=["opened_at"])
df["opened_date"] = df.opened_at.dt.strftime("%Y-%m-%d")
df["year_month"] = df.opened_at.dt.strftime("%Y-%m")
df["weekday"] = df.opened_at.dt.day_name()
df["weekday_number"] = df.opened_at.dt.dayofweek + 1      # Monday = 1, for sorting
df["hour"] = df.opened_at.dt.hour
df["is_reassigned"] = (df.reassignment_count > 0).astype(int)
df["reassignment_band"] = df.reassignment_count.clip(upper=3).map(
    {0: "0", 1: "1", 2: "2", 3: "3 or more"})
df["is_password"] = df.category.str.startswith("Password").astype(int)
df["sla_met"] = 1 - df.sla_breached
df["handle_hours"] = (df.handle_minutes / 60).round(3)
df.to_csv(OUT / "tickets_dashboard.csv", index=False, date_format="%Y-%m-%d %H:%M")

kpi = pd.read_csv(ROOT / "reports" / "tables" / "01_baseline_kpis.csv").set_index("kpi").value
assert round(100 * df.sla_met.mean(), 1) == kpi["Resolved inside SLA (%)"]
assert round(100 * df.is_reassigned.mean(), 1) == kpi["Tickets reassigned at least once (%)"]
assert round(df.handle_hours.sum()) == kpi["Agent handling hours per year"]
print(f"tickets_dashboard  {len(df):,} rows, {df.shape[1]} columns. "
      f"Reconciliation PASS against the baseline KPIs")
