# Protocol: strategic-decision

Type: **Protocol** (see [`ARTIFACT_TAXONOMY.md`](ARTIFACT_TAXONOMY.md)).
Status: **active — advisory**. Enforcement checkpoints are inline; a Guard is planned.

---

```
name:        strategic-decision
trigger:     any decision that affects strategy, architecture, product direction,
             resources, or partnerships — at organisation level
steps:       see Phase Map below
exit:        Decision Record signed by Owner and filed in decisions/
on_failure:  escalate to Owner; block the action; record the deadlock
enforced_by: advisory; mandatory council session per step 3; planned Guard
owner:       this file (core/Brain/PROTOCOL_STRATEGIC_DECISION.md)
```

---

## Phase Map — ordered, every step mandatory

```
TRIGGER
  │
  ▼
[PHASE 0] Define the Question
  │
  ▼
[PHASE 1] Collect Data & Context
  │
  ▼
[PHASE 2] Map Stakeholders
  │
  ▼
[PHASE 3] Council Session  ← /council --triad decision
  │
  ▼
[PHASE 4] Evaluate Alternatives
  │
  ▼
[PHASE 5] Risk Assessment
  │
  ▼
[PHASE 6] Verdict & Approval
  │
  ▼
[PHASE 7] Decision Record
  │
  ▼
[PHASE 8] Post-Decision Review (scheduled)
```

---

## Phase 0 — Define the Question

**Goal:** one crisp question the decision must answer.

| Field | Instruction |
|---|---|
| `question` | One sentence. Starts with "Should we…", "Which…", or "How should we…". |
| `decision_type` | `strategic` / `technical` / `product` / `financial` / `operational` / `people` |
| `deadline` | ISO 8601 date — when the decision must be made |
| `reversibility` | `reversible` (can undo in < 30 days) or `irreversible` |
| `urgency` | `critical` / `high` / `medium` / `low` |

> [!IMPORTANT]
> If the question cannot be written in one sentence, the problem is not yet defined. Stop here and reframe.

**Exit check:** question field is non-empty and unambiguous. Owner confirms before Phase 1.

---

## Phase 1 — Collect Data & Context

Gather all available evidence **before** forming an opinion.

### 1.1 — Quantitative data
- Metrics, OKR progress, revenue, costs, usage numbers
- Benchmarks, test results, CI status
- Market data, competitor signals

### 1.2 — Qualitative data
- User feedback, NPS, support tickets
- Team sentiment, known blockers
- Prior Decision Records touching the same domain

### 1.3 — Constraints
- Budget ceiling
- Timeline hard stops
- Technical dependencies (from `ARCHITECTURE.md`)
- Regulatory or legal constraints

**Exit check:** a data summary with explicit gaps noted exists. Gaps that cannot be filled before the deadline are flagged as `unknown — decision proceeds with acknowledged gap`.

---

## Phase 2 — Map Stakeholders

Who is affected by or can block this decision.

| Role | Who | Weight | Must approve? |
|---|---|---|---|
| **Owner** | Mohamed Ashraf | Sovereign | Yes |
| **Domain lead** | person owning the affected area | High | Yes if domain is primary |
| **Implementor** | who will execute | Medium | Consulted |
| **User** | end customer | Medium | Informed |
| **Affected team** | anyone whose work changes | Low | Informed |

> [!NOTE]
> Any stakeholder who is a **blocker** (can stop execution) must be consulted before Phase 6.

**Exit check:** Stakeholder table is complete. All blockers are identified.

---

## Phase 3 — Council Session

**Mandatory for every strategic decision.** The council is the structured deliberation engine.

### Automatic triad selection

The `decision` triad is the default for strategic decisions:
```
/council --triad decision <the question from Phase 0>
```

**`decision` triad:** Kahneman + Munger + Aurelius
- **Kahneman**: detects cognitive biases and System 1 traps in the framing
- **Munger**: multi-model inversion — what guarantees failure?
- **Aurelius**: moral clarity and resilience — what must hold regardless of outcome

