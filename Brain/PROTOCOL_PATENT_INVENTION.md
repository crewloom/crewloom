# Protocol: sovereign-patent-invention
## Sovereign Patent Invention, Prior-Art Diligence & Statutory Filing Protocol

Type: **Protocol** (see [`ARTIFACT_TAXONOMY.md`](ARTIFACT_TAXONOMY.md)).  
Status: **active — mandatory** for any invention disclosure, provisional filing, or intellectual property triage.  
Acceptance Criteria Manual: [`PATENT_ACCEPTANCE_CRITERIA_AND_ACADEMIC_STANDARDS.md`](PATENT_ACCEPTANCE_CRITERIA_AND_ACADEMIC_STANDARDS.md)  

---

```
name:        sovereign-patent-invention
trigger:     any novel hardware/software mechanism proposed for intellectual property protection
             (demarcated from pure academic papers and permanent trade secrets)
steps:       Phase 0 (Track Triage: Patent vs Paper vs Trade Secret & Public-Repo Disclosure Lock) ->
             Phase 1 (Global Prior-Art Intelligence, Verified IDS Compliance & Distinct FTO Audit) ->
             Phase 2 (Dual-Jurisdiction Inventive Step: USPTO § 103 Graham + EPO Art. 56 COMVIK/G 1/19) ->
             Phase 3 (Verified Enablement & Truthful Reduction-to-Practice Audit under § 112(a)) ->
             Phase 4 (Claude Code Adversarial Mock Examination: Examiner vs Counsel vs Practitioner) ->
             Phase 5 (Authoritative Master Specification Drafting & Faithful Legal Translation) ->
             Phase 6 (Pre-Filing Foreign-Filing License, Human Inventorship Pannu Audit & Filing) ->
             Phase 7 (Official Provisional / PCT Priority Anchoring & Private Possession Hashing)
exit:        Authoritative Master Patent Dossier in private encrypted/local storage (.crewloom/private/),
             verified citations (37 CFR 1.56 IDS ready), passed structural checks, practitioner review,
             and official Patent Office filing receipt establishing statutory priority date.
on_failure:  Route unpatentable abstract algorithms (§ 101) to Academic Paper track; retain un-disclosed
             server/edge heuristics as confidential Trade Secrets. NEVER commit pre-filing specs to public repos.
enforced_by: core/scripts/verify_patent_protocol.py, registered patent practitioner review, human sign-off.
```

---

## 1. The Strategic Confidentiality & Novelty Preservation Rule
### (حظر الكشف العلني المسبق وقواعد الحفاظ على الجدة المطلقة)

> **CRITICAL STATUTORY WARNING (EPC Art. 54 vs 35 U.S.C. § 102):**  
> 1. **Zero Public Commits Prior to Official Filing:** Committing technical blueprints, concrete model parameters, or patent claims to a **public repository** (e.g., public `core/`) before an official patent filing constitutes an immediate **public disclosure**. Under the European Patent Convention (**EPO — zero grace period**), pre-filing public disclosure **permanently destroys novelty**. Under US law (35 U.S.C. § 102(b)(1)), it starts an irreversible 1-year grace period clock.  
> 2. **Git / SHA-256 Does NOT Grant Patent Priority:** Since the America Invents Act (**AIA — First-Inventor-to-File**), statutory priority dates are established **exclusively by an official Patent Office filing date** (e.g., USPTO Provisional Application under 35 U.S.C. § 111(b), or PCT International Filing). Git commits and SHA-256 hashes provide evidentiary documentation of conception/possession only (useful for internal provenance or limited prior-user defenses under § 273), **never** filing priority.  
> 3. **Mutual Exclusivity of Patent vs Trade Secret:** A specific technical feature cannot simultaneously be a permanent trade secret and a patented invention. Patents require **full enabling disclosure (35 U.S.C. § 112(a))** and become **public at 18 months** from earliest priority (35 U.S.C. § 122(b)). Before drafting, each subsystem MUST be assigned cleanly to one of the three tracks below.

