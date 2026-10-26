# Baseline and Reconnaissance Record (WP-00)

**Date:** 2026-10-25  
**Package:** WP-00 (Recon and baseline)  
**Role / Hat:** SDET  
**Author:** antigravity-1  

This document establishes the verified baseline of the codebase and host environment before any changes from the Universal Computer Use programme are introduced. All facts and command outputs recorded here were empirically measured on 2026-10-25.

---

## 1. Scope & Objective

Record the actual pre-existing state of typechecking, linting, test suites, build configuration, file structures, import conventions, protocols, and host tooling. Later work packages compare their gates against this baseline to ensure no new regressions are introduced.

---

## 2. Pre-existing Code Quality Gates (Step 2)

Commands executed from directory `/Volumes/data/projects/crewloom/agent`:

### 2.1 `pnpm run typecheck`
- **Exit Code:** `1` (FAILED)
- **Execution Summary:** 4 passed, 1 failed, 0 skipped in 6.73s.
  - `PASS host compiler` (0.51s)
  - `PASS Host Typert` (3.43s)
  - `PASS client compiler` (0.33s)
  - `PASS client aggregate check` (0.39s)
  - `FAILED host aggregate check` (6.21s, exit 1) — `tsc -b tsconfig.host.json`
- **Pre-existing Failure Details:**
  - `TS6307: File '.../packages/crewloom/contracts/src/personalization.ts' is not listed within the file list of project '.../tsconfig.host.json'` (and related contracts files `personalization-store.ts`, `personalization-lifecycle.ts`, `persona-builder.ts`, `capabilities.ts`, `activation-check.ts`, `evaluation.ts`, `skill-pack.ts`, and test files under `packages/crewloom/contracts/tests/`).
  - `TS2532: Object is possibly 'undefined'` in `packages/crewloom/contracts/tests/personalization-store.spec.ts` (lines 77, 80, 104, 207, 215, 243) and `personalization.spec.ts` (lines 65, 80).
  - `TS2345: Argument of type 'PersonaProfile | undefined' is not assignable to parameter of type 'PersonaProfile'` in `packages/crewloom/contracts/tests/personalization.spec.ts` (line 180).
  - `TS6307: File '.../packages/crewloom/skills/src/loader.ts' is not listed within the file list of project '.../tsconfig.host.json'` (imported via `./loader.js`).
  - `TS6307: File '.../packages/crewloom/skills/src/guard.ts' is not listed within the file list of project '.../tsconfig.host.json'` (imported via `./guard.js`).
  - `TS6307` in `packages/crewloom/skills/tests/composition.spec.ts`.

### 2.2 `pnpm run lint`
- **Exit Code:** `1` (FAILED)
- **Execution Command:** `tsx scripts/compile-referenced-projects.ts host-contracts && npm run lint:contracts-ready` (`tsx scripts/run-oxlint.ts .`)
- **Result:** Found 1 warning and 1179 errors across 5809 files with 90 rules using 12 threads (completed in 60.2s).
- **Pre-existing Failure Classes:**
  - `@stylistic(semi)`, `@stylistic(member-delimiter-style)`, `@stylistic(arrow-parens)` in `apps/crewloom-desktop/src/version.ts`.
  - `@typescript-eslint(no-floating-promises)`, `typescript(no-unsafe-assignment)`, `typescript(no-unsafe-member-access)`, `typescript(no-confusing-void-expression)` in `apps/crewloom-studio/tests/chat.test.ts`.
  - Numerous legacy stylistic and typing errors in `apps/crewloom-desktop` and `apps/crewloom-studio`.

### 2.3 `pnpm exec vitest run packages/experimental/cua packages/crewloom`
- **Exit Code:** `0` (ALL PASSED)
- **Test Files:** `21 passed (21)`
- **Tests:** `402 passed (402)`
- **Duration:** 3.31s
- **Breakdown:**
  - `packages/crewloom/contracts/tests/personalization.spec.ts` (15 tests passed)
  - `packages/crewloom/contracts/tests/skill-pack.spec.ts` (13 tests passed)
  - `packages/crewloom/contracts/tests/evaluation.spec.ts` (11 tests passed)
  - `packages/crewloom/contracts/tests/personalization-store.spec.ts` (23 tests passed)
  - `packages/crewloom/contracts/tests/persona-builder.spec.ts` (19 tests passed)
  - `packages/crewloom/contracts/tests/personalization-lifecycle.spec.ts` (13 tests passed)
  - `packages/crewloom/contracts/tests/activation-check.spec.ts` (6 tests passed)
  - `packages/crewloom/contracts/tests/capabilities.spec.ts` (8 tests passed)
  - `packages/crewloom/skills/tests/composition.spec.ts` (1 test passed)
  - `packages/experimental/cua/tests/api.spec.ts` (73 tests passed)
  - `packages/experimental/cua/tests/application-access.spec.ts` (25 tests passed)
  - `packages/experimental/cua/tests/native-client.spec.ts` (44 tests passed)
  - `packages/experimental/cua-macos/tests/native-build.spec.ts` (17 tests passed)
  - `packages/experimental/cua-macos/tests/shared-native.spec.ts` (37 tests passed)
  - `packages/experimental/cua-macos/tests/loader-composition.spec.ts` (1 test passed)
  - `packages/experimental/cua-macos/tests/provider-lifecycle.spec.ts` (41 tests passed)
  - `packages/experimental/cua-macos/tests/large-image-ptc.spec.ts` (1 test passed)
  - And all remaining cua/cua-macos suites passed.

