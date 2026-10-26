# Repository Build Gates Verification (WP-58 & WP-61)

**Date:** 2026-10-26  
**Packages:** WP-58 (`Repository build gates for the new packages`), WP-61 (`Test typing errors and honest classification`)  
**Role:** SRE and SDET  
**Author:** antigravity-1  
**Working Directory:** `/Volumes/data/projects/crewloom/agent`  

---

## 1. Scope & Objective

Empirically execute and record the top-level repository build gates mandated by `agent/AGENTS.md`:
1. `pnpm run build:artifacts`
2. `pnpm run build:check`

This document records the complete trajectory from initial gate measurement in WP-58, through the authorized `tsconfig.host.json` project registration, to the final elimination of all type errors in our test files in WP-61.

Per protocol and package rules: `tsconfig.host.json` was registered only after explicit user authorization on 2026-10-26, and no build configurations were edited thereafter.

---

## 2. Gate Execution Results (Initial WP-58 Measurement)

### 2.1 Gate 1: `pnpm run build:artifacts`
- **Command:** `pnpm run build:artifacts` (`tsx scripts/build.ts --scope artifacts`)
- **Exit Code:** `0` (SUCCESS)
- **Duration:** 19.00s
- **Worker Configuration:** 7 gate(s) with 7 worker(s) across 15 CPUs
- **Execution Log:**
  - `PASS native addon` (0.74s)
  - `PASS host compiler` (0.50s)
  - `PASS Host bundle` (7.56s)
  - `PASS Desktop bundle` (0.90s)
  - `PASS client compiler` (0.33s)
  - `PASS Client bundle` (2.56s)
  - `PASS Web build` (6.42s)
- **Summary:** `7 passed, 0 failed, 0 skipped in 19.00s.`
- **Recorded Artifacts:** 325 client artifact(s) with 3 public value(s).

---

### 2.2 Gate 2: `pnpm run build:check` (Before Package Registration)
- **Command:** `pnpm run build:check` (`tsx scripts/build.ts --scope check`)
- **Exit Code:** `1` (FAILED)
- **Duration:** 26.65s
- **Worker Configuration:** 2 gate(s) with 2 worker(s)
- **Execution Log:**
  - `PASS client aggregate check` (2.53s)
  - `FAILED host aggregate check` (26.64s, exit 2) — `tsc -p tsconfig.host.json`
- **Summary:** `1 passed, 1 failed, 0 skipped in 26.65s.`

---

## 3. Initial Error Breakdown and Classification (Recounted in WP-61)

The initial `host aggregate check` produced **102** TypeScript diagnostic error lines.
Correct classification separating pre-existing files (from `BASELINE.md`) versus files created by the Universal Computer Use programme:

```
Total Errors:        102
├── Pre-existing:     23 (22.5%)
└── Our Packages:     79 (77.5%)
```

### 3.1 Pre-existing Errors (23 errors)
These errors were verified present in `BASELINE.md` before this programme began:

| Error Code | Count | Files / Descriptions |
|---|---|---|
| `TS6307` | 13 | Pre-existing files unlisted in `tsconfig.host.json`: `packages/crewloom/contracts/src/` (`personalization.ts`, `personalization-store.ts`, `personalization-lifecycle.ts`, `persona-builder.ts`, `capabilities.ts`, `activation-check.ts`, `evaluation.ts`, `skill-pack.ts`, `tests/activation-check.spec.ts`), `packages/crewloom/skills/src/` (`loader.ts`, `guard.ts`), `packages/crewloom/skills/tests/composition.spec.ts` (x2) |
| `TS2532` | 8 | Object possibly 'undefined' in `packages/crewloom/contracts/tests/personalization-store.spec.ts` (lines 77, 80, 104, 207, 215, 243) and `personalization.spec.ts` (lines 65, 80) |
| `TS2345` | 1 | Argument type mismatch in `packages/crewloom/contracts/tests/personalization.spec.ts` (line 180) |
| `TS2717` | 1 | Subsequent property declarations in `packages/crewloom/skills/src/index.ts` (line 22) |

*(Note: `contracts/src/computer-use.ts` and `contracts/src/mobile-use.ts` were created in WP-01 and are correctly classified under "Our Packages" below, not as pre-existing).*

---

### 3.2 Our Package Errors (79 errors)

| Error Code | Count | Description |
|---|---|---|
| `TS6307` | 72 | Programme files unlisted in `tsconfig.host.json`: `contracts/src/computer-use.ts` (1), `contracts/src/mobile-use.ts` (1), `computer-use-conformance/` (8), `computer-use/` (30), `mobile-use/` (29), `preset/` (3) |
| `TS2339` | 4 | Strict `data` property access on un-narrowed `Result` in `computer-use/tests/adapters/macos/live.spec.ts` |
| `TS6133` | 1 | Unused parameter `action` in `computer-use/tests/policy/policy-gate.spec.ts` |
| `TS2322` | 1 | Type assertion `verified: true` instead of contract invariant `verified: false` in `mobile-use/tests/core/policy.spec.ts` |
| `TS2379` | 1 | Exact optional property type (`string \| undefined`) in `mobile-use/tests/ios/simulator/wda.spec.ts` |

