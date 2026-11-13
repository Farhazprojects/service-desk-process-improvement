# Business case

## Problem statement

The IT service desk resolves 83.8% of tickets inside the agreed time. The target is 90%. Staff complain that tickets are passed between teams, and the Service Desk Manager has asked for two more analysts.

Before headcount is added, the Head of IT wants to know where the time goes and whether the process can be fixed first.

## Objectives

| # | Objective | Measure | Baseline | Target |
|---|---|---|---|---|
| O1 | Resolve more tickets inside SLA | Tickets inside SLA, excluding password tickets | 78.2% | 90% |
| O2 | Stop tickets being passed between teams | Tickets reassigned at least once | 22.8% | 12% |
| O3 | Release analyst time from routine work | Agent handling hours per year | 8,722 | 7,800 |
| O4 | Keep staff satisfied with the service | Mean satisfaction score | 4.0 | 4.2 |

The baselines come from the ticket analysis. The targets for O2 and O4 are proposals to be agreed with the Service Desk Manager.

## Scope

In scope: how tickets are logged, triaged and assigned, password and account unlock requests, and how the desk reports its performance.

Out of scope: replacing the ticketing tool, changing the SLA hours, the after-hours support contract, and security incident handling.

## What the data shows

Three findings shaped the options. The full analysis is in the [README](../README.md).

Firstly, password and account unlock requests are 27.2% of all tickets. Each one is quick, but together they take 803 analyst hours a year.

Secondly, reassignment is where the SLA is lost. Tickets that are never reassigned meet the SLA 92.9% of the time. After one reassignment the figure is 68.0%, and after three or more it is 33.6%. Reassigned tickets are 22.8% of volume and 66% of all breaches.

Thirdly, the intake channel is linked to reassignment. Email tickets are reassigned 32.2% of the time and portal tickets 10.5%. The gap holds inside every category, so it is not explained by the kind of ticket that arrives by email. An email has no required fields, and the analyst often has to guess the category.

## Options

| Option | Description | Addresses | Verdict |
|---|---|---|---|
| A. Do nothing | Keep the current process | Nothing | Rejected. The SLA stays below target |
| B. Hire two analysts | Add capacity to the desk | O1 in part | Not recommended yet. Reassignment is a routing problem, and more analysts would not fix it |
| C. Self-service password reset | Staff reset their own password after an identity check | O3 | Recommended |
| D. Structured portal form | Replace the support mailbox with a form that has required fields and routes by category | O1, O2, O3 | Recommended |
| C and D together | Both changes | O1 to O4 | Recommended option |

## Estimated benefit of the recommended option

| Measure | Value per year |
|---|---|
| Password tickets that no longer reach an analyst | 2,932 |
| Analyst hours saved by self-service | 482 |
| Analyst hours saved by the portal form | 398 |
| Total analyst hours saved | 880 (10.1% of handling time) |
| Value of the hours saved | $48,384 |
| SLA breaches avoided | 372 |
| Tickets inside SLA, excluding password tickets | 78.2% rising to 81.0% |

The 880 hours is about 17 hours a week. It is released capacity. It becomes a cash saving only if the hours are used to avoid a hire or reduce overtime.

## Costs and payback

| Item | Amount |
|---|---|
| One-off: configuration, form build, testing, staff communication | $35,000 |
| Ongoing: self-service licence and form upkeep, per year | $12,000 |
| Benefit per year | $48,384 |
| Net benefit per year after ongoing cost | $36,384 |
| Payback period | About 12 months |
| Net benefit over three years | $74,152 |

## Assumptions

Every figure above depends on these assumptions. None of them is measured. Each one has an owner who can confirm it.

| # | Assumption | Value used | How to confirm |
|---|---|---|---|
| A1 | Loaded cost of an analyst hour | $55 | Finance |
| A2 | Share of password tickets moved to self-service | 60% | Vendor reference sites, then a pilot |
| A3 | Share of email tickets moved to the portal form | 70% | Pilot with one business unit |
| A4 | A ticket moved to the portal behaves like today's portal tickets in the same category | As observed | Pilot. This is an association in the data and has not been tested |
| A5 | One-off and ongoing costs | $35,000 and $12,000 | Vendor quotes |

## What the recommended option does not fix

The two changes lift the SLA result to 81.0% on comparable tickets. The target is 90%. The remaining gap sits in Access requests (73.5% inside SLA, 44% reassigned) and in P1 and P2 tickets (75.1% and 72.6%).

A second phase should look at routing rules for access requests and at how high-priority tickets are escalated. I would not approve extra headcount until that work is done.

## Risks

| Risk | Likelihood | Impact | Response |
|---|---|---|---|
| Staff keep emailing analysts directly | High | Medium | Auto-reply on the old mailbox with the form link, and a four-week overlap |
| Self-service take-up is lower than 60% | Medium | Medium | Enrol staff at next password expiry and report take-up weekly |
| Identity check for password reset is too weak | Low | High | Security team signs off the method before build |
| Headline SLA appears to fall after go-live | High | Low | Change the reported KPI before go-live. See the [KPI framework](06_kpi_framework.md) |
