# Design: opt-in selection measurement (shadow log)

Status: **proposed, no code written**. Date: 2026-10-31. Owner of the decision data: the usage ledger (`agent/apps/crewloom-desktop/src/lib/usage-ledger.ts`). Related: [`PROTOCOL_MODEL_ESCALATION.md`](PROTOCOL_MODEL_ESCALATION.md), `pulse/docs/TRAINING_REPORT.md`, `pulse/docs/DATA_PLAN.md`.

## 1. The question this answers

> For each task class, how often does the cheapest eligible model fail verification on its first attempt?

A trained router (Pulse) only pays off where that rate is high enough to justify skipping the cheap attempt. If it is low everywhere, the deterministic selector (`model-selection.ts`) is enough and no training is justified. This is the falsifiable condition for the whole training effort. It also produces outcome labels (verification pass or fail) that are independent of any teacher model, which removes the teacher-circularity risk in `distill_with_beam.mjs`.

## 2. Facts that shape the design (read from source, not run)

| Fact | Location | Consequence |
|---|---|---|
| A ledger already records one event per request: model, route, outcome, duration, tokens, cost | `usage-ledger.ts`, `usage-tracker.ts:recordUsage` | Extend it. A second log would break "one owner per concern". |
| `route` is derived from the provider (`crewloom-pulse`, local CLI, else `frontier`), not from a selection decision | `usage-tracker.ts:160` | The ledger cannot yet say which rung ran or why. |
| `retryOf` is always `null` and `holdout` always `false` | `usage-tracker.ts:171-173` | Retry attribution and calibration runs exist in the type but are never produced. |
| Recording errors are swallowed by an empty `catch` | `usage-tracker.ts:191` | Violates the no-silent-failure rule; a broken log would look like an empty log. |
| Settings `smartRouting`, `localFirstPriority`, `pulseAutoOrchestration`, `pulseSupervisionMode`, `adaptiveTemperature` appear only in `types.ts` and `IntelligenceTab.tsx`; no other source reads them | grep of `src/` | Toggles with no consumer, forbidden by `AGENTS.md`. Fix or relabel before adding another. |
| `selectModel` and `escalate` have no caller | `contracts/src/model-selection.ts` | Nothing produces a ladder decision to log yet. |
| No verifier runs anywhere today. `contracts/src/deep-execution.ts` defines `VerifierKind` (`typecheck`, `test`, `build`, `lint`, `schema`) and `depth.ts` names `typecheck` and `test` in its policy, but no runner exists (`DEEP-SKILLS-SPEC.ar.md` status line says so) and `resolveDepth` has no caller. The Rust `orchestrator.rs` "Verify" phase is a descriptive step (title and description text; the file contains no `Command::new`) | grep of `src/` and `src-tauri/src/` | `verification` would be `none` for every event; the measurement cannot start. |
| The only outcomes the ledger has are `ok`, `fail`, `stopped`, `unknown`, derived from the provider stream status | `usage-tracker.ts:162` | They record transport success, not answer quality; they must not be used as labels. |
| Held-out accuracy of the current heuristic: mode 71.4%, role top-1 33.3% (labels unreviewed); no Qwen weights exist | `TRAINING_REPORT.md` | The shadow log must not depend on Pulse being accurate. |

## 3. Artifacts and types

| Artifact | Type | Home |
|---|---|---|
| `SelectionTrace` (fields in §4) | Contract | `contracts`, optional field on `LedgerEvent` |
| Setting `selectionMeasurement` (`off` default, `passive`, `probe`) | Rule plus setting | `Settings` in `types.ts`; consumer is the recorder, so it is not a dead toggle |
| Recorder | Guard-style adapter | `src/lib/` pure function; persistence only through `lib/storage.ts` |
| Measurement procedure and decision rule | Protocol | this document until §9 stage 2, then its own file |
| First-rung failure rate and CI per task class | Eval | script reading ledger events |

## 4. `SelectionTrace` (optional on `LedgerEvent`)

```
taskClass:    'chat' | 'plan' | 'build' | 'unclassified'   // from deterministic features, never from a model
features:     { language: 'ar'|'en'|'mixed', lengthBucket, hasCode, hasPath }   // no raw text
ladder:       string[]                                        // model ids in cost order
rung:         number                                          // index of the model that actually ran
costClass:    'local' | 'free' | 'paid'
decision:     'live' | 'shadow'                               // shadow = what the selector would have picked
shadowPick:   string | null
verification: 'pass' | 'fail' | 'none'                        // 'none' when no deterministic check exists
verifier:     'tests' | 'schema' | 'other' | null
escalatedFrom: string | null                                  // event id; fills the existing retryOf
```