```
┌────────────────────────────────────────────────────────────────────────┐
│               NEW TECHNICAL / SCIENTIFIC BREAKTHROUGH                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
         [ Phase 0: Pre-Publication Isolation (.crewloom/private/) ]
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│ TRACK A: PATENT   │     │ TRACK B: SECRET   │     │ TRACK C: ACADEMIC │
├───────────────────┤     ├───────────────────┤     ├───────────────────┤
│ • Machine-tied    │     │ • Non-reverse-    │     │ • Pure math,      │
│   technical means │     │   engineerable    │     │   observations,   │
│   solving § 101.  │     │   edge/local code.│     │   or benchmarks.  │
│ • Public enabling │     │ • Never published │     │ • Output: arXiv,  │
│   disclosure at   │     │   in patent specs │     │   IEEE, NeurIPS.  │
│   18 months.      │     │   or public repos.│     │ • Zero commercial │
│ • Official filing │     │ • Permanent UTSA  │     │   exclusivity.    │
│   before commits. │     │   protection.     │     │                   │
└───────────────────┘     └───────────────────┘     └───────────────────┘
```

---

## 2. Multidisciplinary Virtual Directorate & Practitioner Boundaries
Claude Code simulates a multi-perspective pre-examination engineering and IP readiness panel **strictly preparatory to mandatory review by a registered patent attorney/agent**:

1. **Legal Eligibility & Jurisdiction Analyst:** Evaluates US 35 U.S.C. § 101 (*Alice/Mayo* Steps 1, 2A Prongs 1–2, 2B *Berkheimer*, and 2024 USPTO AI Eligibility Guidance) alongside EPO Guidelines (**G-II 3.3 mathematical methods**, **COMVIK mixed-invention Art. 56 Problem-Solution Approach**, and **Enlarged Board G 1/19** simulation standards).
2. **Prior-Art Informatics Specialist:** Queries real patent registries and canonical academic literature without fabricating unverified citations, maintaining strict compliance with **Duty of Candor (37 CFR 1.56)** and Information Disclosure Statements (**IDS**). Distinquishes global novelty clearances from **Freedom-to-Operate (FTO)** active-claim clearance by jurisdiction and legal status.
3. **TRIZ & Systematic Engineering Analyst:** Formulates engineering contradictions ($P^+$ vs $P^-$) to assist US § 103 (*Graham*) secondary-consideration rationales (while noting the EPO applies COMVIK Objective Technical Problem analysis rather than TRIZ).
4. **Hardware Verification & Truthful Enablement Auditor:** Verifies that any claimed reduction-to-practice, benchmark, or physical instruction mapping strictly exists in tested production code (eliminating prophetic exaggeration that threatens § 112(a) enablement or candor under *Therasense*).
5. **Human Inventorship & Provenance Registrar:** Ensures compliance with **35 U.S.C. § 100(f)**, ***Thaler v. Vidal* (2022)**, and prevailing **USPTO Guidance on AI-Assisted Inventions** — verifying documented human conception via the ***Pannu* factors** and naming every human contributor accurately.
6. **Master Translator & Dossier Packager:** Enforces drafting ONE authoritative master filing specification first, followed by a faithful translation for PCT national phases (preventing added-matter rejections under **35 U.S.C. § 132 / EPC Art. 123(2)**).

---

## 3. Authoritative Prior-Art Search Repertoire & 37 CFR 1.56 Duty of Candor

### 3.1 Strict Prohibition on Unverified References
Under **37 CFR 1.56** and *Therasense, Inc. v. Becton, Dickinson & Co.*, submitting fabricated, guessed, or unverified patent publication numbers—or falsely misrepresenting prior art in an Information Disclosure Statement (IDS)—risks **inequitable conduct** and total unenforceability of the entire patent. Every cited patent/NPL document in the collision matrix **must be retrieved, read, and verified directly by exact document ID and publication date**.

