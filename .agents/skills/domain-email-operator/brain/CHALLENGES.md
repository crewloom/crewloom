# Challenges

Record the cause, attempted solution, result, and remaining blocker. Entries below are generalized from a real run; they hold no account identifiers or credentials.

### Routing was enabled but no address worked
- Cause: the dashboard showed routing as enabled while there were zero rules and the catch-all was set to drop.
- Fix: read the rules tab and counts, not the enabled badge; add a rule per address.

### Duplicate SPF risk
- Cause: the relay's guide suggests adding its own SPF record while one already exists.
- Fix: a domain may publish exactly one SPF record; merge includes. The relay used here needed none, so check before adding.

### Records not visible from the command line right after saving
- Cause: negative caching of an earlier empty answer.
- Fix: ask the relay to verify from its side, then re-query later; do not edit records that are already correct.

### SMTP key never existed
- Cause: generating a key sends a code by email; the code was not entered, so the keys table stayed empty and Send mail as could not authenticate.
- Fix: read the keys table first. Key generation and entering the code are the owner's steps.

### Test message never appeared
- Cause: a mailbox hides a message sent to itself when it is also the routing destination.
- Fix: test from a different mailbox.

### Setup window opened outside the controlled tabs
- Cause: Send mail as opens in a popup.
- Fix: hand the owner exact values; verify afterwards from the settings page listing.

### Postal address required
- Cause: the relay requires a real sender address and the owner had none fixed.
- Fix: the owner supplies a real, receivable address (PO box or virtual mailbox is acceptable). Never invent one.
