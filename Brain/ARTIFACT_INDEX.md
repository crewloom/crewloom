# Artifact Index

Registry of governed artifacts, typed per [`ARTIFACT_TAXONOMY.md`](ARTIFACT_TAXONOMY.md). This is the lookup the agent uses to explain any artifact (skill `crewloom-explain`). Skills are not listed here: their name, purpose and trigger live in each `.agent/skills/*/SKILL.md` frontmatter (one home per fact). `status`: **active** (exists and is used) or **planned** (decided, not built).

## Constitution

| name | purpose | enforced_by | owner | status |
|---|---|---|---|---|
| constitution | Immutable invariants and order of precedence | human review; Art. III.3 tests | `CONSTITUTION.md` | active |

## Rules

| name | purpose | enforced_by | owner | status |
|---|---|---|---|---|
| architecture-dependency-direction | Imports follow the documented one-way dependency map | `scripts/check-architecture.mjs` | `AGENTS.md` § Architecture | active |
| file-size-limit | No source file over 800 lines | `scripts/check-architecture.mjs` (currently reports 3 violations: `desktop.ts` 834, `solver.rs` 895 and 881) | `AGENTS.md` § Architecture | active, failing |
| i18n-no-inline-ternary | User-facing strings come from dictionaries only | `scripts/check-architecture.mjs` (JSX/TSX only) | `AGENTS.md` § Strict Internationalization | active |
| free-and-local-first | Selection decisions (classify, select, verify, escalate) run on free or local models | none yet | `ARTIFACT_INDEX.md` (this row) until the selection contract exists | planned |

## Protocols

| name | trigger | exit condition | enforced_by | owner | status |
|---|---|---|---|---|---|
| release | any verified modification completes | tag exists locally and on remote; GitHub Release published; CI green | `scripts/release.sh` (steps 3-4); rest advisory | `AGENTS.md` § Mandatory Release Protocol | active |
| post-push-ci-verification | any push, merge or release | all workflow runs for `HEAD` pass, checked with `gh` only | advisory | `AGENTS.md` § Non-negotiable 7; skill `crewloom-release-verifier` | active |
| model-escalation | a task is submitted for execution | verified result, or escalation limit (2) reached | Guard (planned) | to be created | planned |

## Contracts

| name | purpose | enforced_by | owner | status |
|---|---|---|---|---|
| shared-contracts | Cross-package types and `Result<T,E>` | TypeScript `strict`, tests | `agent/packages/crewloom/contracts` | active |
| model-cost-class | Cost class of a model: `local`, `free` or `paid` (unregistered ids are `paid`) | vitest: `contracts/tests/model-catalog.spec.ts`; desktop drift test `apps/crewloom-desktop/tests/model-cost-drift.spec.ts` | `agent/packages/crewloom/contracts/src/model-catalog.ts` | active (bridge not yet migrated; free list unverified against providers) |
| model-metadata | Names, descriptions, context labels for UI | none; duplicated in `bridge/src/domain/model-catalog.ts` and `agent/apps/crewloom-desktop/src/lib/models-catalog.ts`, and the two disagree on context windows and free membership | both files until moved | planned |
| model-selection | Deterministic choice of model for a task class, free/local first | Guard (planned) | to be created | planned |

## Roles (model selection)

| name | responsibility | runs on | status |
|---|---|---|---|
| classifier | Assigns the task to a task class | Pulse (local) | planned |
| selector | Applies the selection contract to pick a model | deterministic code | planned |
| verifier | Checks the result against tests or schema | deterministic code first, free model second | planned |
| escalator | Decides to move up a tier after a failed verification or rate limit; escalates automatically, no operator prompt | deterministic code | planned |

## Guards

| name | enforces | owner | status |
|---|---|---|---|
| check-architecture | dependency direction | `scripts/check-architecture.mjs` | active |
| bridge-prompt-guards | checks before a prompt is submitted | `bridge/src/control-room/submit/guards.ts` | active (path per `AGENTS.md`, not re-verified) |

## Known misclassifications (to resolve)

- Skill `crewloom-release-verifier` describes itself as a "protocol" with mandatory steps. By the taxonomy it is a **Protocol** stored in the skills folder; its content duplicates `AGENTS.md` § Non-negotiable 7.
- Skill `crewloom-context-memory-guard` mixes Rules (never load out-of-scope context), a Protocol-like procedure and Skill guidance. Needs splitting before it can be typed.
