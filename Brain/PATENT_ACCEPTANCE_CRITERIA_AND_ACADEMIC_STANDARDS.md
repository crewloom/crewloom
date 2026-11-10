# Comprehensive Academic, Technical & Legal Acceptance Criteria for Sovereign Patent Inventions
## دليل معايير القبول الأكاديمية والتقنية والقانونية الشاملة لبراءات الاختراع والسيادة المعرفية

> **Authoritative Technical Standard & Statutory Manual**  
> **Constitutional Authority:** Crewloom Sovereign Systems & The Owner  
> **Governing Protocol:** [`PROTOCOL_PATENT_INVENTION.md`](PROTOCOL_PATENT_INVENTION.md)  
> **Applicability:** Mandatory pre-filing readiness manual prior to registered patent practitioner review.

---

## 1. Executive Summary: The Four Statutory Pillars
Every technical breakthrough proposed for patent protection must pass a rigorous four-pillar gate before any legal filing or claim drafting is permitted:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      THE FOUR STATUTORY PATENTABILITY PILLARS                          │
├────────────────────────────┬────────────────────────────┬──────────────────────────────┤
│ 1. Statutory Subject       │ 35 U.S.C. § 101            │ Alice/Mayo 2-Step Framework: │
│    Matter Eligibility      │                            │ Technical Transformation     │
├────────────────────────────┼────────────────────────────┼──────────────────────────────┤
│ 2. Absolute Novelty &      │ 35 U.S.C. § 102            │ Single Reference Rule: Zero  │
│    Prior-Art Clearance     │ (MPEP 2131)                │ Anticipation in Worldwide DBs│
├────────────────────────────┼────────────────────────────┼──────────────────────────────┤
│ 3. Non-Obviousness &       │ 35 U.S.C. § 103            │ Graham Framework & TRIZ:     │
│    Inventive Step          │ (MPEP 2141 / EPC Art. 56)  │ Engineering Contradiction    │
├────────────────────────────┼────────────────────────────┼──────────────────────────────┤
│ 4. Full Enablement &       │ 35 U.S.C. § 112            │ The 8 Wands Factors &        │
│    Definiteness            │ (MPEP 2164 & 2173)         │ Mathematical Reproducibility │
└────────────────────────────┴────────────────────────────┴──────────────────────────────┘
```

---

## 2. Pillar 1: Subject Matter Eligibility (35 U.S.C. § 101 & Alice/Mayo Framework)
### المعيار الأول: أهلية الاختراع والتحول التقني الملموس في الحاسوب

Under international patent jurisprudence (USPTO 2019 Revised Patent Subject Matter Eligibility Guidance, EPO Guidelines for Examination G-II 3.6, and WIPO standards), pure software algorithms, mathematical formulas, and mental processes are rejected as non-statutory judicial exceptions. 

To establish **subject-matter eligibility under § 101**, the disclosure must satisfy the Alice/Mayo framework:

```
                                    ALICE / MAYO TEST FOR AI & ALGORITHMS
                                                      │
                       [ Step 1: Statutory Category? (Machine, Process, Manufacture) ]
                                                      │ YES
                                                      ▼
                           [ Step 2A, Prong 1: Recites Judicial Exception? ]
                           (Mathematical concept, abstract mental process, law of nature)
                                                      │ YES
                                                      ▼
                       [ Step 2A, Prong 2: Integrated into a Practical Application? ]
                       ─────────────────────────────────────────────────────────────
                       • Does it improve computer functioning or physical hardware?
                       • Does it eliminate physical bottlenecks (e.g. KV-cache OOM)?
                       • Does it avoid generic computer execution ("apply it")?
                                      │                               │
                                      │ NO                            │ YES ──> [ PASS: Eligible under § 101 ]
                                      ▼                               
                       [ Step 2B: Contains an Inventive Concept? ]
                       ("Significantly more" than the exception itself)
                                      │
                       ┌──────────────┴──────────────┐
                       ▼                             ▼
                 [ YES: Eligible ]            [ NO: REJECTED ]
