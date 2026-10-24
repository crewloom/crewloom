#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flag launch-copy claims that need evidence before publishing.

Read-only; standard library only. A finding means "prove it or relabel it", not "this is false".
An inventory file whitelists claims already verified: each non-comment line is a case-insensitive
substring; a finding whose line contains it is suppressed.
Exit codes: 0 = no findings, 1 = findings, 2 = unreadable input.
"""
import argparse
import json
import re
import sys

COMPETITORS = (r'claude code|devin|cursor|copilot|windsurf|aider|cline|codex|chatgpt|gemini|'
               r'كلود كود|ديفين|كيرسر|كوبايلوت')
RULES = (
    ('measured-number', re.compile(r'\b\d+(?:\.\d+)?\s?(?:ms|µs|us|kb|mb|gb|x faster|× faster|%\s+faster)\b', re.I),
     'Performance or size number: cite the measurement or label it a target or simulation.'),
    ('competitor-comparison', re.compile(
        rf'\b(?:better|faster|cheaper|smarter|safer|beats?|outperforms?|replaces?)\b[^.\n]{{0,30}}?(?:{COMPETITORS})'
        rf'|(?:{COMPETITORS})[^.\n]{{0,20}}\b(?:alternative|killer)\b'
        rf'|(?:أفضل من|أسرع من|أرخص من|أذكى من|بديل)[^.\n]{{0,20}}?(?:{COMPETITORS})', re.I),
     'Named-competitor comparison needs an independent, dated benchmark.'),
    ('absolute-guarantee', re.compile(
        r'\b100\s?%|\bguarantee[sd]?\b|\bnever (?:fails?|breaks?|leaks?)\b|\bzero[- ](?:risk|leak|telemetry|destruction)\b'
        r'|\bunbreakable\b|ضمان|مضمون|مستحيل أن|بدون أي مخاطر', re.I),
     'Absolute guarantee: state the tested scope and its limits instead.'),
    ('superlative', re.compile(r'\b(?:#1|number one|world[- ]class|best[- ]in[- ]class|the best|industry[- ]leading)\b'
                               r'|الأفضل في|رقم 1|الأول عالميا', re.I),
     'Superlative without a source.'),
    ('unverified-benchmark', re.compile(r'\bbenchmark(?:ed|s)?\b|\bproven\b|\bscientifically\b|مثبت علميا', re.I),
     'Benchmark or proof wording: link the reproducible evidence.'),
    ('production-ready', re.compile(r'\bproduction[- ]ready\b|\benterprise[- ]grade\b|\bbattle[- ]tested\b|جاهز للإنتاج', re.I),
     'Readiness claim: only valid after the release gates pass; say "early preview" otherwise.'),
)


def load_inventory(path):
    with open(path, encoding='utf-8') as handle:
        return [line.strip().lower() for line in handle if line.strip() and not line.lstrip().startswith('#')]


def scan(text, allowed=()):
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        lowered = line.lower()
        if any(item in lowered for item in allowed):
            continue
        for code, pattern, advice in RULES:
            for match in pattern.finditer(line):
                findings.append({'line': number, 'rule': code, 'text': match.group(0), 'advice': advice})
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--file', required=True, help='Campaign copy (Markdown or text).')
    parser.add_argument('--inventory', help='Verified-claims file: one allowed substring per line.')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        with open(args.file, encoding='utf-8') as handle:
            text = handle.read()
        allowed = load_inventory(args.inventory) if args.inventory else []
    except (OSError, UnicodeDecodeError) as exc:
        print(f'Cannot read input: {exc}', file=sys.stderr)
        return 2
    findings = scan(text, allowed)
    if args.json:
        print(json.dumps({'findings': findings}, ensure_ascii=False))
    elif findings:
        for item in findings:
            print(f"line {item['line']}: [{item['rule']}] \"{item['text']}\" - {item['advice']}")
    else:
        print('PASS no unverified-claim patterns found')
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
