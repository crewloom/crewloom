---
name: domain-email-operator
description: Set up official email on the owner's domain for free: inbound routing through Cloudflare Email Routing and outbound sending through a free SMTP relay with Gmail Send mail as, then verify with DNS checks and a real test. Use for official email on a domain, support@ addresses, or sending mail as the domain. يُستدعى لإعداد إيميل رسمي بالدومين مجاناً (استقبال وإرسال).
---

# Domain Email Operator

## When to use

Use this role for domain email operator work. Match the task scope before activation; do not assume the host has external tools or account permissions. Activation triggers are listed in the English procedure.

## Brain and preflight

Read the workspace constitution and the five files in `brain/` before execution. Confirm the requested output language, input facts, authority, dependencies, and acceptance criteria.

## Procedure

1. Read current DNS and routing state before changing anything, and run the DNS checker for a baseline.
2. Create inbound routing rules to a verified destination inbox; leave the catch-all and unrelated records untouched.
3. Authenticate the sending domain manually with TXT and CNAME records kept DNS-only, merging SPF into a single record.
4. Hand the owner the SMTP key, password, verification-code and popup steps with exact values.
5. Verify with the DNS checker, relay logs and the message headers of a test sent to a different mailbox, then record the run.

## Deliverable and verification

Deliver the concrete artifact or findings, the evidence used, checks performed, and remaining limitations. Use Arabic or English as requested. Identify missing tools or facts explicitly; do not fill gaps with invented results.

## Closure

Update completed work, challenges, ideas, and backlog with concise records. Keep credentials and private customer records out of shared memory.

## Detailed procedures and specialist references

Read [the English procedure](references/PLAYBOOK.en.md) for project execution. Read [the full Arabic playbook](references/PLAYBOOK.ar.md) for role boundaries, step-by-step procedures, acceptance conditions, and handoff requirements. Read [the specialist architecture](references/ARCHITECTURE.ar.md) when selecting tools and project inputs.
- [Runbook](references/RUNBOOK_FREE_EMAIL.md)
The English entry point and shared constitution govern public task execution. Source-specific external documents are [project inputs](../../../documentation/PROJECT_INPUTS.md), not bundled private records.

## Included executable tools

- [check-email-dns](scripts/check_email_dns.py): Verify MX, a single SPF record, DMARC and optional Brevo records.

See the [tool catalog](../../../documentation/TOOLS.md) for commands, inputs, side effects and exit behavior.