```

### § 101 Acceptance Invariants:
1. **Specific Technical Improvement (Step 2A Prong 2 & Step 2B):** Claims must recite the **specific hardware structures, memory data structures, or signal transformations** that solve physical computational bottlenecks—not merely the desired result or outcome (*Alice* Step 2A Prong 2; **2024 USPTO AI Subject Matter Eligibility Update**).
2. **Machine-Tied Hardware Execution:** Concrete embodiments should anchor algorithms into real physical memory tiers, SIMD vector arithmetic, or verified neuromorphic accelerators, avoiding abstract "computer program per se" traps.
3. **Truthful Reduction to Practice:** Do not describe speculative or prophetic architectural benchmarks as measured hardware results; distinguish verified running prototypes from prophetic implementations strictly in accordance with **37 CFR 1.56 Duty of Candor**.

---

## 3. Pillar 2: Absolute Novelty, Verified Prior-Art Clearance & IDS Duty (35 U.S.C. § 102 & 37 CFR 1.56)
### المعيار الثاني: الجدة المطلقة، واجب النزاهة العلمية (IDS)، والمسح المهني الموثق

Under the **Single Reference Rule (MPEP 2131)**, an invention lacks novelty if any single public reference discloses, expressly or inherently, every element of the claimed invention. Under **37 CFR 1.56** (*Therasense*), inventors and practitioners have an affirmative **Duty of Candor** to disclose all known material prior art accurately and NEVER submit fabricated or unverified publication IDs.

### 3.1 Distinct Search Workflows: Patentability vs Freedom-To-Operate (FTO)
- **Patentability Search (§ 102 / § 103):** Searches all global public literature (expired patents, pending apps, arXiv preprints, open-source repositories) regardless of enforceability.
- **Freedom-To-Operate (FTO):** Searches **active, unexpired, granted patent claims** strictly within target commercial jurisdictions.

### 3.2 Professional Search Interfaces & Canonical Real Prior-Art Corpus

| Registry / Repository | Focus Coverage | Search Strategy |
|---|---|---|
| **Google Patents** | Global patent families & NPL matching | Combined CPC groups + technical mechanism boolean queries |
| **USPTO PPUBS** | Official US granted patents & applications | `.ti,ab,clm.` fielded proximity queries (`WITH` / `SAME`) |
| **EPO Espacenet** | 140M+ worldwide patents & INPADOC citations | CQL CPC filtering + backward/forward citation crawling |
| **WIPO PATENTSCOPE** | PCT international filings & national entries | Multi-lingual IPC queries & PCT Chapter I/II reports |

**Example Verified Prior-Art Baseline Matrix Format (Never Use Unverified IDs):**

```markdown
| Verified Prior-Art Citation | Technical Focus | Overlapping Features | Documented Inventive Delta (For IDS / Prosecution) | Verification Status |
|---|---|---|---|---|
| **[Exact Verified Patent / DOI #1]** | [Published Architecture] | [Shared functional elements] | [Specific structural/hardware differences confirmed by reading full text] | **Verified Direct Read** |
| **[Exact Verified arXiv / IEEE Paper #2]** | [Academic Baseline] | [Shared theoretical domain] | [Concrete machine-implemented improvement avoiding prior limitations] | **Verified Direct Read** |
```

---

## 4. Pillar 3: Dual-Jurisdiction Inventive Step (USPTO § 103 Graham vs EPO Art. 56 COMVIK)
### المعيار الثالث: الخطوة الابتكارية وعدم البداهة وفق المعايير الأمريكية والأوروبية

### 4.1 US Standard: Graham v. John Deere (35 U.S.C. § 103 / MPEP 2141)
Requires documented factual inquiries: (1) scope and content of prior art; (2) differences between prior art and claims; (3) level of ordinary skill (**PHOSITA**); and (4) objective secondary considerations (commercial success, long-felt unsolved need, unexpected technical results) possessing an explicit **nexus to the claimed structural features**. Systematic TRIZ contradiction analysis ($P^+$ vs $P^-$) aids internal engineering articulation of these differences.

### 4.2 European Standard: EPO Problem-Solution Approach, COMVIK & G 1/19 (EPC Art. 56)
The EPO evaluates software/AI inventions under **mixed-invention COMVIK guidelines** and **G 1/19** (Guidelines **G-II 3.3** mathematical methods):
1. Identify the **Closest Prior Art (CPA)**.
2. Distinguish non-technical mathematical rules from features contributing to a **technical effect** in a real computing machine.
3. Formulate the **Objective Technical Problem** solved by the technical features.
4. Establish that PHOSITA *would not* (not merely *could not*) arrive at the claimed technical features without hindsight.

---

## 5. Pillar 4: Enablement, Definiteness, No New Matter & Human Inventorship
### المعيار الرابع: كفاية الإفصاح، حظر الإضافات اللاحقة، وإثبات المخترع البشري

### 5.1 Enablement (The 8 Wands Factors — MPEP 2164.01(a)) & § 112(b) Definiteness
To prevent "undue experimentation", all 8 Wands factors must be satisfied in the **original filed specification**.
- **Strict Prohibition on New Matter (35 U.S.C. § 132 / EPC Art. 123(2)):** You CANNOT introduce new mathematical definitions, coined terminology explanations, or unfiled embodiment equations during prosecution after the priority date is locked.
- **Truthful Experimental Boundaries:** Only report empirical measurements generated by verified execution of the claimed mechanism; never mischaracterize mocked telemetry or separate baseline outputs as claimed proof.

### 5.2 Legal Inventorship & AI-Assisted Inventions (35 U.S.C. § 100(f) / *Thaler v. Vidal*)
Under federal law (*Thaler v. Vidal*, 2022) and prevailing **USPTO Guidance on AI-Assisted Inventions**:
- **AI Cannot Be Named Inventor:** AI systems, coding assistants, and generative models are tools, not legal inventors.
- **Pannu Factors & Conception Logs:** Every named human inventor MUST possess documented proof of significant human contribution to the conception of at least one claim, and every human co-inventor must be listed truthfully.

### 5.3 Legal Claim Grammar & Single-Master Translation Mandate
1. **Independent Claims:** Recite statutory system, method, and CRM forms with open transitional phrases (`"comprising"`), anchoring technical limitations structurally without functional means-plus-function gaps (§ 112(f)).
2. **Authoritative Master + Faithful Translation:** Author ONE primary master specification first; generate foreign-language equivalents strictly as **faithful technical-legal translations** (never divergent independent rewrites) to avoid added-matter fatal defects upon PCT National/Regional Phase entry.

---

## 6. The Multi-Track Demarcation Matrix: Paper vs. Patent vs. Secret
### مصفوفة الفرز والتحكيم: متى نودع براءة اختراع، ومتى ننشر ورقة بحثية؟

```
                                  INVENTION TRIAGE MATRIX
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ DECISION FLOWCHART:                                                                    │
│                                                                                        │
│ 1. Does it improve physical machine functioning or solve a hardware contradiction?     │
│    ├── NO  ──> Can it be reverse-engineered from public outputs?                      │
│    │           ├── YES ──> ROUTE TO: Academic Research Paper (arXiv / IEEE)           │
│    │           └── NO  ──> ROUTE TO: Trade Secret (Protected Sovereign Vault)          │
│    └── YES ──> Does it pass the Alice/Mayo § 101 Technical Transformation Test?         │
│                ├── NO  ──> ROUTE TO: Academic Research Paper with Formal Benchmark     │
│                └── YES ──> Is there prior art anticipating any single claim?           │
│                            ├── YES ──> Reformulate Inventive Delta or Publish Paper   │
│                            └── NO  ──> ROUTE TO: Sovereign Patent Filing Protocol     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

| Decision Attribute | Track 1: Sovereign Patent Filing | Track 2: Frontier Academic Paper | Track 3: Sovereign Trade Secret | Track 4: Defensive Publication |
|---|---|---|---|---|
| **Primary Goal** | 20-year legal monopoly & sovereign asset valuation. | Scientific impact, peer recognition, and citations. | Permanent protection against copying without public disclosure. | Preventing competitors from patenting common art. |
| **Target Venue** | USPTO, EPO, WIPO (PCT), Arab Patent Offices. | arXiv.org, IEEE Xplore, NeurIPS, ICML, ICLR. | Air-gapped Sovereign Brain Vault. | IP.com, Research Disclosure, public blog. |
| **Legal Protection** | Strong exclusive right to exclude others. | Zero legal protection; public domain. | Protection under Uniform Trade Secrets Act (UTSA). | Defensive prior art shield only. |
| **Language Format** | Dual-Language: Pure English (`.en.md`) & Pure Arabic (`.ar.md`). | Pure Academic English (`.tex` / `.pdf`). | Encrypted source code / binary weights. | Concise technical disclosure. |
| **Cost & Timeline** | Filing fees, examination, 18-month publication. | $0.00 cost, immediate publication. | $0.00 cost, permanent until leaked. | $0.00 cost, immediate prior art status. |

---

## 7. The 100-Point Deterministic Patent Readiness Rubric
### مقياس جاهزية براءة الاختراع المئوي (Rubric)

Before any patent specification is submitted to a registered patent practitioner for filing, Claude Code and human technical reviewers assess readiness against this 100-point rubric. **Minimum internal readiness threshold: 85/100, with ZERO fatal deductions.**

| Category | Maximum Points | Verification Criteria & Evidence | Fatal Deduction Triggers (Score = 0) |
|---|:---:|---|---|
| **1. Statutory Eligibility (§ 101 / Art. 52)** | **20** | Specific machine/hardware technical means explicitly recited; passes Alice Step 2A/2B & EPO technical-effect rules. | Claims pure mathematical formula or generic outcome without hardware/technical transformation. |
| **2. Verified Prior-Art Clearance (§ 102 / IDS)** | **25** | Directly inspected prior art across Google Patents, PPUBS, Espacenet, PATENTSCOPE, and arXiv; accurate Collision Table for 37 CFR 1.56 IDS. | Unverified/fabricated citations or a single reference anticipating all elements of Claim 1. |
| **3. Dual-Jurisdiction Inventive Step (§ 103 / Art. 56)** | **20** | Objective technical problem / TRIZ contradiction documented alongside claimed structural nexus. | Obvious combination of standard prior art under *Graham* or EPO *COMVIK*. |
| **4. Enablement, Candor & Truthful Proofs (§ 112)** | **25** | All 8 Wands factors satisfied; zero new-matter reliance; only actually executed benchmarks reported as measured results. | Undue experimentation required, prophetic results disguised as live data, or ambiguous undefined terms. |
| **5. Human Inventorship & Legal Claim Structure** | **10** | Documented human conception provenance (*Pannu* factors) naming ALL human co-inventors truthfully; open `"comprising"` transition; single-master faithful translation. | Deliberate omission of a human co-inventor, naming an AI as inventor, or divergent multi-language specs. |
| **TOTAL** | **100** | **Readiness Threshold: $\ge 85 / 100$** | Any fatal trigger blocks practitioner submission until resolved. |

---

## 8. Operational Integration Mandate
Whenever preparing a draft filing under `core/Brain/PROTOCOL_PATENT_INVENTION.md`:
1. Store confidential pre-filing disclosures strictly inside private storage (`.crewloom/private/`), never in public `core/`.
2. Execute the deterministic structure guard:
   ```bash
   python3 core/scripts/verify_patent_protocol.py --structure-only <PATH_TO_PRIVATE_SPECIFICATION>
   ```
3. Generate the complete Readiness Scorecard and submit to a registered patent attorney/agent before any public commit.
