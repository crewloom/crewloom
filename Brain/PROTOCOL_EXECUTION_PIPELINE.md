# Protocol: execution-pipeline

Type: Protocol (see [`ARTIFACT_TAXONOMY.md`](ARTIFACT_TAXONOMY.md)). Arabic edition: [`PROTOCOL_EXECUTION_PIPELINE.ar.md`](PROTOCOL_EXECUTION_PIPELINE.ar.md). Status: **written, advisory**. Only the pieces marked *exists* below run today; the gate runner, technology profiles, risk router, holdout checks and escape ledger are *planned* and not built.

Purpose: make the agent accurate on any software task in any project, even when the underlying model is weak. A builder that writes the check it then satisfies cannot be trusted to verify itself, so the protocol moves verification into skills, tools and rules the builder does not control. It is project-agnostic: it names no application and no stack.

## Components (the protocol is these parts, not prose)

| Kind | Component | Owns |
|---|---|---|
| Skill | `.agent/skills/crewloom-execution-pipeline` | running the five steps, task weight, depth, stop rules |
| Skill | `.agent/skills/crewloom-pin-before-change` | step 2: characterization tests with proof they can fail |
| Skill | `.agent/skills/crewloom-adversarial-verify` | step 4: sabotage-red, claim-versus-code audit, evidence-only findings |
| Tool | `scripts/exec-gates.mjs` *exists* | stack detection and running build, typecheck, lint and test, plus the promise gate; prints evidence, marks gates it could not run as `NOT-RUN` |
| Tool | `scripts/promise-ledger.sh` *exists* | promise gate (`ENGINEERING-PROTOCOLS.md` §2.8), run by the Stop hook |
| Tool | `scripts/check-architecture.mjs` *exists* | dependency-direction check |
| Rule | the Rules below | what no step may skip |
| Planned | holdout verifier, diff-scope check, report generator, escape ledger | not built |

```
name:        execution-pipeline
trigger:     the agent is asked to build, change, fix, refactor or migrate any software, in any sub-project or any project the operator points it at
steps:
  1. UNDERSTAND  Classify the task (build | feature | fix | refactor | migrate). Map the code the task touches and its callers. Split the request into one-line promises with a postcondition each (Promise Ledger, `ENGINEERING-PROTOCOLS.md` §2.8). Record every assumption; ask the operator only when the answer would change a postcondition.
  2. PIN         Before editing existing code, write tests that capture its current behavior and run them green. A fix first needs a deterministic red reproduction (BDRP). New code starts with the promise tests failing for the right reason.
  3. CHANGE      Make the smallest change that satisfies the promises. Structural refactors and behavior changes go in separate commits. Stay inside the files the map names; anything else is reported, not edited.
  4. PROVE       Run the project's gates with `scripts/exec-gates.mjs`: build, typecheck, lint with zero warnings, tests, and the repo's architecture check. Run every promise test and every pinned test. Sabotage-red each promise (remove or stub the implementation, the test must go red, restore it). Run the independent verifier's holdout checks, which the builder never sees.
  5. DELIVER     The harness generates the report from gate evidence: what was run with its real result, what was not run or not verified, open assumptions, and the diff scope. The builder cannot edit the report's verdict.
exit:        every promise has a passing test with sabotage-red evidence, every pinned test is still green, the profile gates pass, the holdout checks pass, and the report is generated
on_failure:  a failed gate returns a localized repair task (file, line, failing input) to the builder. The same cause twice stops that approach: change strategy (split the task, escalate per `PROTOCOL_MODEL_ESCALATION.md`, or ask the operator). More than two attempts on one cause: stop and report the blocker and the evidence. Never report success with an open gate.
enforced_by: partial. exists: `scripts/exec-gates.mjs`, `scripts/promise-ledger.sh` (Stop hook `.claude/hooks/promise-ledger-stop.sh`), `scripts/check-architecture.mjs`; the three skills are advisory. planned: holdout verifier, diff-scope check, report generator. Enforcement added 2026-11-22 (Claude Code only, `decisions/2026-11-22-enforced-production-gates.md`): `scripts/risk-tier.mjs` computes the tier; `scripts/task-open.mjs` plus `.crewloom/hooks/task-gate.sh` block code edits without an open task; `scripts/exec-gates.mjs --write-evidence` records evidence and `scripts/release.sh` refuses without it. Bash writes bypass the hook.
owner:       this file; promise mechanics in `docs/architecture/ENGINEERING-PROTOCOLS.md` §2.8
```

## Crewloom roles

Roles are separated by function, and the role that builds never approves. Each maps onto a squad already defined in [`SKILLS_AND_TEAMS_CATALOG.md`](SKILLS_AND_TEAMS_CATALOG.md); no role is a new agent type.

