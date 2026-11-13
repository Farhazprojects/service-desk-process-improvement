"""Current-state analysis of the service desk and the benefit estimate.

Run:  python src/ticket_analysis.py
Outputs: reports/tables/*.csv and reports/figures/*.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES, FIGS = ROOT / "reports" / "tables", ROOT / "reports" / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

BLUE, GREY, ORANGE = "#1f5a94", "#9aa5b1", "#d9822b"
plt.rcParams.update({
    "figure.dpi": 130, "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.titleweight": "bold",
    "axes.titlesize": 12, "axes.titlelocation": "left",
})

# Assumptions behind the benefit estimate. They are mine, not measured.
# docs/01_business_case.md lists them and says how each should be checked.
AGENT_COST_PER_HOUR = 55      # loaded cost of a service desk analyst
PASSWORD_DEFLECTION = 0.60    # share of password tickets moved to self-service
EMAIL_TO_PORTAL_SHIFT = 0.70  # share of email tickets moved to the portal form
SLA_TARGET_PCT = 90           # the desk's stated target for tickets inside SLA


def load() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "tickets.csv", parse_dates=["opened_at"])
    assert df.ticket_id.is_unique
    assert df[["category", "channel", "priority", "resolution_hours"]].notna().all().all()
    assert (df.resolution_hours > 0).all()
    assert ((df.resolution_hours > df.sla_target_hours) == (df.sla_breached == 1)).all()
    return df


def save(df: pd.DataFrame, name: str) -> pd.DataFrame:
    df.to_csv(TABLES / f"{name}.csv", index=False)
    return df


def baseline(df: pd.DataFrame) -> pd.DataFrame:
    kpis = pd.DataFrame([
        ("Tickets in 12 months", len(df)),
        ("Tickets per working day", round(len(df) / np.busday_count(
            df.opened_at.min().date(), df.opened_at.max().date()), 1)),
        ("Resolved inside SLA (%)", round(100 * (1 - df.sla_breached.mean()), 1)),
        ("Median hours to resolve", round(df.resolution_hours.median(), 1)),
        ("Tickets reassigned at least once (%)",
         round(100 * (df.reassignment_count > 0).mean(), 1)),
        ("Agent handling hours per year", round(df.handle_minutes.sum() / 60)),
        ("Satisfaction score, mean of 1 to 5", round(df.csat_score.mean(), 2)),
        ("Survey response rate (%)", round(100 * df.csat_score.notna().mean(), 1)),
    ], columns=["kpi", "value"])
    return save(kpis, "01_baseline_kpis")


def by_category(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("category").agg(
        tickets=("ticket_id", "size"),
        handle_hours=("handle_minutes", lambda s: s.sum() / 60),
        sla_met_pct=("sla_breached", lambda s: 100 * (1 - s.mean())),
        reassigned_pct=("reassignment_count", lambda s: 100 * (s > 0).mean()),
        median_resolution_hours=("resolution_hours", "median"),
    ).sort_values("tickets", ascending=False).reset_index()
    out["ticket_share_pct"] = 100 * out.tickets / out.tickets.sum()
    out["cumulative_share_pct"] = out.ticket_share_pct.cumsum()
    out = save(out.round(1), "02_by_category")

    fig, ax = plt.subplots(figsize=(8.5, 4))
    colours = [ORANGE if c.startswith("Password") else BLUE for c in out.category]
    bars = ax.barh(out.category[::-1], out.tickets[::-1], color=colours[::-1])
    ax.bar_label(bars, labels=[f"{v:.0f}%" for v in out.ticket_share_pct[::-1]],
                 padding=3)
    ax.set_xlabel("Tickets in 12 months")
    ax.set_title("Ticket volume by category")
    ax.set_xlim(0, out.tickets.max() * 1.12)
    fig.tight_layout()
    fig.savefig(FIGS / "01_volume_by_category.png")
    plt.close(fig)
    return out


def by_priority(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("priority").agg(
        tickets=("ticket_id", "size"),
        sla_target_hours=("sla_target_hours", "first"),
        median_resolution_hours=("resolution_hours", "median"),
        p90_resolution_hours=("resolution_hours", lambda s: s.quantile(0.9)),
        sla_met_pct=("sla_breached", lambda s: 100 * (1 - s.mean())),
    ).reset_index()
    return save(out.round(1), "03_sla_by_priority")


def by_reassignment(df: pd.DataFrame) -> pd.DataFrame:
    band = df.reassignment_count.clip(upper=3).map(
        {0: "0", 1: "1", 2: "2", 3: "3 or more"})
    out = df.assign(reassignments=band).groupby("reassignments").agg(
        tickets=("ticket_id", "size"),
        median_resolution_hours=("resolution_hours", "median"),
        sla_met_pct=("sla_breached", lambda s: 100 * (1 - s.mean())),
        avg_handle_minutes=("handle_minutes", "mean"),
        avg_csat=("csat_score", "mean"),
    ).reset_index()
    out["share_of_breaches_pct"] = (
        100 * df.assign(reassignments=band).groupby("reassignments")
        .sla_breached.sum().values / df.sla_breached.sum())
    out = save(out.round(2), "04_by_reassignment")

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    b = axes[0].bar(out.reassignments, out.sla_met_pct, color=BLUE)
    axes[0].bar_label(b, fmt="%.0f%%", padding=2)
    axes[0].axhline(SLA_TARGET_PCT, color=ORANGE, ls="--", lw=1)
    axes[0].set_title("Resolved inside SLA (dashed: 90% target)")
    axes[0].set_xlabel("Times the ticket was reassigned")
    axes[0].set_ylim(0, 105)
    b = axes[1].bar(out.reassignments, out.avg_csat, color=BLUE)
    axes[1].bar_label(b, fmt="%.1f", padding=2)
    axes[1].set_title("Average satisfaction score (1 to 5)")
    axes[1].set_xlabel("Times the ticket was reassigned")
    axes[1].set_ylim(0, 5)
    fig.tight_layout()
    fig.savefig(FIGS / "02_reassignment_impact.png")
    plt.close(fig)
    return out


def by_channel(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("channel").agg(
        tickets=("ticket_id", "size"),
        reassigned_pct=("reassignment_count", lambda s: 100 * (s > 0).mean()),
        sla_met_pct=("sla_breached", lambda s: 100 * (1 - s.mean())),
        avg_handle_minutes=("handle_minutes", "mean"),
        avg_csat=("csat_score", "mean"),
    ).reset_index()
    # Channel mix differs by category, so compare inside each category too.
    inside = (df.groupby(["category", "channel"]).reassignment_count
              .apply(lambda s: 100 * (s > 0).mean()).unstack().round(1).reset_index())
    save(inside, "05b_reassigned_pct_by_category_and_channel")
    out = save(out.round(2), "05_by_channel")

    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    b = ax.bar(out.channel, out.reassigned_pct,
               color=[ORANGE if c == "Email" else BLUE for c in out.channel])
    ax.bar_label(b, fmt="%.0f%%", padding=2)
    ax.set_ylabel("Tickets reassigned at least once (%)")
    ax.set_title("Reassignment rate by intake channel")
    fig.tight_layout()
    fig.savefig(FIGS / "03_reassignment_by_channel.png")
    plt.close(fig)
    return out


def arrival_pattern(df: pd.DataFrame) -> pd.DataFrame:
    wd = df[df.opened_at.dt.dayofweek < 5]
    weeks = wd.opened_at.dt.to_period("W").nunique()
    grid = (wd.groupby([wd.opened_at.dt.day_name(), wd.opened_at.dt.hour]).size()
            .unstack(fill_value=0) / weeks)
    grid = grid.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    grid = grid.loc[:, 7:18]
    save(grid.round(1).reset_index().rename(columns={"opened_at": "weekday"}),
         "06_arrivals_per_hour")

    fig, ax = plt.subplots(figsize=(9, 3.4))
    im = ax.imshow(grid.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(grid.shape[1]))
    ax.set_xticklabels([f"{h}:00" for h in grid.columns], fontsize=8)
    ax.set_yticks(range(5))
    ax.set_yticklabels(grid.index)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            v = grid.values[i, j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7,
                    color="white" if v > grid.values.max() * 0.6 else "black")
    ax.set_title("Average tickets opened per hour, by weekday")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(FIGS / "04_arrivals_heatmap.png")
    plt.close(fig)
    return grid


def benefit_estimate(df: pd.DataFrame) -> pd.DataFrame:
    """Estimate the yearly effect of the two proposed changes.

    1. Self-service password reset: a share of password tickets never
       reaches an agent, so their handling time is saved.
    2. Structured portal form: a share of email tickets moves to the portal.
       Those tickets are assumed to take on the portal's handling time and
       SLA result for the same category. This is an association in the
       data, not a tested cause, so it has to be confirmed in a pilot.
    """
    pw = df[df.category.str.startswith("Password")]
    pw_hours = PASSWORD_DEFLECTION * pw.handle_minutes.sum() / 60
    pw_tickets = PASSWORD_DEFLECTION * len(pw)

    rest = df[~df.category.str.startswith("Password")]
    cat_ch = rest.groupby(["category", "channel"]).agg(
        n=("ticket_id", "size"), handle=("handle_minutes", "mean"),
        breach=("sla_breached", "mean"))
    form_hours = form_breaches = 0.0
    for cat in rest.category.unique():
        email, portal = cat_ch.loc[(cat, "Email")], cat_ch.loc[(cat, "Portal")]
        moved = EMAIL_TO_PORTAL_SHIFT * email.n
        form_hours += moved * (email.handle - portal.handle) / 60
        form_breaches += moved * (email.breach - portal.breach)

    # Deflected password tickets leave the SLA calculation entirely.
    pw_breaches_removed = PASSWORD_DEFLECTION * pw.sla_breached.sum()
    new_total = len(df) - pw_tickets
    new_breaches = df.sla_breached.sum() - pw_breaches_removed - form_breaches
    out = pd.DataFrame([
        ("Password tickets deflected per year", round(pw_tickets)),
        ("Agent hours saved, password self-service", round(pw_hours)),
        ("Agent hours saved, portal form", round(form_hours)),
        ("Total agent hours saved per year", round(pw_hours + form_hours)),
        ("Share of current handling hours (%)",
         round(100 * (pw_hours + form_hours) / (df.handle_minutes.sum() / 60), 1)),
        ("Value of hours saved per year ($)",
         round((pw_hours + form_hours) * AGENT_COST_PER_HOUR)),
        ("SLA breaches avoided by portal form", round(form_breaches)),
        ("Current SLA met (%)", round(100 * (1 - df.sla_breached.mean()), 1)),
        ("Projected SLA met (%)", round(100 * (1 - new_breaches / new_total), 1)),
        # The headline falls because the easy password tickets leave the count.
        # Measured on the same tickets before and after, SLA improves.
        ("Current SLA met, excluding password tickets (%)",
         round(100 * (1 - rest.sla_breached.mean()), 1)),
        ("Projected SLA met, excluding password tickets (%)",
         round(100 * (1 - (rest.sla_breached.sum() - form_breaches) / len(rest)), 1)),
    ], columns=["measure", "value"])
    return save(out, "07_benefit_estimate")


def main() -> None:
    pd.set_option("display.width", 170)
    df = load()
    for title, fn in [("Baseline KPIs", baseline), ("By category", by_category),
                      ("SLA by priority", by_priority),
                      ("By reassignment count", by_reassignment),
                      ("By channel", by_channel),
                      ("Arrivals per hour", arrival_pattern),
                      ("Benefit estimate", benefit_estimate)]:
        print(f"== {title}\n{fn(df).round(1).to_string()}\n")
    print(pd.read_csv(TABLES / "05b_reassigned_pct_by_category_and_channel.csv")
          .to_string(index=False))
    monday = df[df.opened_at.dt.dayofweek == 0]
    print(f"\nMonday share of weekday tickets: "
          f"{100 * len(monday) / (df.opened_at.dt.dayofweek < 5).sum():.1f}%")


if __name__ == "__main__":
    main()