### Override rules

| Condition | Triad to use |
|---|---|
| Technical / architecture choice | `architecture` (Aristotle + Ada + Feynman) |
| Market entry / competitive move | `strategy` (Sun Tzu + Machiavelli + Aurelius) |
| Financial / economic trade-off | `economics` (Munger + Machiavelli + Sun Tzu) |
| People / team / HR | `conflict` (Socrates + Machiavelli + Aurelius) |
| AI / product direction | `ai-product` (Karpathy + Torvalds + Machiavelli) |
| Existential risk | `/council --full` (all 19 members) |

### Council output required fields

The session must produce:
1. **Unresolved Questions** — what the council does not know
2. **Vote Tally** — weighted stances (from STEP 6 of council protocol)
3. **Minority Report** — any `DEALBREAKER: yes` position, even if outvoted
4. **Council Verdict** — the synthesized recommendation

> [!CAUTION]
> The Council Verdict is **input** to Phase 4, not the final decision. The Owner decides; the council advises.

**Exit check:** Council verdict file saved. Minority Report reviewed by Owner.

---

## Phase 4 — Evaluate Alternatives

Compare every viable option — including "do nothing".

### Evaluation Matrix

For each alternative, score 1–5 on each dimension:

| Dimension | Weight | Description |
|---|---|---|
| **Strategic alignment** (OKRs) | 30% | Does it move us toward our stated goals? |
| **Technical feasibility** | 20% | Can we build/execute this with current resources? |
| **Financial impact** (ROI) | 20% | Net value: revenue gain + cost saved − cost to implement |
| **User / customer impact** | 15% | NPS delta, friction, trust |
| **Operational complexity** | 10% | Dependencies, coordination cost, maintenance burden |
| **Team impact** | 5% | Morale, learning, attrition risk |

**Weighted score = Σ (dimension score × weight)**

### Decision Table

| Alternative | Strategic | Technical | Financial | User | Ops | Team | **Total** | Council stance |
|---|---|---|---|---|---|---|---|---|
| Option A | | | | | | | | |
| Option B | | | | | | | | |
| Do nothing | | | | | | | | |

**Exit check:** At least two alternatives evaluated. Do-nothing always present. Council stances recorded.

---

## Phase 5 — Risk Assessment

For the leading alternative from Phase 4:

### Risk Register

| Risk | Probability | Impact | Severity | Mitigation | Owner |
|---|---|---|---|---|---|
| | `high/med/low` | `high/med/low` | `P × I` | | |

### Tail Risk Check (Taleb lens)

> "What is the worst-case outcome if this decision is wrong? Can the organisation survive it?"

- **Reversibility check:** if `irreversible`, minimum council must have been `--triad decision` or higher
- **Antifragility check:** does the decision gain from volatility or break under it?
- **Concentration check:** does it create a single point of failure?

**Exit check:** Severity column complete. Any `high × high` risk has an explicit mitigation and an owner.

---

## Phase 6 — Verdict & Approval

### Approval thresholds

| Decision type | Approval required |
|---|---|
| `reversible` + `low/medium` urgency | Domain lead + Owner notification |
| `reversible` + `critical` urgency | Owner explicit sign-off |
| `irreversible` + any urgency | **Owner sovereign sign-off** (no delegation) |
| Cross-domain (≥ 2 domain leads) | All domain leads + Owner |
| Financial > threshold | Owner + financial review |

### Sign-off record

```yaml
decision:    <one-line summary of what was decided>
chosen:      <option label>
decided_by:  <name and role>
date:        <ISO 8601>
confidence:  high | medium | low
rationale:   <why this option over the alternatives — 2-5 sentences>
council_ref: <path to council verdict file, or "no council — below threshold">
```

> [!WARNING]
> Any `irreversible` decision taken without Owner sovereign sign-off is **invalid** and must be halted.

**Exit check:** Sign-off YAML complete. For `irreversible` decisions, Owner has confirmed in writing (message, commit, or file).

---