| Role | Does | Squad |
|---|---|---|
| Planner | Steps 1 and the design note | Architecture & Planning |
| Builder | Steps 2 (new code) and 3 | the domain squad for the files touched |
| Verifier | Pinning tests, holdout checks, sabotage-red, step 4 | QA & Debugging |
| Reviewer | Reads the diff and the README against the code; every finding names a file and line or it is dropped | QA & Debugging, on a different model family from the Builder |
| Releaser | Step 5 and the release (`AGENTS.md` § Mandatory Release Protocol) | `crewloom-release-verifier` |

A single small model may play several roles in sequence. It may not both write a promise test and be the only one to judge it: the holdout checks and sabotage-red are the independent part.

## Task types

Same five steps, different weight.

| Type | Weight falls on | Reuses |
|---|---|---|
| build | promises and tests before code | FEP |
| feature on existing code | PIN: without it nothing shows the change broke something | FEP, ASDP when boundaries move |
| fix | the red reproduction and the 5-Whys | BDRP |
| refactor | proof that behavior is unchanged: same pinned tests before and after | FEP structural rules |
| migrate | expand and contract, each step reversible | ASDP |

## Depth

The task type sets the path; risk sets how deep. A deterministic risk score (not a model's opinion) raises depth when the change touches: security, credentials or crypto; persistent storage or deletion; a system boundary (network, files, native bridge, subprocess); a new claim in a README or UI; or an area listed in the escape ledger. A one-line low-risk fix runs UNDERSTAND, CHANGE and a reduced PROVE. High risk adds the independent Reviewer on a different model family and the full holdout set.

## Technology profiles

`scripts/exec-gates.mjs` detects the stack from project files (Node, Flutter, Rust, Go, Python) and runs its gates. A project overrides or extends detection with `.crewloom/profile.json` (`{"gates": {"test": "..."}}`); an unknown stack needs that file, confirmed once by the operator. The skills never hardcode a stack's commands. Stack lint strictness (for example forbidding blanket lint suppression) belongs in the profile or the project's own config, not in this protocol.

## Evidence order

Prefer, in this order: an executed check (a test that went red then green, a sabotage run), a deterministic tool (analyzer, type checker), and only then a model's judgment. A finding from a model without a file and line is discarded. Do not turn a check a program can run into an opinion.

## Escape ledger

Each defect found after delivery is recorded with its area and the step that should have caught it. A custom check is added only after the same defect escapes twice (`ENGINEERING-PROTOCOLS.md` §2.8 item 5). A check that catches nothing over a stated number of tasks moves to a lighter path, so cost does not grow without bound. Planned file: `.crewloom/ledger/escapes.json`.

## Crewloom invariants this protocol keeps

- **Zero-Destruction** (Constitution Art. III): PIN and CHANGE edit in place; deleting or moving a file needs a backup and an adapter. Sabotage-red restores the implementation it removed.
- **No fabrication** (`AGENTS.md` § Non-negotiable 3; Constitution Art. VII): the report lists only commands that ran, with real output, and states what was not verified.
- **Owner sovereignty**: the operator approves promises and any change of scope. Messages, deploys, purchases and history rewrites still need explicit authorization.
- **Bilingual**: user-facing strings in a change go through the i18n dictionaries; both languages are verified for UI work.
- **Release**: a verified change ends in the release flow of `AGENTS.md` and CI is checked with `gh`, never by scraping.
- **Order of precedence** (Constitution Art. VI): the Constitution, then `AGENTS.md`, then this protocol.

## Limits

- Enforcement gaps: edits made through Bash bypass the task gate; other agents and tools get none of it; security scanners other than gitleaks (semgrep, cargo-audit, pip-audit) are not installed, so tier 3 on those stacks reports NOT-RUN and fails; the workspace root is not a git repo, so where these scripts are committed is undecided.
- Nothing here has been measured. Unknown: gate time and token cost per task size, how many seeded faults the pipeline catches, and how often a gate blocks sound work. A seeded-fault benchmark built from real defects that escaped in several projects and stacks is the planned first measurement; do not claim effectiveness before it exists. `exec-gates.mjs` has been run on `bridge/` (Node) and one Flutter project only; other stacks are untested.
- PIN is only as good as the tests the agent writes on weak existing coverage. Sabotage-red is what exposes a tautological one; do not drop it to save time.
- A Reviewer on a different model family reduces correlated mistakes but does not remove them. It supplements executed checks and never replaces them.
- Operator approval of every promise can slow small tasks. A pre-approved path for low-risk tasks is planned but not defined.
