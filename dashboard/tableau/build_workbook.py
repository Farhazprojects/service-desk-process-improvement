"""Build the Tableau packaged workbook for this project.

Run:  python dashboard/tableau/build_workbook.py
Needs: pip install tableauhyperapi
"""
import sys
from pathlib import Path
import pandas as pd
from twb_builder import DS, sheet, dashboard, build, declare_parameters

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / "dashboard" / "data" / "tickets_dashboard.csv").drop(columns=["opened_at"])
df["opened_date"] = pd.to_datetime(df.opened_date).dt.date
df["priority_label"] = df.priority + " (" + df.sla_target_hours.astype(str) + "h target)"
DIMS = ("sla_target_hours", "reassignment_count", "weekday_number", "hour", "is_password")
P = declare_parameters([("Parameter 1", "Share of password tickets moved to self-service", "real", 0.6, 0, 1, 0.05, "pct"),
                        ("Parameter 2", "Analyst cost per hour ($)", "integer", 55, 40, 80, 5, None)])
ds = DS("service_tickets", "Service desk tickets", df, dims=DIMS)
N = "COUNT([ticket_id])"
ds.calc("c_tickets", "Tickets", N, "int")
ds.calc("c_sla", "SLA met %", f"SUM([sla_met]) / {N}", "pct")
ds.calc("c_sla_x", "SLA met % excluding password tickets",
        "SUM(IF [is_password] = 0 THEN [sla_met] END) / SUM(IF [is_password] = 0 THEN 1 END)", "pct")
ds.calc("c_reassigned", "Reassigned %", f"SUM([is_reassigned]) / {N}", "pct")
ds.calc("c_breach_share", "Share of SLA breaches %", "SUM([sla_breached]) / MIN({FIXED : SUM([sla_breached])})", "pct")
ds.calc("c_ticket_share", "Share of tickets %", f"{N} / MIN({{FIXED : {N}}})", "pct")
HRS = "[Parameters].[Parameter 1] * SUM(IF [is_password] = 1 THEN [handle_hours] END)"
ds.calc("c_pw_hours", "Analyst hours saved per year", HRS, "int")
ds.calc("c_pw_saving", "Value of hours saved per year", f"{HRS} * [Parameters].[Parameter 2]", "usd")
ds.calc("c_pw_tickets", "Password tickets deflected per year",
        "[Parameters].[Parameter 1] * SUM([is_password])", "int")
ds.cols["resolution_hours"] = ("real", "measure", "Resolution hours", "n#,##0.0")
ds.cols["csat_score"] = ("real", "measure", "Satisfaction score", "n#,##0.0")

# Business hours only, for the arrivals heatmap. 53 calendar weeks are in the extract.
bh = df[(df.weekday_number <= 5) & df.hour.between(7, 18)][["ticket_id", "weekday", "weekday_number", "hour"]].copy()
bh["hour_label"] = bh.hour.map(lambda h: f"{h:02d}:00")
db = DS("tickets_business_hours", "Tickets in business hours", bh, dims=("weekday_number", "hour"))
db.calc("c_per_hour", "Tickets per hour (weekly average)", "COUNT([ticket_id]) / 53", "dec1")
db.calc("c_tickets", "Tickets", "COUNT([ticket_id])", "int")

S = []
kpi = lambda name, inst, title=None: S.append(sheet(ds, name, big=inst, title=title))
kpi("Ticket count", "usr:c_tickets:qk", "Tickets in 12 months"); kpi("SLA met", "usr:c_sla:qk", "Resolved inside SLA")
kpi("SLA met excluding password", "usr:c_sla_x:qk", "Inside SLA, excl. password tickets")
kpi("Reassigned", "usr:c_reassigned:qk", "Reassigned at least once")
kpi("Median resolution hours", "med:resolution_hours:qk", "Median hours to resolve")
kpi("Satisfaction", "avg:csat_score:qk", "Satisfaction (1 to 5)")
T = lambda inst: (inst, 0.9, "Target 90%")
S.append(sheet(ds, "SLA by month", cols=["none:year_month:nk"], rows=["usr:c_sla:qk"], mark="Line", refline=T("usr:c_sla:qk"),
               title="Tickets resolved inside SLA by month"))
S.append(sheet(ds, "Tickets by category", rows=["none:category:nk"], cols=["usr:c_tickets:qk"], mark="Bar",
               text="usr:c_ticket_share:qk", sort=("none:category:nk", "usr:c_tickets:qk", "DESC"),
               title="Tickets by category (label: share of all tickets)"))
