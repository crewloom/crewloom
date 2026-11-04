# Scientific manuscript verification

`python3 scripts/verify_patent_protocol.py <document>` is the publication gate. It fails closed with exit code 2: citation resolution, claim-to-evidence review, and frozen benchmark verification are currently unavailable. No manuscript can receive scientific, legal, or publication approval from this script.

Use `python3 scripts/verify_patent_protocol.py <document> --structure-only` for a drafting check. Exit 0 means only that expected text, headings, notation, and table headings were found. It does not establish ownership, patent eligibility, mathematical correctness, real measurements, valid citations, or scientific compliance. Invalid structure returns a nonzero status in either mode. Existing callers retain the same path and one-document argument; they now fail closed instead of receiving false certification.

The scientific-discovery-and-patent protocol remains blocked pending independent evidence review and an implemented evidence verification workflow. A future implementation must verify provenance and the manuscript's actual claims against reviewable evidence; user-written status booleans or a syntactically valid manifest are not proof. No network lookup or purported DOI validation is performed here.

Regression checks: `python3 -m unittest discover -s scripts -p test_patent_protocol_gate.py -q`.

The defect arose because a structural regex checklist was treated as evidence validation, its success message claimed full compliance, and the protocol used exit 0 as publication approval. Tests now preserve the boundary between these two operations.

[العربية](SCIENTIFIC_VERIFICATION.ar.md)