Missing `SelectionTrace` means the event predates the feature or the setting was off. `formulaVersion` is bumped only when a rollup formula changes, not for this optional field.

## 5. Modes

- **off (default):** nothing changes, nothing is recorded beyond today's ledger.
- **passive:** the selector runs alongside the real choice and its pick is logged as `shadowPick`. The real behavior is untouched. Limit: when a paid model actually ran, the outcome of the cheaper rung is unknown, so passive mode cannot measure the counterfactual by itself.
- **probe:** for a sampled fraction of tasks that have a deterministic verifier, the cheapest **free or local** rung is also run in the background and verified. Only free and local models may be probed, so a probe never spends money. Probe runs are `holdout: true` (the existing field) and their result is never shown as the answer. Paid models are never probed.

## 6. Decision rule, fixed before any data

For each `taskClass`, among events with `verification` of `pass` or `fail` only:

- `r` = first-rung failure rate with a Wilson 95% interval; denominators always reported; `none` events are counted and shown but excluded from `r`.
- A router is worth building for a class only if the **lower** bound of the saving estimated from `r` exceeds the router's own cost (latency of the routing stage plus misroute penalty). The cost model and the threshold are written down and frozen **before** the first measurement. No threshold is chosen here because none has been calibrated.
- Sample size follows the precision needed: `n ≈ 400` per class for about ±5 points at `r` near 0.5 (formula in `DATA_PLAN.md`). Classes below the target `n` are reported as undecided, not as zero.
- Falsifier: if `r` is low in every class with enough `n`, stop and keep the deterministic selector.

## 7. Privacy and data sovereignty

- Local only. Nothing is sent anywhere; the log lives in the existing ledger storage.
- No raw prompt, file content or path is stored. `features` are derived locally and coarse.
- Training later needs text. That is a **separate** opt-in (`keepPromptsForTraining`, off), never implied by `selectionMeasurement`.
- Same posture as Constitution Article VII.6: the user can disable, delete and export; deletion first shows what goes, including derived rollups, and says what it cannot undo; exports hold approved data only.

## 8. Required fixes before or with this feature

1. Replace the empty `catch` in `recordUsage` with a visible, typed failure (a counter and a UI notice), so a broken log is never mistaken for an empty one.
2. Populate `retryOf` and `holdout`, which exist but are always constant.
3. Give the five dead Intelligence settings a consumer or remove them from the UI; do not add a sixth.
4. Wire a call site for `selectModel` in the run path (shadow call only, no behavior change).

## 9. Stages

0. **Prerequisite, implemented 2026-10-31 (not yet called by any run path):** a verifier runner (`verifier.rs`, see `agent/packages/crewloom/ARCHITECTURE.md`). The Rust side runs the project's fixed verification commands (`AGENTS.md` Verification table) as processes and returns pass or fail per `VerifierKind`. It is the same runner `deep-execution` needs, so it is built once. First scope: `build`-class tasks in a bound project with `typecheck` and `test`. `chat` and `plan` tasks have no deterministic verifier and stay `none`; they are out of scope for the rate in §6.
1. Contract: `SelectionTrace` plus parser tolerance for old events; tests for old and new events.
2. Recorder and `passive` mode behind the setting, with `ar`/`en` strings in the dictionaries; fixes 1 to 4 from §8.
3. `probe` mode, only after a verifier exists for at least one task class.
4. Eval script for `r` and intervals; run once n is reached; apply the §6 rule.
5. Only if the rule passes: label review (`DATA_PLAN.md` D0), dataset from verified outcomes, train, compare against the heuristic and the deterministic selector on the frozen test set.

## 10. Verification of this feature

- Unit: trace parsing (old and new events), ladder and `shadowPick` correctness, no raw text in any stored field.
- Behavior: with the setting `off`, run behavior and stored events are byte-identical to today; with `passive`, the chosen model is unchanged.
- UI: Arabic and English strings, RTL and LTR, persistence of the setting, visible state when recording fails.

## 11. Open questions for the operator

1. ~~Which task classes have a deterministic verifier today?~~ Answered by inspection: none (see §2). Stage 0 creates the first.
2. Is `probe` acceptable at all (it spends free-tier quota and local compute in the background)? It also needs stage 0.
3. Should the five dead settings be wired or removed? Wiring changes product behavior.
4. Is measuring only `build`-class tasks acceptable as the first scope? It is the only class stage 0 can verify; routing for `chat` and `plan` would then stay on the deterministic selector until a separate quality signal exists.