## Phase 7 — Decision Record

File the decision for institutional memory and future auditing.

### File location and naming

```
decisions/
  YYYY-MM-DD--<kebab-case-title>.md
```

### Record template

```markdown
# Decision: <title>

**Date:** YYYY-MM-DD
**Status:** decided | superseded by [link] | reversed on YYYY-MM-DD
**Type:** strategic | technical | product | financial | operational | people
**Reversibility:** reversible | irreversible
**Decided by:** <name>

## Question
<Phase 0 question>

## Context
<Phase 1 data summary — key facts and acknowledged gaps>

## Alternatives considered
<Phase 4 table — condensed>

## Council input
<Council verdict summary + link to full session>
<Minority report summary, if any>

## Risks accepted
<Phase 5 high-severity risks and their mitigations>

## Decision
<Phase 6 sign-off YAML>

## Review date
<ISO 8601 — when Phase 8 is due>

## Outcome (filled at Phase 8)
_Pending review._
```

**Exit check:** File exists at the correct path. `decisions/` directory committed and pushed.

---

## Phase 8 — Post-Decision Review

**Scheduled at filing time (Phase 7).** The review date is set in the Decision Record.

### Timing guidelines

| Reversibility | Urgency | Review window |
|---|---|---|
| `reversible` | any | 30 days after implementation |
| `irreversible` | `low/medium` | 90 days after implementation |
| `irreversible` | `high/critical` | 14 days after implementation — first signal check |

### Review checklist

- [ ] Was the question in Phase 0 the right question?
- [ ] Were the data gaps in Phase 1 material to the outcome?
- [ ] Did any risk in Phase 5 materialise? If so, did the mitigation hold?
- [ ] Did the actual outcome match the confidence level in Phase 6?
- [ ] Should this decision be reversed, adjusted, or confirmed?

### Outcome codes

| Code | Meaning |
|---|---|
| `confirmed` | Decision stands; outcome matches or exceeds expectation |
| `adjusted` | Decision remains but parameters changed; update the record |
| `reversed` | Decision undone; link the reversal decision record |
| `inconclusive` | Too early or insufficient data; reschedule review |

Update the Decision Record's `Outcome` section with the code and a brief explanation.

**Exit check (Protocol complete):** Decision Record updated with outcome code. If `reversed`, a new decision record is filed.

---

## on_failure — what happens when a step stalls or fails

| Failure condition | Response |
|---|---|
| Phase 0: question cannot be defined | Convene a /council --duo --members socrates,watts to reframe |
| Phase 1: critical data gap, deadline imminent | Proceed with explicit `unknown — acknowledged gap` flag; escalate to Owner |
| Phase 3: Council quorum not reachable (all providers fail) | Use `--quick` mode minimum; if that fails, Owner decides solo with an explicit "no-council" flag in Phase 6 sign-off |
| Phase 6: stakeholder blocker refuses to unblock | Escalate to Owner for sovereign override; document the refusal |
| Phase 7: `decisions/` directory missing | Create it; file is mandatory before execution begins |
| Phase 8: review not done within review window | Flag as `overdue` in the Decision Record; Owner is notified |

---

## Limits (what this Protocol does NOT do)

- It does not replace the Owner's judgment — the Owner is sovereign at every phase.
- It does not verify that the chosen option was executed correctly (that is a release or delivery protocol).
- Advisory enforcement means a motivated agent can skip steps; a Guard is planned.
- The evaluation matrix scores are estimates; they are not measurements.
- Phase 8 outcome codes are self-reported; no automated tracking exists yet.

---

## Integration with other Protocols

| Protocol | Relationship |
|---|---|
| `council` skill | Mandatory at Phase 3 |
| `release` protocol | Triggered after Phase 7 when the decision involves a code change |
| `model-escalation` protocol | Governs which model runs the council if auto-routing fails |
| `contradiction-adjudication` protocol | Triggered if council output contradicts prior Decision Records |
| `skill-vetting` protocol | Triggered if the decision involves adopting a new skill or agent |