### 3.2 Canonical Literature Corpus Discipline
Every patent draft must conduct deep academic & patent discovery across primary CPC/IPC domains (`G06N`, `G06F`, `H03M`, etc.), transparently citing and distinguishing verified foundational papers (`arXiv`, `IEEE`, `ACM`, `NeurIPS`, `ICLR`) as well as granted patents (`USPTO PPUBS`, `EPO Espacenet`, `WIPO PATENTSCOPE`, `Google Patents`). All candidate IDS citations are cataloged privately inside `.crewloom/private/research/`.

### 3.3 Distinct Search Types (Patentability vs Freedom-To-Operate)

| Search Type | Scope & Temporal Horizon | Legal Objective |
|---|---|---|
| **1. Novelty / Patentability Search (§ 102/103)** | Global public disclosures (patents, pending apps, arXiv, GitHub commits, IEEE/ACM) regardless of legal expiry. | Verify whether ANY prior reference (or obvious combination) discloses our claims. |
| **2. Freedom-To-Operate / FTO Clearance** | Active, **unexpired, in-force granted claims** strictly within target commercial jurisdictions (US, EP, etc.). | Verify whether commercializing our product infringes another party's enforceable claims. |

---

## 4. The 8 Operational Phases of the Protocol

### Phase 0: Pre-Publication Isolation & Triage Gate
1. Confirm all draft disclosures and architectural values reside inside **private local storage** (`.crewloom/private/`) — never public `core/` or open repos.
2. Assign every component cleanly to **Track A (Patent)**, **Track B (Permanent Trade Secret)**, or **Track C (Academic Paper)**.

### Phase 1: Verified Prior-Art Search, Collision Mapping & Duty of Candor Audit
1. Execute boolean/CPC queries across **Google Patents**, **USPTO PPUBS**, **EPO Espacenet**, **WIPO PATENTSCOPE**, **arXiv**, and **Semantic Scholar**.
2. Populate a verified collision matrix recording **only directly inspected citations** and log all discovered close references for mandatory **37 CFR 1.56 IDS disclosure**.

### Phase 2: Dual-Jurisdiction Legal Analysis (§ 101 / EPC Art. 52 & 56)
1. **USPTO Track (§ 101 & 2024 AI Update):**
   - **Step 1:** Statutory category (Process / Machine / Manufacture / Composition).
   - **Step 2A Prong 1:** Identify any mathematical/abstract judicial exception recited.
   - **Step 2A Prong 2:** Recite the **concrete technical structures and hardware mechanisms** integrating the math into a practical computer improvement (*Enfish*, *McRO*) — explicitly avoiding outcome-only functional claiming.
   - **Step 2B (*Berkheimer*):** If needed, supply concrete factual evidence of an unconventional inventive concept.
   - **§ 103 (*Graham*):** Document claimed nexus between any secondary considerations (unexpected technical results, failure of others) and the specific claim limitations.
2. **EPO Track (Problem-Solution Approach & COMVIK):**
   - Identify **Closest Prior Art (CPA)**; isolate distinguishing **technical features** producing a **credible technical effect** (Guidelines **G-II 3.3** & **G 1/19**); formulate the **Objective Technical Problem**; establish why PHOSITA *could not and would not* arrive at the solution without hindsight (**COMVIK Art. 56**).

### Phase 3: Truthful Enablement & Reduction-to-Practice Audit (§ 112(a)/(b))
1. **No Unimplemented Working-Example Claims:** Verify that any example claimed as built and measured actually executes the claimed mechanism in verified tests/hardware (no prophetic results presented as measured data).
2. **Definitional Precision (§ 112(b)):** Explicitly define any specialized or coined terminology in the initial specification. **Post-filing new matter (adding unseen equations during prosecution) is strictly prohibited under 35 U.S.C. § 132 and EPC Art. 123(2).**
3. **Dimensional & Numerical Consistency:** Audit every tensor shape, numerical dtype byte width, and memory formula independently for arithmetic consistency.

