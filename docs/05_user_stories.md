# User stories and acceptance criteria

The stories cover the must-have requirements. Acceptance criteria are written as Given, When, Then so a tester can run them as written.

## US1. Reset my own password

As a staff member, I want to reset my password myself, so that I can get back to work without waiting for the service desk.

Traces to FR1, FR3, NFR2, NFR3.

- Given I am a staff member with a standard account, when I pass the multi-factor identity check and enter a new password that meets the policy, then my password is changed and I can sign in with it.
- Given I have reset my password, when the reset completes, then a record is saved with my user ID, the time and the outcome.
- Given I am on the reset page, when I complete the steps without error, then the whole reset takes under three minutes.
- Given my new password does not meet the policy, when I submit it, then I see which rule it failed and my old password is unchanged.

## US2. Get help when self-service fails

As a staff member who cannot pass the identity check, I want a ticket raised for me, so that I am not locked out with nowhere to go.

Traces to FR4.

- Given I have failed the identity check three times, when the third attempt fails, then a ticket is created in the Password and account unlock category and I am shown the ticket number.
- Given a ticket was created this way, when an analyst opens it, then it shows that self-service was attempted and failed.

## US3. Block privileged accounts from self-service

As the Information Security Lead, I want administrator accounts excluded from self-service reset, so that a stolen phone cannot be used to take over a privileged account.

Traces to RULE1.

- Given an account is flagged as privileged, when its owner starts a self-service reset, then the reset is refused and the owner is told to phone the service desk.

## US4. Log a ticket with the right details

As a staff member, I want the form to ask for what the IT team needs, so that nobody has to email me later for more detail.

Traces to FR5, FR6.

- Given I am on the portal form, when I leave category, affected service or description empty, then I cannot submit and the empty field is marked.
- Given I choose a category, when the form updates, then I see only the extra fields for that category.
- Given I submit a complete form, when the ticket is created, then I receive the ticket number by email.

## US5. Request access to a system

As a staff member, I want to name the system, the access level and my approving manager in one request, so that the request goes to the right team first time.

Traces to FR7, FR8.

- Given I choose the Access request category, when the form updates, then system name, access level and approving manager are required.
- Given I submit an access request, when the ticket is created, then it is assigned to the team that owns the named system.

## US6. Receive tickets my team can act on

As a second-level support engineer, I want tickets to reach my team with the category and service filled in, so that I can start work without sending the ticket back.

Traces to FR8.

- Given a ticket is submitted through the portal, when it is assigned, then the resolver team matches the routing table for its category and affected service.
- Given no routing rule matches, when the ticket is submitted, then it is assigned to the service desk queue and not to a second-level team.

## US7. Be pointed to the form when I email

As a staff member who emails the old support address, I want an automatic reply with the form link, so that I know how to log my request.

Traces to FR9.

- Given the portal form is live, when I email the support mailbox, then I receive a reply within five minutes with a link to the form and the phone number for urgent problems.

## US8. See whether the change is working

As the Service Desk Manager, I want SLA and reassignment figures by category, priority and channel, so that I can tell whether the new process is working.

Traces to FR12, FR13, NFR6.

- Given I open the dashboard, when I view the SLA result, then I can see it for all tickets and for all tickets except password and account unlock.
- Given I open the dashboard, when I filter by channel or category, then the share of tickets reassigned updates to match.
- Given tickets were closed yesterday, when I open the dashboard today, then those tickets are included.

## US9. Spot tickets that keep bouncing

As the Service Desk Manager, I want to be told when a ticket has been reassigned more than twice, so that I can step in before it breaches.

Traces to RULE3.

- Given a ticket has been reassigned twice, when it is reassigned a third time, then I receive a notification with the ticket number and its reassignment history.
