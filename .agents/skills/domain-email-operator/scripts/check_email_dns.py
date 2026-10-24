#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check a domain's email DNS: MX, a single SPF record, DMARC, and optional Brevo records.

Read-only. Uses `dig` for live lookups, or a recorded JSON file for offline review and tests.
Exit codes: 0 = no findings, 1 = findings, 2 = invalid input or `dig` unavailable.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys

DOMAIN_RE = re.compile(r'^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$')
BREVO_CODE_RE = re.compile(r'^brevo-code:[0-9a-f]{16,}$')


def clean(value):
    """Strip dig's quoting and joined TXT chunks."""
    return re.sub(r'"\s+"', '', value.strip()).strip('"')


def dig_lookup(record_type, name):
    result = subprocess.run(['dig', '+short', '+time=5', '+tries=2', record_type, name],
                            capture_output=True, text=True, timeout=30, check=False)
    return [clean(line) for line in result.stdout.splitlines() if line.strip()]


def offline_lookup(records):
    def lookup(record_type, name):
        return [clean(item) for item in records.get(f'{record_type} {name}', [])]
    return lookup


def check(domain, lookup, sender):
    findings = []

    def finding(code, message):
        findings.append({'code': code, 'message': message})

    mx = lookup('MX', domain)
    if not mx:
        finding('mx-missing', f'No MX record for {domain}; inbound mail cannot arrive.')

    txt = lookup('TXT', domain)
    spf = [item for item in txt if item.lower().startswith('v=spf1')]
    if len(spf) > 1:
        finding('spf-multiple', f'{len(spf)} SPF records found; merge them into one record, '
                'because receivers treat several SPF records as a permanent error.')
    elif not spf:
        finding('spf-missing', f'No SPF record on {domain}.')

    dmarc = [item for item in lookup('TXT', f'_dmarc.{domain}') if item.upper().startswith('V=DMARC1')]
    if not dmarc:
        finding('dmarc-missing', f'No DMARC record on _dmarc.{domain}.')

    if sender == 'brevo':
        if not any(BREVO_CODE_RE.match(item) for item in txt):
            finding('brevo-code-missing', f'No brevo-code TXT record on {domain}.')
        for selector in ('brevo1', 'brevo2'):
            name = f'{selector}._domainkey.{domain}'
            targets = lookup('CNAME', name)
            if not targets:
                finding(f'dkim-{selector}-missing', f'No CNAME for {name}.')
            elif not any(target.rstrip('.').endswith('.dkim.brevo.com') for target in targets):
                finding(f'dkim-{selector}-target', f'{name} does not point at *.dkim.brevo.com: {targets}.')
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--domain', required=True)
    parser.add_argument('--sender', choices=('none', 'brevo'), default='none',
                        help='Also verify the records a Brevo sending domain needs.')
    parser.add_argument('--records-json', help='Recorded answers {"TYPE name": ["value", ...]} for offline use.')
    parser.add_argument('--json', action='store_true', help='Emit machine-readable output.')
    args = parser.parse_args(argv)

    domain = args.domain.strip().lower().rstrip('.')
    if not DOMAIN_RE.match(domain):
        print(f'Invalid domain: {args.domain!r}', file=sys.stderr)
        return 2

    if args.records_json:
        try:
            with open(args.records_json, encoding='utf-8') as handle:
                records = json.load(handle)
            if not isinstance(records, dict):
                raise ValueError('top-level value must be an object')
        except (OSError, ValueError) as exc:
            print(f'Cannot read records file: {exc}', file=sys.stderr)
            return 2
        lookup = offline_lookup(records)
    else:
        if shutil.which('dig') is None:
            print('`dig` is not installed; supply --records-json instead.', file=sys.stderr)
            return 2
        lookup = dig_lookup

    findings = check(domain, lookup, args.sender)
    if args.json:
        print(json.dumps({'domain': domain, 'sender': args.sender, 'findings': findings}, ensure_ascii=False))
    elif findings:
        for item in findings:
            print(f"FAIL {item['code']}: {item['message']}")
    else:
        print(f'PASS {domain}: MX, single SPF, DMARC' + (', Brevo records' if args.sender == 'brevo' else ''))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
