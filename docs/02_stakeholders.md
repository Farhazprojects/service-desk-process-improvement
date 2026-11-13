# Stakeholder analysis

The organisation and the people in it are fictional. The roles are the ones I would expect to deal with on a service desk change.

## Stakeholder register

| Stakeholder | Interest in the change | Influence | Interest | How to engage |
|---|---|---|---|---|
| Head of IT (sponsor) | Wants the SLA met without extra headcount | High | High | Fortnightly update, signs off the business case |
| Service Desk Manager | Runs the desk and asked for two more analysts | High | High | Weekly working session, co-owns the requirements |
| Service desk analysts (9) | Do the work. Worried that self-service means fewer jobs | Medium | High | Workshop to map the current process, test the form |
| Second-level support teams | Receive reassigned tickets, often without enough detail | Medium | Medium | Interview one person per team, review routing rules |
| Information Security Lead | Must approve the identity check for password reset | High | Low | Early review of the reset method, formal sign-off |
| Finance Business Partner | Confirms the cost per hour and the budget | Medium | Low | One meeting to confirm assumptions A1 and A5 |
| Staff (about 1,200 users) | Want problems fixed quickly and dislike new forms | Low | Medium | Short survey, pilot group, clear communication at go-live |
| Ticketing tool administrator | Builds the form and the routing | Medium | Medium | Joins requirements reviews to confirm what the tool can do |

## Power and interest grid

| | Low interest | High interest |
|---|---|---|
| High influence | Keep satisfied: Information Security Lead | Manage closely: Head of IT, Service Desk Manager |
| Lower influence | Monitor: Finance Business Partner | Keep informed: analysts, second-level teams, staff, tool administrator |

## RACI for the main deliverables

R is responsible, A is accountable, C is consulted and I is informed.

| Deliverable | Head of IT | Service Desk Manager | Business analyst | Analysts | Security Lead | Tool administrator |
|---|---|---|---|---|---|---|
| Business case | A | C | R | I | I | I |
| Current-state process map | I | A | R | C | I | I |
| Requirements | A | C | R | C | C | C |
| Password reset identity check | I | C | C | I | A | R |
| Portal form and routing rules | I | A | C | C | I | R |
| KPI framework and dashboard | A | C | R | I | I | C |
| Pilot and go-live decision | A | R | C | C | C | C |

## How I would elicit requirements

Three methods would be used. A process workshop with the analysts would map what happens to a ticket today. Interviews with the second-level teams would cover what information is missing when a ticket reaches them. The ticket data would then be used to check what people said in the room.

The analysts are the group most likely to resist. Their concern about jobs is reasonable, and the business case answers it directly. The 880 hours saved is routine work, and the SLA gap shows there is plenty of other work for that time.
