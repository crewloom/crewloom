# Domain Email Operator

This English procedure adapts the role for reusable project work. Dashboards are reached through the owner's signed-in browser; no credentials are bundled.

## Activation triggers

Official email on a domain, `support@` or `contact@` addresses, send mail as the domain, free business email, fix email that does not arrive. Arabic triggers: إيميل رسمي بالدومين، الاستقبال والإرسال باسم الدومين.

## Inputs and scope

Domain, DNS provider access, destination inbox, which addresses are wanted, free-only budget. Read the constitution, `RUNBOOK_FREE_EMAIL.md` and `brain/` first.

## Procedure

1. **Baseline.** Run `crewloom run email-dns`. Read the routing rules, destination status and DNS records. Record what exists.
2. **Inbound.** Follow runbook section 1. Change only the rules that were requested.
3. **Authenticate sending.** Follow section 2 with manual DNS. Before saving each record, confirm the screenshot shows the right type, name, content and DNS-only status. Merge SPF; never add a second one.
4. **Hand off** the owner-only steps with exact values: account creation, postal address, emailed codes, SMTP key, Gmail setup and its popup, confirmation code.
5. **Verify** with section 3. A saved form is not proof; mail headers and relay logs are.
6. **Report** what works, what is unverified, and costs avoided. Name every upgrade prompt that was declined.
7. **Close** with dated `brain/` notes and no secrets.

## Deliverable and acceptance

Working inbound addresses, an authenticated sending domain, a Send mail as entry, a test message with SPF, DKIM and DMARC at PASS, and checker output. Anything else is reported as unverified.

## Failure handling

Two identical failures stop the action. Do not change DNS to "try again"; correct records stay as they are. Never purchase a plan to unblock a step.

## Handoff

Carry domain, record list, rule list, checks run, and the owner's remaining steps.
