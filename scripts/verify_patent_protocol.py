#!/usr/bin/env python3
"""
verify_patent_protocol.py — Deterministic Guard and Validator for Scientific Monograph & Patent Specifications.
Part of Crewloom Sovereign Scientific Discovery & Patent Protocol Suite.
Checks manuscript structure only. Scientific evidence verification is unavailable;
the default publication gate fails closed even when structural checks pass.
"""

import sys
import re
import argparse
from pathlib import Path

def print_err(msg):
    sys.stderr.write(f"\033[91m[FAIL]\033[0m {msg}\n")

def print_ok(msg):
    sys.stdout.write(f"\033[92m[PASS]\033[0m {msg}\n")

def print_warn(msg):
    sys.stdout.write(f"\033[93m[WARN]\033[0m {msg}\n")

def audit_document(file_path: str, *, structure_only: bool = False) -> int:
    """Return zero only for an explicitly requested structural check, never certification."""
    path = Path(file_path)
    if not path.exists():
        print_err(f"Document file not found: {file_path}")
        return 2

    content = path.read_text(encoding="utf-8")
    if len(content.strip()) < 500:
        print_err("Document content is too brief to constitute a scientific patent specification (< 500 characters).")
        return 2

    failures = 0
    warnings = 0

    # 1. Sovereign Ownership & Inventor Check
    inventor_patterns = [
        r"INVENTOR.*:\s*.*(?:The Owner|المالك)",
        r"(?:Sovereign|Exclusive)\s+Owner",
        r"CREWLOOM.*SOVEREIGN"
    ]
    if any(re.search(p, content, re.IGNORECASE) for p in inventor_patterns):
        print_ok("Inventor attribution text present; ownership is not verified.")
    else:
        print_err("Rule Violation: Sovereign Inventor not attributed to 'The Owner'.")
        failures += 1

    # 2. Structural Patent Sections
    required_sections = [
        ("Abstract", r"(?:##\s*1\.\s*ABSTRACT|ABSTRACT\s*\(ملخص)"),
        ("Prior Art / Background", r"(?:##\s*2\.\s*BACKGROUND|PRIOR\s+ART)"),
        ("Detailed Description", r"(?:##\s*3\.\s*DETAILED|DETAILED\s+TECHNICAL)"),
        ("Claims", r"(?:##\s*4\.\s*CLAIMS|CLAIMS\s*\(عناصر)"),
    ]
    for name, pattern in required_sections:
        if re.search(pattern, content, re.IGNORECASE):
            print_ok(f"Required structural section present: {name}")
        else:
            print_err(f"Missing required patent section: {name}")
            failures += 1

    # 3. Patent Claims Syntax Validation
    # Independent claim must use "comprising"
    independent_claim = re.search(r"Independent\s+(?:System\s+)?Claim\s+1.*?(?=Claim\s+2|\Z)", content, re.DOTALL | re.IGNORECASE)
    if independent_claim:
        claim_text = independent_claim.group(0)
        if "comprising" in claim_text.lower():
            print_ok("Independent Claim 1 contains the transitional phrase 'comprising'; legal validity is not assessed.")
        else:
            print_err("Independent Claim 1 is missing the transitional phrase 'comprising'.")
            failures += 1
    else:
        print_err("Missing Independent Claim 1 specification.")
        failures += 1

    # Check for dependent claims
    dependent_claims = re.findall(r"\*{0,2}Claim\s+[2-9]\d*.*?:", content, re.IGNORECASE)
    if len(dependent_claims) >= 3:
        print_ok(f"Sufficient dependent claims detected ({len(dependent_claims)} dependent claims).")
    else:
        print_warn(f"Fewer than 3 dependent claims detected (found {len(dependent_claims)}). Recommended: ≥ 3.")
        warnings += 1

    # 4. Mathematical / Algorithmic Rigor Check
    math_indicators = [
        r"\$\$.*?\$\$",
        r"\\arg\\max",
        r"\\mathcal\{[A-Z]\}",
        r"\\sum_",
        r"\\le|\\ge"
    ]
    has_math = any(re.search(p, content, re.DOTALL) for p in math_indicators)
    if has_math:
        print_ok("Mathematical notation present; correctness is not verified.")
    else:
        print_err("Rule Violation: No formal mathematical equations or algorithmic bounds found.")
        failures += 1

    # 5. Comparative Benchmarks Table
    table_pattern = r"\|.*?Metric.*?\|.*?Baseline.*?\|"
    if re.search(table_pattern, content, re.IGNORECASE):
        print_ok("Benchmark table heading present; measurements are not verified.")
    else:
        print_err("Missing comparative benchmark table against industry baselines.")
        failures += 1

    # 6. TRIZ / Contradiction Formulation Check
    triz_indicators = [
        r"TRIZ",
        r"Asymmetric|Asymmetry",
        r"Speculative.*Neuro-Symbolic",
        r"Contradiction|تناقض"
    ]
    if any(re.search(p, content, re.IGNORECASE) for p in triz_indicators):
        print_ok("TRIZ terminology present; contradiction resolution is not verified.")
    else:
        print_warn("Explicit TRIZ contradiction terminology not strongly highlighted.")
        warnings += 1

    # Final Verdict
    print("\n--- AUDIT SUMMARY ---")
    if failures == 0:
        print_ok(f"Document {file_path} passes structural checks only (Warnings: {warnings}).")
        if structure_only:
            print_warn("Structure-only result: not scientific, legal, or publication approval.")
            return 0
        print_err("Publication blocked: citation resolution, claim evidence, and frozen benchmark verification are unavailable. Independent evidence review is required; structural checks cannot certify this protocol.")
        return 2
    else:
        print_err(f"Document {file_path} FAILED protocol verification with {failures} blocking violation(s).")
        return 2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', help='Manuscript path')
    parser.add_argument('--structure-only', action='store_true',
                        help='Check document structure without granting publication approval')
    args = parser.parse_args()
    sys.exit(audit_document(args.document, structure_only=args.structure_only))