### Phase 4: Claude Code Adversarial Red-Team Simulation
Convene an adversarial simulated review (treating outputs strictly as pre-filing preparation, not legal counsel):
1. **Hostile USPTO/EPO Examiner:** Attacks under § 101 (*Alice* Step 2A/2B, AI Eligibility Updates), § 102 over verified closest literature/patents, § 112(b) indefiniteness, and EPO Art. 56 / COMVIK.
2. **Competitor FTO & Litigator:** Tests design-arounds, functional claiming traps (§ 112(f)), and inequitable-conduct vulnerabilities.
3. **Fortification Drafter:** Adds structural fallback dependent claims supported natively by the original specification disclosure.

### Phase 5: Single-Master Specification Drafting & Faithful Translation
1. Draft **ONE authoritative Master Specification** (e.g. `.en.md`) adhering strictly to:
   - Independent System Claim (`comprising`), Independent Method Claim, Independent CRM Claim.
   - Concrete structural recitations without exposing permanent Trade Secrets assigned to Track B.
2. Produce the Arabic counterpart (`.ar.md`) strictly as a **faithful technical-legal translation** of the authoritative master specification (100% classical Arabic without inline English), ensuring zero divergence for international/national-phase priority (EPC Art. 123(2)).

### Phase 6: Inventorship Provenance, Foreign Filing License & Deterministic Check
1. **Human Inventorship Audit (*Thaler v. Vidal* / Feb 2024 USPTO AI Guidance):**
   - Record concrete **conception provenance** proving human contribution under the ***Pannu* factors** for every named human inventor. AI tools cannot be listed as inventors. Every real human co-inventor who contributed to any claim MUST be included accurately.
2. **Foreign Filing License & Export Compliance:**
   - Clear national-security / foreign-filing license rules applicable to the inventors' jurisdictions and place of invention (e.g., **35 U.S.C. § 184** if applicable, or national IP office clearance) BEFORE transmitting filings abroad.
3. **Registered Patent Practitioner Review:** Mandatory sign-off by a licensed patent attorney/agent prior to submission.
4. **Structural Verification Guard:**
   ```bash
   python3 core/scripts/verify_patent_protocol.py --structure-only <PATH_TO_PRIVATE_SPECIFICATION>
   ```

### Phase 7: Official Provisional / PCT Priority Anchoring
1. File **USPTO Provisional Patent Application** (or national first filing) to obtain the **legally recognized priority date**.
2. Compute private SHA-256 archival digests strictly inside `.crewloom/private/` to prove filing integrity.
3. Track statutory post-filing calendars:
   - **12 Months:** Non-Provisional / PCT / Paris Convention foreign priority deadline.
   - **18 Months:** Mandatory international patent publication date.
   - **30 / 31 Months:** PCT National/Regional Phase entry deadlines (with faithful translations).

---

## 5. Unchecked Pre-Filing Readiness Checklist for Operators

```
[ ] Step 1: Confirm zero confidential specs or parameters exist in public repos (core/).
[ ] Step 2: Classify every feature: Track A (Patent) vs Track B (Trade Secret) vs Track C (Paper).
[ ] Step 3: Verify human conception records (*Pannu* factors) & list ALL human co-inventors.
[ ] Step 4: Retrieve and inspect REAL prior art across USPTO/EPO/WIPO/arXiv (log for 37 CFR 1.56 IDS).
[ ] Step 5: Verify factual working examples vs prophetic embodiments cleanly (§ 112(a) candor).
[ ] Step 6: Validate US (§ 101 Step 2A/2B, Graham) AND EPO (COMVIK, Art. 56, G 1/19) compliance.
[ ] Step 7: Draft single authoritative Master Specification (.en.md) with structured structural claims.
[ ] Step 8: Generate faithful legal translation (.ar.md) without divergent added matter.
[ ] Step 9: Run verify_patent_protocol.py --structure-only (0 structural failures).
[ ] Step 10: Obtain Foreign Filing License & Registered Patent Practitioner review before filing.
```
