"""Generate the synthetic service desk ticket extract used in this case study.

The data is made up. The organisation is a fictional professional services
firm with about 1,200 staff and an internal IT service desk. I generate
twelve months of tickets with a fixed seed so the CSV can be rebuilt exactly.

The process problems written into the data are the ones the case study
then has to find: a large share of password tickets, email tickets that
arrive without enough detail and get passed between teams, and a Monday
morning peak.

Run:  python src/generate_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 11
N = 18000
START, END = pd.Timestamp("2025-10-01"), pd.Timestamp("2026-09-30")
OUT = Path(__file__).resolve().parents[1] / "data" / "tickets.csv"
rng = np.random.default_rng(SEED)

# category: (share of tickets, typical agent handling minutes, chance of reassignment)
CATEGORIES = {
    "Password and account unlock": (0.27, 9, 0.03),
    "Software": (0.19, 28, 0.22),
    "Hardware": (0.13, 40, 0.25),
    "Email and calendar": (0.12, 18, 0.15),
    "Network and VPN": (0.11, 32, 0.30),
    "Access request": (0.12, 22, 0.38),
    "Other": (0.06, 20, 0.28),
}
SLA_HOURS = {"P1": 4, "P2": 8, "P3": 24, "P4": 72}
# Median hours to resolve for a ticket that is never reassigned.
BASE_HOURS = {"P1": 1.6, "P2": 3.6, "P3": 9.5, "P4": 26.0}

# ---- when tickets arrive: weekdays, business hours, Monday morning peak
days = pd.date_range(START, END, freq="D")
day_w = np.array([1.45, 1.10, 1.00, 0.98, 0.90, 0.06, 0.04])[days.dayofweek]
date = rng.choice(days, N, p=day_w / day_w.sum())
hour_w = np.array([.2, .1, .1, .1, .2, .4, 1.2, 3.5, 8.5, 9.5, 8.0, 6.5,
                   4.5, 6.0, 6.5, 5.5, 4.5, 3.0, 1.2, .7, .5, .4, .3, .2])
hour = rng.choice(24, N, p=hour_w / hour_w.sum())
opened = (pd.to_datetime(date) + pd.to_timedelta(hour, unit="h")
          + pd.to_timedelta(rng.integers(0, 60, N), unit="m"))

category = rng.choice(list(CATEGORIES), N, p=[v[0] for v in CATEGORIES.values()])
channel = rng.choice(["Phone", "Email", "Portal"], N, p=[0.46, 0.38, 0.16])
priority = rng.choice(list(SLA_HOURS), N, p=[0.03, 0.14, 0.55, 0.28])
is_password = category == "Password and account unlock"
# Password tickets are almost never P1 or P2.
priority = np.where(is_password & np.isin(priority, ["P1", "P2"]), "P3", priority)

# ---- reassignments: email tickets lack detail, so they bounce more often
p_reassign = np.array([CATEGORIES[c][2] for c in category])
p_reassign = p_reassign * np.where(channel == "Email", 1.7,
                                   np.where(channel == "Portal", 0.6, 1.0))
p_reassign = np.clip(p_reassign, 0, 0.85)
reassignments = np.where(rng.random(N) < p_reassign,
                         1 + rng.binomial(3, 0.28, N), 0)

# ---- resolution time: lognormal, longer with every reassignment
base = np.array([BASE_HOURS[p] for p in priority])
base = base * np.where(is_password, 0.45, 1.0)
resolution_hours = base * rng.lognormal(0, 0.75, N) * (1 + 0.85 * reassignments)
resolution_hours = np.round(np.clip(resolution_hours, 0.05, None), 2)
sla_target = np.array([SLA_HOURS[p] for p in priority])
sla_breached = (resolution_hours > sla_target).astype(int)

handle_minutes = np.array([CATEGORIES[c][1] for c in category])
handle_minutes = np.round(
    handle_minutes * rng.lognormal(0, 0.35, N) * (1 + 0.45 * reassignments), 0)

# ---- satisfaction survey: about a third reply; breaches and bouncing hurt
replied = rng.random(N) < 0.34
score = 4.4 - 1.1 * sla_breached - 0.35 * reassignments + rng.normal(0, 0.8, N)
csat = np.where(replied, np.clip(np.round(score), 1, 5), np.nan)

df = pd.DataFrame({
    "opened_at": opened,
    "category": category,
    "channel": channel,
    "priority": priority,
    "sla_target_hours": sla_target,
    "reassignment_count": reassignments,
    "resolution_hours": resolution_hours,
    "handle_minutes": handle_minutes.astype(int),
    "sla_breached": sla_breached,
    "csat_score": csat,
}).sort_values("opened_at").reset_index(drop=True)
df.insert(0, "ticket_id", [f"INC{200000 + i}" for i in range(len(df))])

OUT.parent.mkdir(exist_ok=True)
df.to_csv(OUT, index=False, date_format="%Y-%m-%d %H:%M")
print(f"{len(df):,} tickets written, "
      f"SLA met {1 - df.sla_breached.mean():.1%}, "
      f"survey replies {df.csat_score.notna().mean():.1%}")
