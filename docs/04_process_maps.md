# Process maps

GitHub draws these diagrams from the Mermaid code in this file.

## Current state (as-is)

```mermaid
flowchart TD
    A([Staff member has an IT problem]) --> B{How do they contact the desk?}
    B -->|Phone 46%| C[Analyst asks questions and logs the ticket]
    B -->|Email 38%| D[Email lands in the shared mailbox]
    B -->|Portal 16%| E[Staff member fills in the portal form]
    D --> F[Analyst reads the email and guesses the category]
    C --> G{Can the desk fix it?}
    E --> G
    F --> G
    G -->|Yes| H[Analyst resolves the ticket]
    G -->|No| I[Assign to a second-level team]
    I --> J{Right team and enough detail?}
    J -->|Yes| K[Second-level team resolves the ticket]
    J -->|No| L[Ticket is sent back or passed on]
    L --> M[Analyst emails the staff member for more detail]
    M --> I
    H --> N([Ticket closed])
    K --> N
```

### Pain points

| # | Step | Problem | Evidence |
|---|---|---|---|
| P1 | Email intake | An email has no required fields, so the analyst has to guess | 32.2% of email tickets are reassigned, against 10.5% for the portal |
| P2 | Assign to second level | Tickets reach the wrong team or arrive without enough detail | 22.8% of tickets are reassigned at least once |
| P3 | Sent back or passed on | Each loop adds waiting time | Median time to resolve is 8.2 hours with no reassignment and 27.1 hours with two |
| P4 | Analyst resolves | Password resets fill the queue | 4,887 password tickets a year |
| P5 | Whole process | Monday morning demand is far above the rest of the week | 11.9 tickets an hour at 9:00 on Monday, 7.7 to 8.6 on other days |

## Future state (to-be)

```mermaid
flowchart TD
    A([Staff member has an IT problem]) --> B{Password or account unlock?}
    B -->|Yes| C[Self-service reset with identity check]
    C --> D{Check passed?}
    D -->|Yes| E([Reset complete, no ticket])
    D -->|No, three times| F[Ticket created for the desk]
    B -->|No| G{Is it urgent, P1?}
    G -->|Yes| H[Phone the desk]
    G -->|No| I[Portal form with required fields for the category]
    H --> J[Analyst logs the ticket with the same required fields]
    I --> K[System assigns the ticket by category and service]
    J --> K
    F --> K
    K --> L{Can the desk fix it?}
    L -->|Yes| M[Analyst resolves the ticket]
    L -->|No| N[Second-level team resolves the ticket]
    N --> O{Reassigned more than twice?}
    O -->|Yes| P[Flag to Service Desk Manager]
    P --> N
    O -->|No| Q([Ticket closed])
    M --> Q
```

## What changes

| Pain point | Change | Requirement |
|---|---|---|
| P1 | The mailbox is replaced by a form with required fields | FR5, FR6, FR9 |
| P2 | The system assigns the ticket using category and service | FR7, FR8 |
| P3 | Repeated reassignment is flagged to the manager | RULE3, FR13 |
| P4 | Staff reset their own password | FR1, FR2 |
| P5 | Not changed by this phase | See note below |

The Monday peak is partly password resets after the weekend, so self-service should reduce it. I have not measured by how much, because the ticket extract does not record why a password was reset. Rostering for the Monday peak is a separate recommendation for the Service Desk Manager.
