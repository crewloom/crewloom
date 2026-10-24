# Free launch stack (template)

Use as a template. Confirm each service's current free limits in its own dashboard; they change.

| Need | Free option | Notes |
|---|---|---|
| Inbound mail on a domain | Cloudflare Email Routing | Rules forward to one verified inbox. Does not send mail. |
| Outbound mail as the domain | Brevo free plan SMTP relay + Gmail "Send mail as" | Needs a verified sending domain and a real postal address. |
| DNS | Cloudflare DNS (free zone) | Add TXT and CNAME records; keep them DNS-only. |
| Social presence | LinkedIn Page, Facebook Page | Created from the owner's existing signed-in profile. |
| X account | Owner creates it | The agent must not create accounts. |
| Brand assets | Local SVG rendered to PNG | Inspect the render and run the asset checker. |

## Never use (paid or out of authority)

- Cloudflare Email Sending / Workers Paid, Premium page upgrades, ad products, domain purchases.
- Automatic DNS connection that grants a vendor access to the DNS account.

## User-only steps

Account creation, passwords, API or SMTP keys, emailed verification codes, payment, terms acceptance for the owner's own account, and any window the host browser tool cannot reach.
