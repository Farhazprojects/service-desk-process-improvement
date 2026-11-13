# KPI framework

## Why the headline KPI has to change first

The desk reports one number today, the share of all tickets resolved inside SLA. That number is 83.8%.

Password tickets meet the SLA 98.8% of the time. When 60% of them move to self-service, they leave the count. The headline then falls to 83.3%, even though 372 fewer tickets breach and no ticket is handled worse than before.

If the desk keeps reporting the old number, the project will look like a failure in its first month. Measured on the same kind of tickets before and after, the SLA result rises from 78.2% to 81.0%. The KPI definition should be changed and agreed before go-live.

## KPIs

| KPI | Definition | Baseline | Target | Source | Reported |
|---|---|---|---|---|---|
| SLA result, comparable tickets | Tickets resolved inside the SLA hours for their priority, as a share of all tickets except Password and account unlock | 78.2% | 90% | Ticketing tool | Weekly |
| SLA result by priority | The same measure for P1, P2, P3 and P4 separately | 75.1%, 72.6%, 85.2%, 85.6% | 90% each | Ticketing tool | Weekly |
| Reassignment rate | Tickets reassigned at least once, as a share of all tickets | 22.8% | 12% | Ticketing tool | Weekly |
| Tickets reassigned three or more times | Count per month | 64 a month on average | Under 20 | Ticketing tool | Monthly |
| Self-service take-up | Self-service resets, as a share of self-service resets plus password tickets | 0% | 60% | Reset audit log and ticketing tool | Weekly |
| Portal share of intake | Portal tickets as a share of portal plus email tickets | 29.7% | 80% | Ticketing tool | Monthly |
| Agent handling hours | Sum of handling minutes on closed tickets, in hours | 8,722 a year | 7,800 a year | Ticketing tool | Monthly |
| Satisfaction score | Mean survey score from 1 to 5 | 4.0 | 4.2 | Survey | Monthly |
| Survey response rate | Tickets with a survey reply, as a share of closed tickets | 33.7% | Watch only | Survey | Monthly |

## Notes on the measures

Satisfaction comes from the 33.7% of tickets where the staff member replied to the survey. People with a strong view are more likely to reply, so the score may not represent everyone. The response rate is tracked for that reason.

Resolution time in the extract is elapsed hours. A real SLA clock usually pauses outside business hours and while the desk waits for the user. Before the baselines are used in a real project, the SLA calculation should be checked against how the ticketing tool counts time.

Self-service resets do not create tickets. Take-up therefore has to be measured from the reset audit log, which is why FR3 is a must-have requirement.

## Benefits realisation

| When | Check | Owner |
|---|---|---|
| Before go-live | New KPI definitions agreed, baselines recorded | Business analyst |
| 4 weeks after pilot | Reassignment rate for pilot users on the form against other users in the same weeks | Business analyst |
| 3 months after go-live | Take-up, portal share and handling hours against assumptions A2 and A3 | Service Desk Manager |
| 6 months after go-live | SLA result against the 90% target, decision on the second phase | Head of IT |