S.append(sheet(ds, "SLA by priority", cols=["none:priority_label:nk"], rows=["usr:c_sla:qk"], mark="Bar", label=True,
               refline=T("usr:c_sla:qk"), title="Resolved inside SLA by priority"))
S.append(sheet(ds, "SLA by category", rows=["none:category:nk"], cols=["usr:c_sla:qk"], mark="Bar", label=True,
               sort=("none:category:nk", "usr:c_sla:qk", "ASC"), refline=T("usr:c_sla:qk"),
               title="Resolved inside SLA by category"))
band = lambda name, m, title, **k: S.append(sheet(ds, name, cols=["none:reassignment_band:nk"], rows=[m], mark="Bar",
                                                    label=True, title=title, **k))
band("SLA by reassignments", "usr:c_sla:qk", "Resolved inside SLA by number of reassignments", refline=T("usr:c_sla:qk"))
band("Satisfaction by reassignments", "avg:csat_score:qk", "Average satisfaction by number of reassignments", mark_color="#d9822b")
band("Breach share by reassignments", "usr:c_breach_share:qk", "Share of all SLA breaches by number of reassignments", mark_color="#9aa5b1")
band("Resolution hours by reassignments", "med:resolution_hours:qk", "Median hours to resolve by number of reassignments", mark_color="#9aa5b1")
S.append(sheet(ds, "Reassigned by category and channel", rows=["none:category:nk"], cols=["none:channel:nk"], mark="Square",
               color="usr:c_reassigned:qk", text="usr:c_reassigned:qk",
               title="Tickets reassigned at least once, by category and intake channel"))
S.append(sheet(db, "Arrivals by weekday and hour", rows=["none:weekday:nk"], cols=["none:hour_label:nk"], mark="Square",
               color="usr:c_per_hour:qk", text="usr:c_per_hour:qk", sort=("none:weekday:nk", "min:weekday_number:qk", "ASC"),
               title="Average tickets opened per hour, by weekday"))
S.append(sheet(db, "Tickets by weekday", cols=["none:weekday:nk"], rows=["usr:c_tickets:qk"], mark="Bar", label=True,
               sort=("none:weekday:nk", "min:weekday_number:qk", "ASC"), title="Tickets by weekday (business hours)"))
kpi("Password tickets deflected", "usr:c_pw_tickets:qk", "Password tickets deflected per year")
kpi("Hours saved", "usr:c_pw_hours:qk", "Analyst hours saved per year")
kpi("Value of hours saved", "usr:c_pw_saving:qk", "Value of hours saved per year")

note = "Synthetic data generated for a portfolio project."
six = ["Ticket count", "SLA met", "SLA met excluding password", "Reassigned", "Median resolution hours", "Satisfaction"]
D1 = dashboard("Service desk overview", "IT service desk: current state",
               [(n, i * 216 + (4 if i == 5 else 0) * 0, 56, 216 if i < 5 else 220, 104) for i, n in enumerate(six)] +
               [("SLA by month", 0, 160, 760, 330), ("SLA by priority", 760, 160, 540, 330),
                ("Tickets by category", 0, 490, 650, 330), ("SLA by category", 650, 490, 650, 330)],
               subtitle=note + " Click a category to filter the page.")
D2 = dashboard("Reassignment", "Where the SLA is lost: reassignment",
               [("SLA by reassignments", 0, 56, 433, 300), ("Satisfaction by reassignments", 433, 56, 433, 300),
                ("Breach share by reassignments", 866, 56, 434, 300),
                ("Resolution hours by reassignments", 0, 356, 433, 464), ("Reassigned by category and channel", 433, 356, 867, 464)],
               subtitle=note + " Tickets that stay with one team meet the SLA target. Reassigned tickets do not.")
D3 = dashboard("Demand and benefit", "Demand pattern and the benefit of self-service password reset",
               [("Arrivals by weekday and hour", 0, 56, 870, 330), ("Tickets by weekday", 870, 56, 430, 330),
                ("Password tickets deflected", 0, 470, 433, 150), ("Hours saved", 433, 470, 433, 150),
                ("Value of hours saved", 866, 470, 434, 150)],
               params=[("Parameter 1", 0, 396, 500, 66), ("Parameter 2", 520, 396, 400, 66)],
               subtitle=note + " Move the sliders to change the assumptions behind the estimate.", h=640)
acts = [("Filter by category", "Service desk overview", "Tickets by category")]
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("service_desk_dashboard.twbx")
build(out, [ds, db], S, [D1, D2, D3], params=P, acts=acts)
print(f"Wrote {out.name}")
