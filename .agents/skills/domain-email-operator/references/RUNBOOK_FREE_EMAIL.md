# Free email on your own domain

Limits and screens change. Confirm each free tier in its dashboard; do not assume.

## 0. Baseline

`crewloom run email-dns -- --domain example.org --sender brevo` lists what exists. Read routing rules and counts in the dashboard; an "enabled" badge is not proof that any address works.

## 1. Inbound (Cloudflare Email Routing)

1. The destination inbox must show **Verified**. Add and verify it first if absent (the owner clicks the emailed link).
2. Create one **Send to an email** rule per address (for example `support@`). Choose the verified destination. Leave the catch-all unchanged unless asked.
3. Test from a **different** mailbox. A message sent from the destination mailbox to itself may not appear.

## 2. Outbound (free SMTP relay + Gmail)

Use a relay with a free tier (the reference path is Brevo). Free tiers have daily caps; read the plan page.

1. **Owner:** create the relay account, complete its profile and real postal address, choose the free plan.
2. Add the sending domain. Choose **Manual** DNS setup. Do not use the automatic option, which asks for access to your DNS account.
3. Add the records exactly as shown. Types are normally one TXT on the apex (verification code), two CNAME DKIM records, and one TXT on `_dmarc` such as `v=DMARC1; p=none; rua=mailto:<address the relay shows>`. Keep CNAMEs **DNS only** (not proxied). Never publish a second SPF record.
4. Ask the relay to verify, then authenticate the domain, then add the sender address.
5. **Owner:** generate an SMTP key (an emailed code is required), copy it once, then in Gmail add the address under Settings > Accounts and Import > Send mail as. Server, port 587, TLS, the relay login, and the key as the password. Untick "Treat as an alias". Enter the confirmation code Gmail sends to the new address.
6. Do not enable IP restriction for SMTP keys; Gmail's sending addresses change.

## 3. Verify

- `crewloom run email-dns -- --domain example.org --sender brevo` must print PASS.
- Send from the new address to a **different** mailbox. In the received message open the original headers: SPF, DKIM and DMARC must say PASS.
- The relay's log page should list the message.

## Never

Paid email-sending plans, ad or premium upgrades, entering the owner's password or keys, or inventing a postal address.
