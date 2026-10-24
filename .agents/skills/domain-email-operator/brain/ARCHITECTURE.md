# domain-email-operator architecture

Read [the procedure](../SKILL.md). This public role guide contains no client history or bundled external account access. Use the host tools and project architecture selected for the task.

## Flow

```
read state (dig + dashboard) -> inbound rules (Cloudflare Email Routing)
   -> sending domain (relay dashboard, MANUAL records, DNS-only)
   -> owner: SMTP key + Gmail Send mail as + codes
   -> verify: check-email-dns, relay logs, Show original (SPF/DKIM/DMARC)
```