---

## 4. Unlisted Files List (TS6307)

The 72 unlisted files belonging to this programme prior to registration:

### `@crewloom/contracts` (2 programme files)
1. `packages/crewloom/contracts/src/computer-use.ts`
2. `packages/crewloom/contracts/src/mobile-use.ts`

### `@crewloom/computer-use-conformance` (8 files)
1. `packages/crewloom/computer-use-conformance/src/conformance.ts`
2. `packages/crewloom/computer-use-conformance/src/fake-backend.ts`
3. `packages/crewloom/computer-use-conformance/src/index.ts`
4. `packages/crewloom/computer-use-conformance/src/probes/focus.ts`
5. `packages/crewloom/computer-use-conformance/src/probes/index.ts`
6. `packages/crewloom/computer-use-conformance/src/probes/pointer.ts`
7. `packages/crewloom/computer-use-conformance/src/suite.ts`
8. `packages/crewloom/computer-use-conformance/src/types.ts`

### `@crewloom/computer-use` (30 files)
1. `packages/crewloom/computer-use/src/adapters/macos/action-mapping.ts`
2. `packages/crewloom/computer-use/src/adapters/macos/adapter.ts`
3. `packages/crewloom/computer-use/src/adapters/macos/capabilities.ts`
4. `packages/crewloom/computer-use/src/adapters/macos/error-mapping.ts`
5. `packages/crewloom/computer-use/src/adapters/macos/index.ts`
6. `packages/crewloom/computer-use/src/adapters/macos/real-client.ts`
7. `packages/crewloom/computer-use/src/adapters/macos/types.ts`
8. `packages/crewloom/computer-use/src/audit/events.ts`
9. `packages/crewloom/computer-use/src/audit/index.ts`
10. `packages/crewloom/computer-use/src/audit/redact.ts`
11. `packages/crewloom/computer-use/src/audit/sink.ts`
12. `packages/crewloom/computer-use/src/audit/with-audit.ts`
13. `packages/crewloom/computer-use/src/core/detect-platform.ts`
14. `packages/crewloom/computer-use/src/core/index.ts`
15. `packages/crewloom/computer-use/src/core/negotiator.ts`
16. `packages/crewloom/computer-use/src/core/registry.ts`
17. `packages/crewloom/computer-use/src/core/unsupported-backend.ts`
18. `packages/crewloom/computer-use/src/messages/ar.ts`
19. `packages/crewloom/computer-use/src/messages/en.ts`
20. `packages/crewloom/computer-use/src/messages/index.ts`
21. `packages/crewloom/computer-use/src/policy/decide.ts`
22. `packages/crewloom/computer-use/src/policy/default-denylist.ts`
23. `packages/crewloom/computer-use/src/policy/index.ts`
24. `packages/crewloom/computer-use/src/policy/kill-switch.ts`
25. `packages/crewloom/computer-use/src/policy/types.ts`
26. `packages/crewloom/computer-use/src/policy/with-policy.ts`
27. `packages/crewloom/computer-use/src/strategy/index.ts`
28. `packages/crewloom/computer-use/src/strategy/ladder.ts`
29. `packages/crewloom/computer-use/src/strategy/specificity.ts`
30. `packages/crewloom/computer-use/src/strategy/types.ts`

### `@crewloom/mobile-use` (29 files)
1. `packages/crewloom/mobile-use/src/android/adb/client.ts`
2. `packages/crewloom/mobile-use/src/android/adb/index.ts`
3. `packages/crewloom/mobile-use/src/android/adb/parser.ts`
4. `packages/crewloom/mobile-use/src/android/adb/process.ts`
5. `packages/crewloom/mobile-use/src/android/adb/types.ts`
6. `packages/crewloom/mobile-use/src/android/text/clipboard.ts`
7. `packages/crewloom/mobile-use/src/android/text/index.ts`
8. `packages/crewloom/mobile-use/src/android/text/input.ts`
9. `packages/crewloom/mobile-use/src/android/text/strategy.ts`
10. `packages/crewloom/mobile-use/src/android/text/types.ts`
11. `packages/crewloom/mobile-use/src/android/ui/bounds.ts`
12. `packages/crewloom/mobile-use/src/android/ui/gestures.ts`
13. `packages/crewloom/mobile-use/src/android/ui/index.ts`
14. `packages/crewloom/mobile-use/src/android/ui/screenshot.ts`
15. `packages/crewloom/mobile-use/src/android/ui/state.ts`
16. `packages/crewloom/mobile-use/src/android/ui/types.ts`
17. `packages/crewloom/mobile-use/src/android/ui/xml-parser.ts`
18. `packages/crewloom/mobile-use/src/core/denylist.ts`
19. `packages/crewloom/mobile-use/src/core/device-registry.ts`
20. `packages/crewloom/mobile-use/src/core/device-session.ts`
21. `packages/crewloom/mobile-use/src/core/index.ts`
22. `packages/crewloom/mobile-use/src/core/tools.ts`
23. `packages/crewloom/mobile-use/src/core/types.ts`
24. `packages/crewloom/mobile-use/src/core/unsupported-device-backend.ts`
25. `packages/crewloom/mobile-use/src/ios/simulator/adapter.ts`
26. `packages/crewloom/mobile-use/src/ios/simulator/index.ts`
27. `packages/crewloom/mobile-use/src/ios/simulator/simctl-client.ts`
28. `packages/crewloom/mobile-use/src/ios/simulator/types.ts`
29. `packages/crewloom/mobile-use/src/ios/simulator/wda-client.ts`

