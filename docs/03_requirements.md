# Requirements

Each requirement traces back to a business objective in the [business case](01_business_case.md) and to a finding in the data. Priority uses MoSCoW: must have, should have, could have, won't have this time.

## Business requirements

| ID | Requirement | Objective |
|---|---|---|
| BR1 | Staff can reset a password or unlock an account without contacting the service desk | O3 |
| BR2 | Every ticket arrives with enough information to be assigned to the right team the first time | O1, O2 |
| BR3 | Service desk performance is reported in a way that stays comparable before and after the change | O1, O4 |

## Functional requirements

| ID | Requirement | Priority | Traces to | Evidence |
|---|---|---|---|---|
| FR1 | The system shall let a user reset their own password after passing an identity check | Must | BR1 | Password tickets are 27.2% of volume |
| FR2 | The system shall let a user unlock their own account after passing an identity check | Must | BR1 | Same category |
| FR3 | The system shall record every self-service reset with user, time and outcome | Must | BR1 | Security audit need |
| FR4 | The system shall create a ticket for the service desk after three failed identity checks | Should | BR1 | Avoids locked-out users with no path |
| FR5 | The portal form shall require a category, an affected service and a description before a ticket can be submitted | Must | BR2 | Email tickets are reassigned 32.2% of the time, portal tickets 10.5% |
| FR6 | The portal form shall show extra fields that depend on the category chosen | Must | BR2 | Access requests are reassigned 44.0% of the time |
| FR7 | For an access request, the form shall require the system name, the access level and the approving manager | Must | BR2 | Same finding |
| FR8 | The system shall assign a submitted ticket to a resolver team using the category and affected service | Must | BR2 | Reassigned tickets are 66% of SLA breaches |
| FR9 | The support mailbox shall send an automatic reply with a link to the portal form | Should | BR2 | Email is 38% of tickets |
| FR10 | The system shall let an analyst log a phone ticket with the same required fields as the portal form | Should | BR2 | Phone tickets are reassigned 19.2% of the time |
| FR11 | The system shall suggest knowledge articles while the user types the description | Could | BR1 | Not tested in this analysis |
| FR12 | The dashboard shall report SLA results by category and by priority, with and without password tickets | Must | BR3 | Headline SLA falls from 83.8% to 83.3% when easy tickets leave the count |
| FR13 | The dashboard shall report the share of tickets reassigned, by channel and category | Must | BR3 | Objective O2 |
| FR14 | A chatbot for ticket intake | Won't | | Out of scope for this phase |

## Non-functional requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR1 | Self-service reset shall be available 24 hours a day, with 99.5% availability measured monthly | Must |
| NFR2 | A user shall be able to complete a password reset in under three minutes | Should |
| NFR3 | The identity check shall use multi-factor authentication approved by the Information Security Lead | Must |
| NFR4 | The portal form shall meet WCAG 2.1 level AA | Must |
| NFR5 | The portal form shall work on a mobile browser | Should |
| NFR6 | The dashboard shall refresh at least once a day | Should |
| NFR7 | Reset audit records shall be kept for 12 months | Must |

## Business rules

| ID | Rule |
|---|---|
| RULE1 | Privileged and administrator accounts cannot use self-service reset |
| RULE2 | A P1 ticket can always be raised by phone |
| RULE3 | A ticket reassigned more than twice is flagged to the Service Desk Manager |

## Open questions

| # | Question | Owner |
|---|---|---|
| Q1 | Which identity check is acceptable for staff without a company mobile? | Information Security Lead |
| Q2 | Can the ticketing tool route on two fields, or only on category? | Tool administrator |
| Q3 | Is the 90% SLA target for all tickets or per priority? | Head of IT |

## Acceptance of the requirements

The requirements are ready for build when the Head of IT has signed them off, the three open questions are closed, and the tool administrator has confirmed each must-have requirement can be configured.