---

## 3. Build, Test Configuration, Import Style, and i18n Architecture (Step 3)

### 3.1 Build Architecture for `@crewloom/plugin-skills`
- **Build Tool:** `tsdown` (invoked via `"build": "tsdown"` in `package.json`).
- **Configuration:** No package-local `tsdown.config.*` exists in `packages/crewloom/skills/`.
- **Repository Configuration:** Root `agent/tsdown.config.ts` defines the workspace build, selecting packages via `workspacePackageGlobs(globSync(['vendor/*/package.json', 'packages/*/*/package.json']))`.
- **Entry & Outputs:** Standard package build targets entry `src/index.ts`, emitting ESM runtime bundle to `lib/index.js` and TypeScript declaration artifacts to `lib/types/` directed by `tsconfig.json` (`outDir: "lib/types"`).

### 3.2 Vitest Include Patterns (`agent/vitest.config.ts`)
- **Pattern Definition:**
  ```ts
  const testIncludes = [
    'packages/*/*/tests/**/*.spec.{ts,tsx}',
    'apps/*/tests/**/*.spec.{ts,tsx}',
    'scripts/**/*.spec.ts',
    'website/tests/**/*.spec.ts',
  ]
  ```
- **Matching for `packages/crewloom/*/tests/*.spec.ts`:**
  **MATCHED.** The glob `packages/*/*/tests/**/*.spec.{ts,tsx}` matches two directory levels below `packages/`: `packages/<group>/<package>/tests/**/*.spec.ts`. Since Crewloom packages are placed at `packages/crewloom/<name>`, their tests under `tests/*.spec.ts` match this include pattern natively.

### 3.3 Import-Extension Conventions
- **`packages/crewloom/contracts/src`:** Relative module imports strictly use the `.ts` file extension:
  - Example: `import { canRate, resolveVerdict } from './evaluation.ts'`
  - Example: `import { checkSkillStructure } from './skill-pack.ts'`
  - Example: `import { findSecretLikeValues } from './personalization.ts'`
- **`packages/crewloom/skills/src`:** Relative module imports currently use `.js` in `skills/src/index.ts`:
  - `import { CoreSkillsRepository } from './loader.js'`
  - `import { ZeroDestructionGuard } from './guard.js'`
- **Authoritative Rule:** In accordance with root `AGENTS.md` and `agent/AGENTS.md` ("ESM only. Local relative imports use the `.ts` extension in `agent/`"), new TypeScript code in `packages/crewloom/*` must strictly use `.ts` relative imports.

### 3.4 Shape and Loader of `skills/locale/*.json`
- **Shape:** Flat key-value JSON dictionary mapping metadata keys to localized string values:
  - `ar.json`:
    ```json
    {
      "name": "مهارات وحارس كرو لوم",
      "description": "محمل لـ 44 دوراً تخصصياً ثنائي اللغة مع حارس سياسة عدم الهدم وعقود التنفيذ"
    }
    ```
  - `en.json`:
    ```json
    {
      "name": "Crewloom Skills & Guard",
      "description": "Loader for 44 bilingual specialist roles and Zero-Destruction execution contracts"
    }
    ```
- **Loader:** Harness Cordis plugin loader infrastructure (`agent/packages/boot/app-boot/src/package-meta.ts` and `agent/packages/boot/plugin-manager`). It dynamically resolves package export paths matching `./locale/*.json` to populate plugin display names and descriptions in runtime manifests, settings catalogs, and inventory inspectors.

