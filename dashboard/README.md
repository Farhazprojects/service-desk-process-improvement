# Dashboard build pack: service desk

This folder holds what is needed to build the service desk dashboard in Power BI and in Tableau. The dashboards themselves are not built yet. Power BI Desktop needs Windows, and neither tool was installed on the machine where the analysis was written.

The dashboard is the one described in user story US8 and requirements FR12 and FR13.

## Files

| File | Use |
|---|---|
| `data/tickets_dashboard.csv` | One row per ticket, 18,000 rows, with the extra columns below |
| `measures.dax` | Power BI measures |
| `portfolio_theme.json` | Power BI colour theme |

The CSV is written by `python src/export_dashboard_data.py`. The script checks the SLA result, reassignment rate and handling hours against the baseline KPIs before it finishes.

## Columns added for the dashboard

| Column | Meaning |
|---|---|
| `opened_date`, `year_month`, `weekday`, `weekday_number`, `hour` | Parts of the opened time |
| `is_reassigned`, `reassignment_band` | Reassigned at least once, and a band of 0, 1, 2, 3 or more |
| `is_password` | 1 for Password and account unlock tickets |
| `sla_met` | 1 when the ticket was resolved inside its SLA hours |
| `handle_hours` | Handling minutes divided by 60 |

In Power BI, name the table `tickets` and sort `weekday` by `weekday_number`.

## Pages

### Page 1. Service desk overview

| Visual | Fields |
|---|---|
| Cards | Tickets, SLA Met %, SLA Met % ex Password, Reassigned %, Median Resolution Hours, Average Satisfaction |
| Line chart | `year_month` on the axis, SLA Met % and SLA Met % ex Password as values, SLA Target as a constant line |
| Bar chart | `category` by Tickets, with Ticket Share % as the data label |
| Table | `priority`, Tickets, `sla_target_hours`, Median Resolution Hours, SLA Met % |
| Slicers | `category`, `channel`, `priority` |

### Page 2. Reassignment

| Visual | Fields |
|---|---|
| Column chart | `reassignment_band` by SLA Met %, with SLA Target as a constant line |
| Column chart | `reassignment_band` by Average Satisfaction |
| Column chart | `reassignment_band` by Share of Breaches % |
| Matrix | `category` on rows, `channel` on columns, Reassigned % as the value, with a colour scale |

### Page 3. Demand and benefit

| Visual | Fields |
|---|---|
| Matrix | `weekday` on rows, `hour` on columns, Tickets as the value, with a colour scale. Filter to hours 7 to 18 and Monday to Friday |
| Column chart | `weekday` by Tickets |
| Slicers | Password Deflection and Analyst Hourly Cost what-if parameters |
| Cards | Password Hours Saved, Password Saving $ |

The heatmap shows ticket counts for the year. The main README quotes an average per hour, which is the count divided by 53 weeks.

The benefit cards cover the password change only. The portal form estimate needs a category-by-channel comparison that is easier to keep in the Python script.

## Tableau

Connect to `tickets_dashboard.csv`. Create two parameters, `Password Deflection` (float, 0 to 1, default 0.6) and `Analyst Hourly Cost` (integer, 40 to 80, default 55). Then create these calculated fields.

| Name | Formula |
|---|---|
| SLA Met % | `SUM([Sla Met]) / COUNT([Ticket Id])` |
| SLA Met % ex Password | `SUM(IF [Is Password] = 0 THEN [Sla Met] END) / SUM(IF [Is Password] = 0 THEN 1 END)` |
| Reassigned % | `SUM([Is Reassigned]) / COUNT([Ticket Id])` |
| Share of Breaches % | `SUM([Sla Breached]) / TOTAL(SUM([Sla Breached]))` |
| Survey Response % | `COUNT([Csat Score]) / COUNT([Ticket Id])` |
| Password Hours Saved | `[Password Deflection] * SUM(IF [Is Password] = 1 THEN [Handle Hours] END)` |
| Password Saving $ | `[Password Hours Saved] * [Analyst Hourly Cost]` |

Median resolution time is `MEDIAN([Resolution Hours])` and satisfaction is `AVG([Csat Score])`. The two heatmaps are highlight tables. Add a reference line at 0.9 for the SLA target.

## Numbers the dashboard must match

With no slicer applied, the dashboard should show these values. They come from the ticket analysis.

| Measure | Value |
|---|---|
| Tickets | 18,000 |
| SLA met | 83.8% |
| SLA met, excluding password tickets | 78.2% |
| Reassigned | 22.8% |
| Median resolution hours | 10.4 |
| Average satisfaction | 4.0 |
| SLA met with no reassignment, and with 3 or more | 92.9% and 33.6% |
| Reassigned, access request by email | 63.4% |
| Password hours saved at 60% deflection | 482 |
| Password saving at $55 an hour | $26,483 |