### `@crewloom/preset` (3 files)
1. `packages/crewloom/preset/src/computer-use.ts`
2. `packages/crewloom/preset/src/index.ts`
3. `packages/crewloom/preset/src/mobile-use.ts`

---

## 5. Applied `tsconfig.host.json` Registration

On 2026-10-26, user authorization was granted to register workspace package references in `agent/tsconfig.host.json`. The registration was applied by the reviewer, adding the references to the host aggregate configuration.

### Historical Proposal Snippet (proposed, not tried by agent prior to user authorization)
```json
[
  { "path": "./packages/crewloom/contracts" },
  { "path": "./packages/crewloom/skills" },
  { "path": "./packages/crewloom/computer-use" },
  { "path": "./packages/crewloom/mobile-use" },
  { "path": "./packages/crewloom/computer-use-conformance" },
  { "path": "./packages/crewloom/preset" }
]
```

### Result of Registration
Following the application of the references:
- **`TS6307` error count dropped from 85 to 0**.
- Zero files in `@crewloom/*` packages are unlisted.

---

## 6. Resolution of Test File Errors (WP-59 & WP-61)

Following package registration, `pnpm run build:check` surfaced 7 type errors in our test files:
1. `computer-use/tests/adapters/macos/live.spec.ts` (4 x `TS2339`): Fixed in WP-59 by narrowing `Result` before reading `.data`.
2. `computer-use/tests/policy/policy-gate.spec.ts` (1 x `TS6133`): Fixed in WP-61 by renaming unused parameter `action` to `_action`.
3. `mobile-use/tests/core/policy.spec.ts` (1 x `TS2322`): Fixed in WP-61 by setting `verified: false` to conform to contract invariant.
4. `mobile-use/tests/ios/simulator/wda.spec.ts` (1 x `TS2379`): Fixed in WP-61 by typing `receivedRequests` properties as `string | undefined` to satisfy `exactOptionalPropertyTypes: true`.

---

## 7. Final Verification Results (WP-61 Gate)

Command executed:
```bash
cd /Volumes/data/projects/crewloom/agent && pnpm run build:check
```

Execution Output:
```text
$ tsx scripts/build.ts --scope check
run-gates: build:check running 2 gate(s) with 2 worker(s) from 12 local default worker(s) of 15 CPU(s).
run-gates: start host aggregate check
run-gates: start client aggregate check
run-gates: PASS client aggregate check (2.68s)

== FAILED host aggregate check (6.01s) ==
command: tsc -p tsconfig.host.json
outcome: exit 1
packages/crewloom/contracts/tests/personalization-store.spec.ts(77,12): error TS2532: Object is possibly 'undefined'.
packages/crewloom/contracts/tests/personalization-store.spec.ts(80,12): error TS2532: Object is possibly 'undefined'.
packages/crewloom/contracts/tests/personalization-store.spec.ts(104,12): error TS2532: Object is possibly 'undefined'.
packages/crewloom/contracts/tests/personalization-store.spec.ts(207,12): error TS2532: Object is possibly 'undefined'.
packages/crewloom/contracts/tests/personalization-store.spec.ts(215,12): error TS2532: Object is possibly 'undefined'.
packages/crewloom/contracts/tests/personalization-store.spec.ts(243,12): error TS2532: Object is possibly 'undefined'.
packages/crewloom/contracts/tests/personalization.spec.ts(65,12): error TS2532: Object is possibly 'undefined'.
packages/crewloom/contracts/tests/personalization.spec.ts(80,12): error TS2532: Object is possibly 'undefined'.
packages/crewloom/contracts/tests/personalization.spec.ts(180,32): error TS2345: Argument of type 'PersonaProfile | undefined' is not assignable to parameter of type 'PersonaProfile'.
  Type 'undefined' is not assignable to type 'PersonaProfile'.

run-gates: 1 passed, 1 failed, 0 skipped in 6.01s.
```

### Final Error Summary
- **Total Remaining Errors:** **9** (down from 102).
- **Errors in Our Packages (`computer-use`, `mobile-use`, `computer-use-conformance`, `preset`):** **0**.
- **Remaining Errors:** All 9 are the pre-existing test typing errors in `packages/crewloom/contracts/tests/personalization*.spec.ts` (8 x `TS2532`, 1 x `TS2345`), which are strictly preserved per repository instructions.