### 3.5 Desktop App i18n Dictionaries
- **Location:** `agent/apps/crewloom-desktop/src/lib/`
  - `i18n.ts`: Primary application UI dictionary, containing structured Arabic (`const ar = { ... }`) and English (`const en = { ... }`) translation tables for controls, inputs, headers, connections, and error notices.
  - `roles-i18n.ts`: Specialist role translations and localized capability descriptions.

---

## 4. CUA Protocol Methods and Schema Comparison (Step 4)

Both `agent/packages/experimental/cua/src/protocol.ts` and `agent/packages/experimental/cua-macos/native/protocol.schema.json` define the exact same 20 method names:

1. `getCapabilities`
2. `listApps`
3. `findApps`
4. `getApp`
5. `activate`
6. `show`
7. `listWindows`
8. `getState`
9. `hover`
10. `click`
11. `setValue`
12. `selectText`
13. `performSecondaryAction`
14. `typeText`
15. `paste`
16. `pressKey`
17. `scroll`
18. `drag`
19. `screenshot`
20. `launchApp`

### Differences Between `protocol.ts` and `protocol.schema.json`
1. **Model Tool Boundary Separation:**
   - In `protocol.ts`, the model-submittable `Request` discriminated union contains only 19 methods (`getCapabilities` through `screenshot`).
   - `launchApp` is explicitly segregated into `NativeOnlyOperations` as an executor-only continuation invoked strictly after explicit application consent; it is excluded from model-facing tools.
2. **Resource Parameter Injection:**
   - In `protocol.ts`, Host-provided execution limits (`maxElements`, `maxDepth`, `durationMs`, `steps`, `maxClipboardBytes`, `pasteReadTimeoutMs`, `maxAppMatches`) are isolated in `NativeResourceParameters` and injected by the host process.
   - In `protocol.schema.json`, all 20 methods are represented as a unified `oneOf` JSON schema representing the native IPC/JSONL wire contract with the child helper binary. The resource parameters are embedded directly into each method's `params` schema.
3. **Envelope Requirement:**
   - `protocol.schema.json` requires an outer envelope with fields `"id"` (string), `"method"` (string constant), and `"params"` (object with `additionalProperties: false`).

---

## 5. Host System and Tooling Inventory (Step 5)

All measurements gathered on 2026-10-25:

| Tool / Metric | Measured Value / Path | Status |
|---|---|---|
| `uname -a` | `Darwin MacBook-Pro.local 25.6.0 Darwin Kernel Version 25.6.0: Fri Jul 31 19:19:08 PDT 2026; root:xnu-12377.161.14~5/RELEASE_ARM64_T6050 arm64` | Verified |
| `sw_vers` | `ProductName: macOS`, `ProductVersion: 26.6.2`, `BuildVersion: 25G83` | Verified |
| `node --version` | `v26.7.0` | Verified |
| `pnpm --version` | `12.15.0` | Verified |
| `python3 --version` | `Python 3.14.7` | Verified |
| `adb` | `/Users/macbook/Library/Android/sdk/platform-tools/adb` | **Found** |
| `xcrun simctl` | `/usr/bin/xcrun simctl` | **Found** |
| `swift` | `/usr/bin/swift` | **Found** |
| `cargo` | `not found` in PATH | **Not Found** |

---

## 6. Resolution of Open Question (Step 6)

### Question:
*Where is the single owner of desktop i18n strings, and does a plugin-local `locale/` directory (as in `skills/locale`) fit? Resolve in WP-00 and use in WP-14.*

### Resolution:
1. **Desktop UI Text Ownership:**
   - `agent/apps/crewloom-desktop/src/lib/i18n.ts` is the single owner of desktop application UI copy, button labels, and user settings strings.
2. **Plugin Metadata Ownership:**
   - Plugin-local `locale/*.json` files (following `@crewloom/plugin-skills/locale/{ar,en}.json`) are used specifically for Cordis / DSH plugin discovery and metadata (plugin title and plugin description loaded by `packages/boot/app-boot`). `@crewloom/plugin-computer-use` will export `./locale/*.json` with `"name"` and `"description"` in Arabic and English for this purpose.
3. **Domain Error & Permission Explanations (WP-14 Architecture):**
   - User-facing diagnostic messages for domain errors (`ComputerUseErrorCode`) and permission instructions (`Permission`) belong to the domain layer of the computer-use subsystem.
   - Per WP-14 specification, they must be implemented in a dedicated bilingual module in `@crewloom/plugin-computer-use` (e.g., `src/locale/messages.ts` with pure function `messageFor(error, language)`), providing complete Arabic and English dictionaries that desktop UI, CLI, and bridge can import without duplicating translation dictionaries.
