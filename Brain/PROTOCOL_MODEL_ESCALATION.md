# Protocol: model-escalation

Type: Protocol (see [`ARTIFACT_TAXONOMY.md`](ARTIFACT_TAXONOMY.md)). Status: **written, not wired**: the pure functions exist in `contracts`, but no run path calls them yet.

```
name:        model-escalation
trigger:     a task is submitted for execution and more than one model could run it
steps:
  1. Build the ladder: eligible candidates ordered local, free, paid (`buildLadder`).
  2. Run the first rung (`selectModel`).
  3. Verify the result with a deterministic check first (tests, schema); a free model may judge only when no deterministic check exists.
  4. On a failed verification, a rate limit or a provider error, take the next untried rung (`escalate`).
  5. Escalate automatically, including to paid, without asking the operator.
  6. Record each attempt: model id, cost class, outcome, and for a paid rung the `paidBecause` list.
exit:        a verified result, or `escalate` returns `stop`
on_failure:  `escalation-limit` (more than 2 escalations) or `ladder-exhausted`: stop and report every attempt and its failure to the operator; never loop on the same rung
enforced_by: advisory until a Guard rejects a paid pick that has no `paidBecause` (planned)
owner:       this file; logic in agent/packages/crewloom/contracts/src/model-selection.ts
```

## Limits

- Ordering is by cost class only. Quality per task class needs the planned Eval; until then cheaper does not mean good enough, which is why step 3 gates every rung.
- The free list in `model-catalog.ts` is unverified against providers.
- The classifier, selector, verifier and escalator roles in `ARTIFACT_INDEX.md` are not implemented as agents. `selectModel` and `escalate` are the deterministic core of the selector and escalator.
