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

    # 1. Human Inventorship & Assignee Attribution Check (matches single or co-inventors per Pannu factors)
    inventor_patterns = [
        r"(?:INVENTOR|INVENTORS|المخترع|المخترعون).*?:\s*\S+",
        r"(?:Sovereign|Exclusive)\s+Owner",
        r"CREWLOOM.*SOVEREIGN"
    ]
    if any(re.search(p, content, re.IGNORECASE) for p in inventor_patterns):
        print_ok("Inventor/Assignee attribution field present (conception provenance must be verified manually).")
    else:
        print_err("Missing statutory human inventor attribution field (35 U.S.C. § 100(f)).")
        failures += 1

    # 2. Structural Patent Sections
    required_sections = [
        ("Abstract", r"(?:##\s*1\.\s*(?:ABSTRACT|ملخص)|ABSTRACT\s*\(ملخص)"),
        ("Prior Art / Background", r"(?:##\s*2\.\s*(?:BACKGROUND|الخلفية|خلفية)|PRIOR\s+ART|التقنيات\s+السابقة)"),
        ("Detailed Description", r"(?:##\s*3\.\s*(?:DETAILED|الوصف.*?التفصيلي)|DETAILED\s+TECHNICAL)"),
        ("Claims", r"(?:##\s*4\.\s*(?:CLAIMS|عناصر\s+الحماية)|CLAIMS\s*\(عناصر)"),
    ]
    for name, pattern in required_sections:
        if re.search(pattern, content, re.IGNORECASE):
            print_ok(f"Required structural section present: {name}")
        else:
            print_err(f"Missing required patent section: {name}")
            failures += 1

    # 3. Patent Claims Syntax Validation
    # Independent claim must use "comprising" or "يشتمل على / تشتمل على"
    independent_claim_en = re.search(r"Independent\s+(?:System\s+)?Claim\s+1.*?(?=Claim\s+2|\Z)", content, re.DOTALL | re.IGNORECASE)
    independent_claim_ar = re.search(r"(?:عنصر\s+الحماية\s+(?:المستقل\s+)?الأول|العنصر\s+المستقل\s+1).*?(?=عنصر\s+الحماية\s+(?:الثاني|2)|العنصر\s+2|\Z)", content, re.DOTALL | re.IGNORECASE)

    if independent_claim_en:
        claim_text = independent_claim_en.group(0)
        if "comprising" in claim_text.lower():
            print_ok("Independent Claim 1 contains the transitional phrase 'comprising'; legal validity is not assessed.")
        else:
            print_err("Independent Claim 1 is missing the transitional phrase 'comprising'.")
            failures += 1
    elif independent_claim_ar:
        claim_text = independent_claim_ar.group(0)
        ar_transitional = ["يشتمل على", "تشتمل على", "يتضمن", "تتضمن"]
        if any(term in claim_text for term in ar_transitional):
            print_ok("عنصر الحماية المستقل الأول يحتوي على الصيغة الانتقالية القانونية ('يشتمل على / تشتمل على').")
        else:
            print_err("عنصر الحماية المستقل الأول يفتقر للصيغة الانتقالية القانونية ('يشتمل على / تشتمل على').")
            failures += 1
    else:
        print_err("Missing Independent Claim 1 specification.")
        failures += 1

    # Check for dependent claims (English or Arabic)
    dependent_claims_en = re.findall(r"\*{0,2}Claim\s+[2-9]\d*.*?:", content, re.IGNORECASE)
    dependent_claims_ar = re.findall(r"\*{0,2}(?:عنصر\s+الحماية|العنصر)\s+(?:الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر|[2-9]\d*).*?:", content, re.IGNORECASE)
    total_dependent = len(dependent_claims_en) + len(dependent_claims_ar)

    if total_dependent >= 3:
        print_ok(f"Sufficient dependent claims detected ({total_dependent} dependent claims).")
    else:
        print_warn(f"Fewer than 3 dependent claims detected (found {total_dependent}). Recommended: ≥ 3.")
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
    table_pattern = r"\|.*?(?:Metric|المعيار|المؤشر).*?\|.*?(?:Baseline|خط\s*الأساس|الأنظمة\s*التقليدية|القيم\s*المرجعية).*?\|"
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
