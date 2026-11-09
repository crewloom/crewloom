# Protocol: contradiction-adjudication

Type: Protocol (see [`ARTIFACT_TAXONOMY.md`](ARTIFACT_TAXONOMY.md)). Status: **written, advisory**: no Guard checks the decision record yet.

```
name:        contradiction-adjudication
trigger:     two or more claims, results, sources or model outputs contradict each other AND a decision, release note, benchmark claim or document depends on which one holds
steps:       1 state -> 2 classify -> 3 appraise -> 4 rivals -> 5 discriminate -> 6 decide and record
exit:        a decision record (template below) with one verdict per contradiction, each with evidence class, confidence and the test that would change it; or verdict `undecided` with the named missing test
on_failure:  no discriminating evidence reachable, or evidence of equal strength: verdict `undecided`, list the test and its cost, tell the operator. Never pick a side to close the task. After 2 failed attempts to obtain the same evidence, stop and report (AGENTS.md: max 2 retries per root cause).
enforced_by: advisory
owner:       this file
```

Scope: one contradiction at a time. A formal manuscript review is `crewloom-scientific-peer-review`; a multi-perspective opinion on a choice is `council`. This protocol is the narrow case where two statements cannot both be true and something rests on which one is.

## Steps

1. **State.** Write both claims in one line each with exact source and location. Ask whether they truly conflict: same subject, same unit, same conditions, same date, same definition. If the conflict disappears, the verdict is `not-a-contradiction` and the reconciling difference is recorded. Most apparent conflicts end here.
2. **Classify each claim** by evidence class: `measured` (raw data and config exist), `derived` (calculated from stated assumptions), `hypothesis`, `unsupported`. Model agreement, star counts, repetition and elegance are not evidence classes (see AGENTS.md "No fabrication").
3. **Appraise.** For each claim: who produced it, method, sample or denominator, confounders, bias, whether independent replication exists, whether the source supports the statement and not merely the topic. Unstable facts (versions, hardware specs, limits) are re-checked against a primary source with URL and retrieval date.
4. **Rivals.** List the explanations that would produce the observed conflict: one claim wrong, both right under different conditions, measurement or definition difference, stale data, shared upstream error. Give each rival a prediction that would be false if the rival were false.
5. **Discriminate.** Choose the cheapest test whose outcome differs between rivals, preferring a deterministic check (rerun, test, query, read the code) over a judgment. Run it and keep the raw result. A model may help design or read the test; a vote of models is not the test.
6. **Decide and record.** Pick the verdict from the closed set below, using the evidence strength and not the number of supporters. Write the record, then link it from the document, change log or `core/Brain/CHALLENGES.md` that depended on the answer.

### Verdicts (closed set)

`A-holds`, `B-holds`, `both-hold-under-conditions` (state the conditions), `neither-holds`, `not-a-contradiction`, `undecided`.

### Decision record

```
contradiction: <one line>
claims:        A = <claim, source:location, class>   B = <claim, source:location, class>
rivals:        <list, each with its prediction>
test:          <what was run, command or method, date, raw result location>
verdict:       <one of the closed set>
confidence:    supported under stated assumptions | needs experiment | contradicted by evidence
would change:  <the observation that flips this verdict>
tools used:    <skills, models and agents that actually ran, with failures; "none" if manual>
```

## Skills this protocol uses

Chosen by the intake stage of [`PROTOCOL_SKILL_VETTING.md`](PROTOCOL_SKILL_VETTING.md): the need was searched against `.agent/skills/`, `SKILLS_AND_TEAMS_CATALOG.md` and the existing scientific pack first. All seven candidate skills of the pack were already selected from a popularity-ranked discovery (`crewloom-scientific-peer-review/references/selection.md`: K-Dense scientific-agent-skills, 54,887 stars on 2026-10-27, pinned `5f2bc034…`), so no new third-party skill is needed. Popularity was a discovery signal only; fit is judged below.

| Step | Skill | Why it fits | Vetting state (read from `SKILL_VETTING_LOG.md`, `vet-skill.py`, `skill-pins.py`) |
|---|---|---|---|
| 1-3 | `scientific-critical-thinking` | evidence hierarchy, GRADE, bias, confounders, logical fallacies, replication (`references/evidence_hierarchy.md`, `common_biases.md`, `logical_fallacies.md`) | scan NO-KNOWN-PATTERN; pinned legacy, not approved |
| 4 | `hypothesis-generation` | rival explanations and discriminating predictions | scan REJECT (bytecode, `.env` named in notes); log: ACCEPT recommended, pending operator |
| 5 | `experimental-design`, `statistical-analysis` | design of the discriminating test; effect size and uncertainty | scan REVIEW; pinned legacy, not approved |
| 5 | `uncertainty-and-units` | only when the conflict is numeric (units, memory, latency) | scan REJECT (bytecode); log: ACCEPT recommended, pending operator |
| 1-6 | `crewloom-scientific-peer-review` | first-party; its step 6 ("reconcile by evidence strength and a discriminating test") is the general case this protocol expands | first-party, exempt |
| 6, opinion conflicts only | `council` | independent perspectives when the conflict is a choice, not a fact; use `--triad` or `--duo` | manual-only; `skill-pins.py check` currently fails on it (unreviewed edits after baseline) |

Rules for using them:

- Skills are knowledge, not authority. If one is unavailable or unvetted for the task at hand, the step is still done by hand from this file; do not install anything to proceed (AGENTS.md skills policy).
- Skills not listed (`literature-review`, `peer-review`) are not part of the default path: use `literature-review` only when step 3 needs a dated source search, and `peer-review` only when the contradiction is inside a manuscript.
- Record in `tools used` what actually ran. Sequential passes by one model are labeled as such and are not independent review.

## Limits

- Advisory: nothing yet rejects a missing decision record. A Guard (for example a CI check that a doc containing `contradiction:` has every field) is planned, not built.
- Verdicts are only as good as the cheapest test available; `undecided` is a valid and expected outcome.
- Six of the seven listed skills are unvetted or pending operator approval; this protocol does not approve them.
