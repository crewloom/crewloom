# Work packages

Each package is self-contained. State (status, owner, dependencies, owned paths) lives in `ledger.json`; this file holds the instructions. Section headings must read exactly `### WP-NN title` because `python3 core/scripts/program_ledger.py check` matches them.

Conventions used below:
- `A` = `agent/packages/crewloom`, `CU` = `agent/packages/crewloom/computer-use`, `MU` = `agent/packages/crewloom/mobile-use`, `DOC` = `core/Brain/computer-use-program`. All paths are relative to the workspace root `/Volumes/data/projects/crewloom`.
- Commands that say "from `agent/`" run in `/Volumes/data/projects/crewloom/agent`.
- **Gate** = a command plus the result that must appear. Paste the real output (trimmed) into `--evidence`.
- **Typecheck rule (from the WP-00 baseline):** `pnpm run typecheck` and `pnpm run lint` in `agent/` are already red before our work (`TS6307` "not listed within tsconfig.host.json" for the existing crewloom packages, and 1179 lint errors). So the gate for a package is: (a) the package's own check `pnpm exec tsc -p packages/crewloom/<pkg>/tsconfig.json --noEmit` prints nothing, and (b) the aggregate `pnpm run typecheck` shows no error line that mentions a file you created. Lint: `pnpm exec oxlint <your paths>` style output must contain no error for your files (use the repo's runner `tsx scripts/run-oxlint.ts <your paths>` if the direct form is not available). Do not fix pre-existing errors and do not edit `tsconfig.host.json`; if a new package must be listed there, checkpoint and ask the person.
- Test files are not covered by the package `tsconfig.json` (`include` is `src`); vitest does not type-check. Keep test code strictly typed anyway.
- If a gate fails, fix once. If it fails again for the same cause, `block` the package with the output and stop. Do not try a third approach.
- `[DECISION]` marks a choice already made for you. Do not reopen it unless a gate proves it wrong.
- Hardware-gated (`hw`) packages need a real machine of that OS. If you do not have one, leave them `todo`; do not simulate their results.

Linear order for a single agent (skip hardware-gated and optional ones, return to them when hardware exists): WP-00, 01, 02, 03, 10, 11, 12, 13, 14, 15, 20, 30, 31, 32, 33, 40, 50, 52, 51, then 04, 05, 06, 21, 23, 41, 34, 25, 35, 42, 22/24 (only if activated), and WP-60 last, only on the person's explicit authorization.

---

### WP-00 Recon and baseline
**Hat:** SDET. **Reviewer hat:** staff architect.
**Goal:** Record the real state of the code before anything changes, so later gates compare against facts.
**Creates:** `DOC/BASELINE.md`.
**Steps:**
1. Read `AGENTS.md`, `CONSTITUTION.md`, `agent/AGENTS.md`, `agent/packages/crewloom/ARCHITECTURE.md`, and [SYSTEM-DESIGN.md](SYSTEM-DESIGN.md).
2. From `agent/`, record the output of: `pnpm run typecheck`, `pnpm run lint`, and `pnpm exec vitest run packages/experimental/cua packages/crewloom` (note failures that exist before your work; do not fix them).
3. Record: how `@crewloom/plugin-skills` is built (does a `tsdown.config.*` exist at the package or repository level, what `entry` it uses); the include patterns for tests in `agent/vitest.config.ts` and whether `packages/crewloom/*/tests/*.spec.ts` is matched; the import-extension style used inside `packages/crewloom/contracts/src` and `skills/src`; the shape of `skills/locale/*.json` and who loads it; where the desktop app keeps its i18n dictionaries (`agent/apps/crewloom-desktop/src/lib`).
4. Read `experimental/cua/src/protocol.ts` and `experimental/cua-macos/native/protocol.schema.json` and list the 20 method names (they are: getCapabilities, listApps, findApps, getApp, activate, show, listWindows, getState, hover, click, setValue, selectText, performSecondaryAction, typeText, paste, pressKey, scroll, drag, screenshot, launchApp). Note any difference.
5. Record `uname -a`, `sw_vers`, `node --version`, `pnpm --version`, `python3 --version`, and which of these exist: `adb`, `xcrun simctl`, `swift`, `cargo`.
6. Resolve the open questions in SYSTEM-DESIGN section 16 that this package can answer; edit that section in place.
**Gates:** `DOC/BASELINE.md` exists and has a section for each of steps 2 to 5; `python3 core/scripts/program_ledger.py check` prints `ledger ok`.
**If stuck:** record what you could not determine as `UNKNOWN: <what>` in BASELINE.md. Never guess.

### WP-01 Desktop and mobile contracts
**Hat:** staff architect. **Reviewer hat:** security engineer.
**Goal:** Pure types and ports from SYSTEM-DESIGN section 5, plus tests.
**Creates/edits:** `A/contracts/src/computer-use.ts`, `A/contracts/src/mobile-use.ts`, `A/contracts/src/index.ts` (add two `export *` lines using the import-extension style recorded in BASELINE.md), `A/contracts/tests/computer-use.spec.ts`.
**Steps:**
1. Implement section 5 verbatim in `computer-use.ts`: all types, plus `DesktopAction` (discriminated on `kind`) and exported helper `assertNever(x: never): never` only if `contracts` does not already export one (search first; reuse it if it does).
2. In `mobile-use.ts` define `MobileAction`, `DeviceInfo { id, name, platform: 'android' | 'ios', kind: 'physical' | 'emulator' | 'simulator', osVersion, authorized: boolean }`, `Gesture` helpers as plain data types (no behavior), and `DeviceSessionState = 'discovered' | 'authorized' | 'connected' | 'busy' | 'closed'` with a pure `nextDeviceState(state, event)` transition function (events: `authorize`, `connect`, `begin`, `end`, `kill`, `disconnect`). Illegal transitions return `Result.fail`.
3. Write `computer-use.spec.ts`: exhaustive switch compiles for both unions (use a function with `assertNever`); `nextDeviceState` table test for every legal and every illegal pair; a test that a `FeatureStatus` with `support !== 'supported'` must have `reason` (provide `validateCapabilities(caps): Result<...>` as a pure function and test it).
4. No framework imports, no filesystem, no network, no `any`.
**Gates (from `agent/`):** `pnpm exec tsc -p packages/crewloom/contracts/tsconfig.json --noEmit` prints nothing; `pnpm run typecheck` shows no error line naming `computer-use.ts` or `mobile-use.ts` (pre-existing errors listed in BASELINE.md are ignored); `pnpm exec vitest run packages/crewloom/contracts` all pass (the 402 baseline tests across cua and crewloom must still pass: run `pnpm exec vitest run packages/experimental/cua packages/crewloom` and expect at least 402 passed, 0 failed); `grep -rn "any\b" packages/crewloom/contracts/src/computer-use.ts packages/crewloom/contracts/src/mobile-use.ts` prints nothing relevant (no type `any`).

### WP-02 Conformance harness
**Hat:** SDET. **Reviewer hat:** platform lead.
**Goal:** A reusable package that proves invariants I1 to I5, usable by every adapter and by CI.
**Creates:** package `A/computer-use-conformance` named `@crewloom/computer-use-conformance` (private), `DOC/CONFORMANCE.md` (empty matrix template).
**Steps:**
1. Scaffold the package by copying the file layout of `A/skills` (package.json, tsconfig.json) with name and dependencies adjusted (`@crewloom/contracts` only).
2. Define port `Probe<T> { name: string; read(): Promise<Result<T, ComputerUseError>> }` and implementations behind small per-OS modules chosen by `process.platform` in one factory: `FocusProbe` (frontmost app id), `PointerProbe` (pointer x,y). macOS: use `osascript`/AppKit through a spawned command; Windows and Linux probes may be written but are marked untested until WP-04/05 (`hw`). Return `UNSUPPORTED_ON_PLATFORM` when a probe is not implemented for the current OS, never a fake value.
3. Implement `runInvariantSuite(backend, fixture, probes)` that executes a fixed action list against a backend and returns a typed report `{ invariant: 'I1'|...; status: 'pass'|'fail'|'not-run'; detail }[]`. I4 compares `probe()` capabilities to real behavior per feature.
4. Implement `FakeBackend` (configurable results and delays) and use it to unit-test the suite: a backend that changes focus must fail I1; one that moves the pointer must fail I2; a feature marked supported that errors must fail I4; a backend that ignores abort must fail I5.
5. Write a CLI entry `conformance.ts` that prints the report as a Markdown table row set for `DOC/CONFORMANCE.md`.
**Gates (from `agent/`):** `pnpm run typecheck` clean for the package; `pnpm exec vitest run packages/crewloom/computer-use-conformance` passes, including the four negative cases in step 4.

### WP-03 Spike: Cua Driver and cua-macos on macOS
**Hat:** macOS platform lead. **Reviewer hat:** SDET.
**Goal:** Measure, on this macOS host, whether the existing `cua-macos` and `@trycua/cua-driver` satisfy I1 to I5, and decide which one the macOS adapter wraps.
**Creates:** `DOC/spikes/macos.md`.
**Steps:**
1. Check permissions (Accessibility, Screen Recording) for the host terminal/app; if missing, record `blocked: permission` and ask the person to grant, do not work around.
2. Run the existing package tests that do not need a display: `pnpm exec vitest run packages/experimental/cua packages/experimental/cua-macos` from `agent/`. Record results.
3. Use `WP-02` probes plus a fixture app (TextEdit via `open -a TextEdit`, and Chrome if present). Drive each backend through click, type, scroll, screenshot while another app is frontmost. Record I1 to I5 results for each backend in the matrix in `DOC/CONFORMANCE.md` (macOS rows).
4. Test the U4 and U8 claims (Electron accessibility tree; permission re-prompts) as far as this host allows; write `not verified` for the rest.
5. Write the recommendation: which backend, why, known gaps, with numbers and command output.
**Gates:** `DOC/spikes/macos.md` contains for each invariant a result or `not run` with a reason; no claim without command output.

### WP-04 Spike: Cua Driver on Windows (hw)
**Hat:** Windows platform lead. **Reviewer hat:** SDET. **Needs:** Windows 10 22H2 or 11 with a graphical session.
**Creates:** `DOC/spikes/windows.md`.
**Steps:** Implement the Windows probes in `computer-use-conformance` (focus: `GetForegroundWindow`; pointer: `GetCursorPos`), install the pinned `@trycua/cua-driver`, run the invariant suite against Notepad, Chrome, a classic Win32 app and an Electron app, at 100% and 150% display scaling, and test an elevated target for `TARGET_ELEVATED`. Verify U2 and U4. Record the matrix. If any of I1 to I4 fails for a class of apps, record exact evidence and call `activate WP-22` with the spike document as the reason.
**Gates:** the spike document exists with real results; matrix rows for Windows are filled.

### WP-05 Spike: Cua Driver on Linux (hw)
**Hat:** Linux platform lead. **Reviewer hat:** SDET. **Needs:** one X11 session and one Wayland session (GNOME), ideally also KDE.
**Creates:** `DOC/spikes/linux.md`.
**Steps:** Implement Linux probes (focus: `xdotool getactivewindow` on X11, compositor tooling or `not supported` on Wayland; pointer: `xdotool getmouselocation`). Run the suite against gedit or a GTK app, a Qt app, Chrome and an Electron app on each session. Verify U3 and U4. Record whether AT-SPI is reachable (`org.a11y.Bus`) and enabled. Where I1 to I4 fail, record evidence and call `activate WP-24`.
**Gates:** the spike document exists with real results; matrix rows for Linux are filled.

### WP-06 ADR-001 final decision
**Hat:** staff architect. **Reviewer hat:** security engineer.
**Creates:** `DOC/adr/ADR-001-adopt-vs-build.md`.
**Steps:** Read the three spike documents. For each OS write: decision (adopt, adopt with gaps, build), the evidence rows, the tier (A, B, C) it earns, and what it costs to keep (upstream pinning, license, maintenance). Confirm or change ADR-007. Update SYSTEM-DESIGN section 7 and 15 in place.
**Gates:** the ADR has one decision per OS and each cites a spike row; `python3 core/scripts/program_ledger.py check` prints `ledger ok`.

### WP-10 Plugin scaffold, registry, negotiation
**Hat:** staff architect. **Reviewer hat:** platform lead.
**Goal:** `@crewloom/plugin-computer-use` with the registry, the negotiator, and the null backend.
**Creates:** `CU/package.json`, `CU/tsconfig.json`, `CU/src/index.ts`, `CU/src/core/*`, stubs `CU/src/policy/index.ts`, `CU/src/audit/index.ts`, `CU/src/strategy/index.ts` (each only `export {}`; later packages own and fill them), `CU/README.md`. Edits `A/ARCHITECTURE.md` (add the package and its dependency arrows).
**Steps:**
1. Scaffold from `A/skills` layout. Dependencies: `@crewloom/contracts`, `@deepseek-ai/cordis` (as other packages do). Build with the same tool; if multiple entry points (`src/adapters/*/index.ts`) need configuration, add it per the BASELINE.md findings so adapters can be imported by subpath; otherwise export adapters through namespaced re-exports and record the choice in the README.
2. `core/registry.ts`: `BackendRegistry` with `register(platform, factory)` and `resolve(platform): ComputerBackend<DesktopAction>`; unknown platform returns `UnsupportedBackend`.
3. `core/unsupported-backend.ts`: null object returning `UNSUPPORTED_ON_PLATFORM` with the reason given at construction.
4. `core/negotiator.ts`: pure function `negotiate(capabilities, feature): Result<FeatureStatus, ComputerUseError>`; refuses `unsupported` features with the status reason and `requires`.
5. `core/detect-platform.ts`: pure mapping from `(process.platform, process.arch)` to `Platform`; throws nothing; unknown yields `UNSUPPORTED_ON_PLATFORM`.
6. Tests in `CU/tests/*.spec.ts` for every file above (registry resolution, null object, negotiation of supported, degraded, unsupported).
7. Update `A/ARCHITECTURE.md` in the same change: package graph arrows (plugin to contracts; preset to plugin) and responsibilities paragraph.
**Gates (from `agent/`):** per the typecheck rule at the top: `pnpm exec tsc -p packages/crewloom/computer-use/tsconfig.json --noEmit` prints nothing, no aggregate error line names your files, `pnpm exec vitest run packages/crewloom/computer-use` passes; also record whether `pnpm install` was needed; no file over about 400 lines; no function over about 60 lines.

### WP-11 PolicyGate
**Hat:** security engineer. **Reviewer hat:** staff architect.
**Creates:** `CU/src/policy/*` (replacing the stub), tests.
**Steps:**
1. Types (in this module, not contracts): `PolicyConfig { allow: readonly string[]; deny: readonly string[]; confirmVerbs: readonly string[]; defaultDecision: 'deny' | 'confirm' }`, `Decision = { kind: 'allow' } | { kind: 'deny'; reason } | { kind: 'confirm'; prompt }`.
2. Pure `decide(config, subject, action): Decision`. Deny wins over allow. Destructive verbs are taken from the action's accessible name or text when present. Default deny classes for mobile come from a typed constant list of bundle/package identifiers plus category tags; the list is data in `policy/default-denylist.ts`, one owner.
3. `withPolicy(backend, { config, confirm, killSwitch })`: decorator implementing `ComputerBackend<Action>`; on `confirm` call the injected async `confirm(prompt, signal)`; map deny to `POLICY_DENIED`, missing confirmation to `CONFIRMATION_REQUIRED`, engaged kill switch to `KILL_SWITCH_ENGAGED`. `KillSwitch` is a small class with `engage()`, `engaged`, and an `AbortSignal` that aborts all in-flight calls.
4. Tests: deny beats allow; default-deny subjects; confirm path accepted and rejected; kill switch aborts in-flight fake calls and blocks new ones.
**Gates:** `pnpm exec vitest run packages/crewloom/computer-use/tests/policy` passes; coverage of every `Decision` branch.

### WP-12 AuditTrail
**Hat:** security engineer. **Reviewer hat:** SDET.
**Creates:** `CU/src/audit/*`, tests.
**Steps:** `AuditEvent` discriminated union (`action.started`, `action.finished`, `action.refused`, `capability.probed`, `session.killed`); `redact(action)` that strips typed text and clipboard payloads to `{ length }` and never includes screenshot bytes; `withAudit(backend, sink)` decorator; `AuditSink` port (`emit(event)`), plus an in-memory sink for tests. Time comes from an injected clock.
**Gates:** tests prove redaction for `type`, `pasteText`, `setValue`, and screenshot results; a sink that throws does not change the action result (the failure is reported to a secondary error channel, not swallowed silently: provide `onSinkError`).

### WP-13 StrategyLadder
**Hat:** staff architect. **Reviewer hat:** platform lead.
**Creates:** `CU/src/strategy/*`, tests.
**Steps:** `Rung<Action>` interface `{ strategy: Strategy; applicable(caps, action): boolean; run(action, ctx): Promise<BackendResult<ActionOutcome>> }`; `StrategyLadder` runs applicable rungs in order, skips rungs the capabilities do not list, never runs `hardware-input` when `ctx.allowHardwareInput` is false, stops on success or on a non-degradable error (`POLICY_DENIED`, `CANCELLED`, `TIMEOUT`), and returns the first success with the rung used; if every rung fails it returns the most specific error. Pure; no OS code.
**Gates:** tests for each ordering rule, including that hardware rung is unreachable without consent and that the outcome's `strategy` equals the rung used.

### WP-14 Localised messages (Arabic and English)
**Hat:** technical writer and i18n. **Reviewer hat:** security engineer.
**Creates:** `CU/locale/ar.json`, `CU/locale/en.json` (plugin metadata only), `CU/src/messages/ar.ts`, `CU/src/messages/en.ts`, `CU/src/messages/index.ts`, tests.
**Steps:** [DECISION from WP-00, BASELINE.md section 6] `locale/{ar,en}.json` are loaded by the plugin manager and must stay flat with exactly the keys `name` and `description` (copy the shape of `A/skills/locale/*.json`). Domain messages do NOT go into those files: they live in the typed TypeScript modules `src/messages/ar.ts` and `en.ts` (`Record<ComputerUseErrorCode, string>` and `Record<Permission, string>`, so the compiler enforces completeness), exposed by a pure `messageFor(error, language)`. One message per `ComputerUseErrorCode` and per `Permission` (how to grant it, step by step) in both languages. `messageFor(error, language)` is a pure function. A test iterates every code and permission and fails if a key is missing in either language or if the two key sets differ. Keep paths, identifiers and flags in English inside Arabic text.
**Gates:** the completeness test passes; manual check that Arabic strings render right-to-left in the desktop settings view is a documented follow-up in WP-51, not claimed here.

### WP-15 Preset wiring
**Hat:** staff architect. **Reviewer hat:** SDET.
**Creates/edits:** `A/preset/src/computer-use.ts`, `A/preset/src/mobile-use.ts` (stub exporting an empty registration function; owned and filled by WP-30), `A/preset/src/index.ts` (two lines), `A/preset/package.json` (dependency on the plugin), `A/preset/tests/computer-use.spec.ts`.
**Steps:** Compose `withPolicy(withAudit(StrategyLadder over adapter))`. Resolve the adapter with `import()` by platform id (`@crewloom/plugin-computer-use/adapters/<id>`); on module-not-found register `UnsupportedBackend('adapter not installed')`. The feature is **off by default** and enabled by a validated config flag. Hardware input is off by default.
**Gates:** typecheck and lint clean; test that the disabled default registers nothing; test that a missing adapter yields `UNSUPPORTED_ON_PLATFORM` rather than throwing.

### WP-20 macOS adapter
**Hat:** macOS platform lead. **Reviewer hat:** SDET.
**Creates:** `CU/src/adapters/macos/*`, `CU/src/adapters/macos/README.md`, tests.
**Steps:** Wrap the backend chosen by WP-03 (anti-corruption layer): map `DesktopAction` to the upstream operations and back to `ActionOutcome` / `ComputerUseError`; map upstream error codes to `ComputerUseErrorCode` in one table; build `PlatformCapabilities` from upstream `getCapabilities` plus the real OS version. Do not import from `cua-macos` internals, only its public exports. Report `focusChanged` from the observed result, never assume.
**Gates:** unit tests with a fake upstream pass; run `runInvariantSuite` on this host and paste the macOS rows into `DOC/CONFORMANCE.md`; typecheck and lint clean.

### WP-21 Windows adapter (hw)
**Hat:** Windows platform lead. **Reviewer hat:** SDET. **Depends on the WP-04 result.**
**Creates:** `CU/src/adapters/windows/*`, README, tests.
**Steps:** Same anti-corruption approach as WP-20 over the Cua Driver win32 binary (or the helper if WP-22 was activated). Add `TARGET_ELEVATED` detection from the upstream error. Capabilities must say `virtualCursor: degraded` for exclusive-fullscreen. Run the conformance suite on a Windows host.
**Gates:** unit tests pass anywhere; the live suite results on Windows are pasted into `DOC/CONFORMANCE.md`.

### WP-22 Windows native helper (dormant, hw)
**Activate only if** WP-04 recorded a failed invariant that Cua Driver cannot fix. **Hat:** Windows platform lead.
**Creates:** `A/computer-use-helper-windows/` (Rust per ADR-007), JSONL protocol compatible with the adapter's anti-corruption layer. Required capabilities: UI Automation invoke/value/toggle/scroll, window capture, layered overlay, per-monitor DPI manifest, no foreground-changing calls. Specify and implement only the failing capability first.
**Gates:** the failing invariant now passes in the live suite on Windows; `cargo test` passes; the helper reports its version and refuses unknown protocol versions.

### WP-23 Linux adapter (hw)
**Hat:** Linux platform lead. **Reviewer hat:** SDET. **Depends on the WP-05 result.**
**Creates:** `CU/src/adapters/linux/*`, README, tests.
**Steps:** Anti-corruption layer over Cua Driver linux (or the helper if WP-24 was activated). Detect `XDG_SESSION_TYPE` at probe time and report `session: 'x11' | 'wayland'`. On GNOME Wayland report `virtualCursor: unsupported` with the reason and `backgroundClick` as `degraded` or `unsupported` according to the spike. Never fall through to hardware input.
**Gates:** unit tests pass anywhere; live results on each session type pasted into `DOC/CONFORMANCE.md`.

### WP-24 Linux AT-SPI helper (dormant, hw)
**Activate only if** WP-05 recorded a failed invariant. **Creates:** `A/computer-use-helper-linux/` (Rust per ADR-007) exposing AT-SPI `Action.DoAction`, `EditableText`, `Component` bounds, and enabling `org.a11y.Status.IsEnabled` only with consent. **Gates:** the failing invariant passes in the live suite; `cargo test` passes.

### WP-25 Linux isolated session (hw, optional)
**Hat:** Linux platform lead.
**Creates:** `CU/src/adapters/linux-isolated/*`, README, tests.
**Steps:** For applications the agent launches itself: start a private X display (`Xvfb` or `Xephyr`), run the application with `DISPLAY` set, drive it with XTEST inside that display only, capture from that display. Provide a `Session` object with explicit `start`/`stop`, process-group cleanup, and a watchdog. Report `isolatedSession: supported`, `session: 'x11'`. Refuse to attach to the user's display.
**Gates:** the suite passes I1 and I2 trivially because the user's display is untouched, and a test proves the user's `DISPLAY` is never used.

### WP-30 Mobile plugin scaffold
**Hat:** staff architect. **Reviewer hat:** security engineer.
**Creates:** `MU/package.json`, `tsconfig.json`, `src/index.ts`, `src/core/*` (`DeviceRegistry`, device session state holder using `nextDeviceState`, `UnsupportedDeviceBackend`), `MU/README.md`, replaces the stub `A/preset/src/mobile-use.ts` with real wiring.
**Steps:** Import `withPolicy`, `withAudit` from the desktop plugin's `policy`/`audit` modules (generic over `PolicySubject`); never import desktop adapters. Define the model-facing tool family `mobile.*` as data (name, JSON schema built from `MobileAction`) in one file; each tool maps to exactly one `MobileAction`. The wiring is off by default.
**Gates:** typecheck, lint, tests: registry resolution, illegal state transitions rejected, default-deny list applies to a banking package id.

### WP-31 Android ADB transport
**Hat:** Android platform lead. **Reviewer hat:** security engineer.
**Creates:** `MU/src/android/adb/*`, tests.
**Steps:** `AdbClient` over a spawned `adb` executable (path from validated config or `PATH`; never from tool output): `listDevices()` parsing `adb devices -l` including `unauthorized` and `offline`; `run(deviceId, args, { timeoutMs, signal })` with process-group kill on abort; `getProps(deviceId)` for API level and model. Map to `DEVICE_UNAUTHORIZED`, `DEVICE_NOT_FOUND`, `TIMEOUT`. Network (`tcpip`) connections require explicit consent; do not start them automatically. Tests use a fake `adb` script in a temp dir.
**Gates:** unit tests including malformed output, timeout, and abort; if `adb` exists on this host, run `listDevices` live and record the output (an empty list is a valid result).

### WP-32 Android UI state, gestures, screenshot
**Hat:** Android platform lead. **Reviewer hat:** SDET.
**Creates:** `MU/src/android/ui/*`, tests, fixtures.
**Steps:** Parse `uiautomator dump` XML to a typed tree (id, text, content-desc, class, bounds, clickable, enabled); tap/swipe/key through `adb shell input`; screenshot through `adb exec-out screencap -p`; detect a mostly black frame on a secure window and return `SECURE_SURFACE` only when the dump also marks the window secure or returns no nodes (never infer from black alone: report as a hint). Coordinate system: pixels of the current screenshot, documented.
**Gates:** parser tests on at least three recorded dump fixtures (Arabic text, nested scroll, empty); live run on an emulator or device when available (WP-34), else record `not run`.

### WP-33 Android Arabic and symbol text input
**Hat:** Android platform lead. **Reviewer hat:** technical writer and i18n.
**Creates:** `MU/src/android/text/*`, `MU/android-ime/` (only if the input-method route is chosen), tests.
**Steps:** [DECISION] First implement clipboard paste: set the clipboard through the Crewloom helper and send the paste key event; fall back to `input text` only for pure ASCII. Evaluate a minimal Crewloom input method only if clipboard paste fails on the test device; document the result. Verify Arabic with diacritics, mixed RTL/LTR, and emoji, reading the field value back through a fresh UI dump.
**Gates:** tests on the strategy selection (ASCII versus non-ASCII); live verification results recorded or `not run`.

### WP-34 Android emulator recipe (hw, optional) [SUPERSEDED: use the re-scoped WP-34 in the section "Android live runs on a dedicated emulator" at the end of this file]
**Creates:** `MU/ci/android/` with a script that creates a headless AVD (pinned system image id passed in, not hard-coded), boots it, waits for `sys.boot_completed`, and shuts it down. **Gates:** the script runs end to end on a machine with the Android SDK and the conformance subset for WP-32 passes against it.

### WP-35 Android virtual display feasibility (hw, optional) [SUPERSEDED: use the re-scoped WP-35 in the section "Android live runs on a dedicated emulator" at the end of this file]
**Creates:** `DOC/spikes/android-virtual-display.md`. **Steps:** On API 29+ and 33+ devices or emulators, test whether an app can be launched on a secondary display (U5), whether `input` can target it, whether screenshots of that display work, and which devices refuse. Verdict: feasible, device-dependent, or not feasible. **Gates:** results with commands and device models; no claim for devices not tried.

### WP-40 iOS Simulator adapter
**Hat:** iOS platform lead. **Reviewer hat:** SDET. **Runs on this macOS host.**
**Creates:** `MU/src/ios/simulator/*`, README, tests.
**Steps:** `SimctlClient` over `xcrun simctl` (list devices, boot, install, launch, screenshot, openurl); WebDriverAgent lifecycle (build/start through `xcodebuild test-without-building` is a documented manual prerequisite; do not auto-sign) and a minimal HTTP client for session, source (UI tree), tap, swipe, send keys; confirm U6 and record the exact endpoints you used. Map failures to typed errors. Report `isolatedSession: unsupported`, `virtualCursor: unsupported`.
**Gates:** unit tests with a fake `simctl` and fake WDA server; a live run on a booted simulator (the iOS Simulator tool in this app can attach for visual confirmation) performing launch, tree read, tap, screenshot, with outputs recorded.

### WP-41 iOS device adapter (hw)
**Hat:** iOS platform lead. **Needs:** an iPhone in developer mode, Xcode, a signing identity.
**Creates:** `MU/src/ios/device/*`, README, tests.
**Steps:** Record which connection tooling works for the iOS versions on hand (U6 plus the version-specific tunnel requirement); reuse the WDA client from WP-40; document signing expiry and the manual prerequisites. Refuse devices that are not trusted/paired (`DEVICE_UNAUTHORIZED`).
**Gates:** live run on a device with recorded outputs; unit tests pass anywhere.

### WP-42 iPhone Mirroring research (optional)
**Creates:** `DOC/spikes/iphone-mirroring.md`. **Steps:** On macOS 15 with iOS 18, test whether the mirroring window is visible to the Accessibility API and whether input from the macOS adapter is accepted (U7). **Gates:** verdict with evidence. No production code.

### WP-50 CI matrix
**Hat:** SRE and release. **Reviewer hat:** SDET.
**Creates:** `agent/.github/workflows/computer-use-conformance.yml`.
**Steps:** Follow the conventions of the existing workflows in `agent/.github/workflows/` (pinned actions, permissions). Jobs: unit and contract tests for the new packages on Linux; live conformance jobs on `macos-latest` and `windows-latest` marked allowed-to-fail until the suite is stable; Linux X11 job under `xvfb`; Android emulator job only if WP-34 is done. Print the conformance table into the job summary. Never grant write permissions the job does not need.
**Gates:** `actionlint` (if installed) or a YAML parse passes; the file contains no secrets; an explicit comment lists which cells cannot run in hosted CI (Wayland, physical devices).

### WP-51 Documentation and shared memory
**Hat:** technical writer and i18n. **Reviewer hat:** staff architect.
**Edits:** package READMEs (`CU`, `MU`, `CONF`), `core/Brain/COMPLETED.md`, `core/Brain/CHALLENGES.md`, `core/Brain/ARCHITECTURE.md` (one paragraph pointing to this programme), the Arabic overview `universal-computer-use-plan.md` (pointer only), `CONFORMANCE.md` tier table.
**Steps:** READMEs state: purpose, what is supported per tier (generated from `CONFORMANCE.md`, `not run` stays `not run`), permissions and how to grant them, safety defaults, how to run the conformance suite. Add dated entries to Brain files in the existing format (Artifact, Impact, Evidence / Cause, Solution, Status). Arabic and English both for any user-facing doc. Verify a right-to-left rendering of Arabic messages in the desktop app or mark it as a stated follow-up.
**Gates:** `python3 core/scripts/check_repository.py` (from `core/`) passes or its failures are unrelated and recorded; links in the new docs resolve (check with a script or by listing each target).

### WP-52 Security review and threat model
**Hat:** security engineer. **Reviewer hat:** staff architect.
**Creates:** `DOC/security/THREAT-MODEL.md`.
**Steps:** For each asset (screen content, input channel, device, clipboard, audit log) list threats from SYSTEM-DESIGN section 9 with likelihood, impact, mitigation in code (file and function), and residual risk. Re-read the code of WP-11, WP-12, WP-31, WP-40 against it. For every gap, add a new work package to `ledger.json` and a section here (never silently fix without a record). Check that pinned versions are exact and that helper paths cannot come from model output.
**Gates:** every mitigation points to a real file and test; gaps become packages.

### WP-60 Release (human gate)
**Needs:** the person's explicit authorization in chat. Do not start otherwise.
**Steps:** Follow the Mandatory Release Protocol in the root `AGENTS.md`: verification gate in each affected sub-project (`agent/`, `core/`), commits with conventional messages, `./scripts/release.sh agent <bump>` and `core`, post-release verification of tags and GitHub releases. Record the commands and output.
**Gates:** `gh release view <tag>` output for each release in `--evidence`. The root `AGENTS.md` (rule 7 and release step 5) also requires CI verification after every push with `gh run list --commit $(git rev-parse HEAD) --limit 5`, and for any failure `gh run view <run-id> --log-failed`; never scrape the web UI. Known context: CI for `agent` and `bridge` has failed because of account billing, not code (project memory); report the exact `gh` output and separate billing refusals from real failures.

---

## Review follow-ups (added 2026-10-26 after the independent review of WP-00 to WP-52)

These packages fix defects that the review found in finished packages. Finished packages stay `done`; after a follow-up changes their files, the follow-up's last step is `python3 scripts/program_ledger.py rebaseline <old WP> --agent <NAME> --reason "<this WP> <what changed>"` for each package whose owned files it touched. Facts below were verified by the reviewer on 2026-10-26 unless marked unverified.

### WP-53 CI workflow honesty and consistency
**Hat:** SRE and release. **Reviewer hat:** SDET. **Owns:** `agent/.github/workflows/computer-use-conformance.yml`.
**Verified defects:** (1) the step "Publish Conformance Summary" runs with `if: always()` and writes a fixed table that says `Passed` for Linux, macOS, Android and iOS whatever the jobs did; (2) both pnpm setup steps pass `version: 9.15.4` while `agent/package.json` declares `"packageManager": "pnpm@11.28.5"` (the repository's `ci.yml` calls `pnpm/action-setup` without `version`); (3) `actions/checkout` is pinned to a v4 SHA while the repository's workflows use `actions/checkout@v7.0.1`.
**Steps:** read `agent/.github/workflows/ci.yml` and one more existing workflow; (1) remove the hard-coded table; write the summary only from real data: the vitest result of that job (use a reporter output or `$?` captured in a variable) and `needs.<job>.result` values; a cell that did not run says `not run`; (2) remove `version:` so the action reads `packageManager`; (3) use the same checkout and action versions as `ci.yml`; (4) keep `permissions: contents: read`; (5) keep the header comment listing cells hosted CI cannot run.
**Gates:** `python3 -c "import yaml,sys;yaml.safe_load(open('agent/.github/workflows/computer-use-conformance.yml'))"` exits 0 (or an equivalent YAML parse, say which); `grep -n "Passed" agent/.github/workflows/computer-use-conformance.yml` shows no literal hard-coded status; `actionlint` output if installed, otherwise `unverified`. Rebaseline WP-50.

### WP-54 Adapter loading and package exports
**Hat:** staff architect. **Reviewer hat:** platform lead. **Owns:** `agent/packages/crewloom/computer-use/package.json`, `agent/packages/crewloom/preset/src/computer-use.ts`, `agent/packages/crewloom/preset/tests/computer-use.spec.ts`.
**Verified defects:** (1) `defaultAdapterLoader` in `preset/src/computer-use.ts` has `catch { return new UnsupportedBackend('adapter not installed') }`, so a syntax error, a missing dependency or a failing constructor inside a real adapter is reported as "not installed", which hides a broken state; (2) `package.json` export `./adapters/*` points its `default` at `./lib/types/adapters/*/index.js` (the declaration output directory); whether the real build emits there is unverified; (3) `pnpm --filter <pkg> build` (plain `tsdown`) fails for this package and for the existing `@crewloom/plugin-skills` with "No workspace packages found", so package-level `tsdown` is not the repository's build path; the path is `pnpm run build:artifacts` from `agent/`.
**Steps:** (1) read how `build:artifacts` builds `packages/crewloom/*` (`agent/scripts/build.ts`, `agent/tsdown.config.ts`) and find where `lib/` for `@crewloom/plugin-skills` is emitted; (2) set the `./adapters/*` export to the real emitted path, proven by `node --input-type=module -e "import('@crewloom/plugin-computer-use/adapters/macos').then(m=>console.log(Object.keys(m)))"` run from `agent/packages/crewloom/preset` after `pnpm run build:artifacts`; (3) in `defaultAdapterLoader` catch only the module-not-found error for that exact specifier (check `error.code === 'ERR_MODULE_NOT_FOUND'` and that the message names the specifier) and return `UnsupportedBackend` with the specifier in the reason; any other error is returned as a `Result.fail`-style `BACKEND_FAILURE` (loader signature may change to return `Promise<BackendResult<ComputerBackend<DesktopAction>>>`; update `applyComputerUse` and its callers and tests accordingly; a failed load must produce an `UnsupportedBackend` whose reason contains the original message, and must also be logged through `ctx.logger.warn`); (4) tests: a loader that throws a syntax-like error is NOT reported as "not installed"; a missing module is.
**Gates:** `pnpm run build:artifacts` exit 0 (paste the last lines); the `node` import command above prints the adapter's export names; `pnpm exec vitest run packages/crewloom/preset packages/crewloom/computer-use` passes; package-level `tsc -p` for both packages prints nothing. Rebaseline WP-10 and WP-15.

### WP-55 macOS adapter connected to the real Cua Driver
**Hat:** macOS platform lead. **Reviewer hat:** SDET. **Owns:** `agent/packages/crewloom/computer-use/src/adapters/macos`, `agent/packages/crewloom/computer-use/tests/adapters/macos`, `agent/packages/crewloom/computer-use/package.json` (dependency line only).
**Verified defects:** (1) `createBackend()` builds `new MacOSAdapter(options)` with no client, and no file in `agent/packages/crewloom` references `@trycua/cua-driver`; every adapter test uses a fake client, so the adapter has never driven the real driver; (2) in `adapter.ts` two `catch { return undefined }` blocks swallow focus-observer failures, so `focusChanged` can be reported without any observation; (3) the matrix row for `MacOSAdapter` in `CONFORMANCE.md` records PASS for TextEdit/Chrome but the spike document shows those runs used the driver directly, and its I1 PASS includes a case where the driver refused background input ("safe refusal"), which does not demonstrate that background input works.
**Steps:** (1) read `agent/packages/experimental/computer-use-cua-driver-native/src/index.ts` and `node_modules/@trycua/cua-driver` typings to learn how the SDK is created and which tools exist; do not copy upstream code; (2) add the dependency `@trycua/cua-driver` with the exact version `0.28.0` (no range) to `computer-use/package.json` and run `pnpm install` once from `agent/`, recording the output; the lockfile change is expected; (3) implement `createUpstreamMacClient()` in `adapters/macos/real-client.ts` that wraps the SDK behind the existing `UpstreamMacClient` interface (anti-corruption layer; no SDK types leak out); lazy import so unit tests and other platforms do not load the native addon; (4) make `createBackend()` use it, with the client created on first `probe`; a failure to load the addon returns `UNSUPPORTED_ON_PLATFORM` or `BACKEND_FAILURE` with the real message; (5) replace the two silent catches: when the focus cannot be observed, return the outcome with `focusChanged: false` ONLY if both before/after observations succeeded; otherwise return `BACKEND_FAILURE` with message `focus observation failed: <reason>`; add tests for both; (6) add a live test file `tests/adapters/macos/live.spec.ts` that is skipped unless `CREWLOOM_LIVE_MACOS=1` and, when enabled, runs click/type/screenshot through the adapter against TextEdit while another app is frontmost, and asserts focus and pointer probes did not change; run it on this Mac with Accessibility and Screen Recording granted and paste the output; if permissions are missing, STOP POINT S5; (7) correct the matrix row in `CONFORMANCE.md` from the live run: separate "action performed" from "action refused"; refused is not PASS for I1.
**Gates:** unit tests pass; the live test passes with `CREWLOOM_LIVE_MACOS=1` (paste output) or the package is blocked with the exact error; `grep -rn "catch {" agent/packages/crewloom/computer-use/src/adapters/macos` shows no silent return; package-level `tsc` clean. Rebaseline WP-20.

### WP-56 Threat model corrections
**Hat:** security engineer. **Reviewer hat:** staff architect. **Owns:** `core/Brain/computer-use-program/security/THREAT-MODEL.md`, `core/Brain/computer-use-program/security/verify-references.mjs`. **Depends on WP-55** so the pin it describes exists.
**Verified defects:** T-11 says upstream native dependencies are pinned in the plugin `package.json` files as `@trycua/cua-driver: 0.1.28`; the plugin `package.json` has no such dependency (until WP-55) and the real version is `0.28.0`. T-02 cites `SafetyPolicyEnforcer`; the repository's name is `ISafetyPolicyEnforcer` (an interface in `contracts`) implemented by `ZeroDestructionGuard` in `skills/src/guard.ts`, and it inspects shell commands, not UI actions. T-03 claims the deny list is "exhaustive" and the tenets mention "cryptographic" confirmation; neither is true of the code. WP-52's evidence said "29 paths exist and pass", but only existence was checked.
**Steps:** (1) write `verify-references.mjs` that parses every `path:Symbol` or `path` reference in the table and fails if the file does not exist or the symbol name does not occur in it; run it; (2) fix each wrong reference and claim (replace "exhaustive" with "default list, not complete; extendable by configuration"; remove "cryptographic"; state exactly what T-02 mitigation does); (3) add a section "Claims not mitigated in code" listing items that are only policy or manual; (4) re-read `policy/decide.ts`, `with-policy.ts`, `audit/redact.ts`, `mobile-use/src/android/adb/client.ts` and state in each audit paragraph the exact lines checked.
**Gates:** `node core/Brain/computer-use-program/security/verify-references.mjs` prints `all references ok` and its count; `python3 core/scripts/check_repository.py` passes (run in background). Rebaseline WP-52.

### WP-57 Conformance matrix provenance
**Hat:** SDET. **Reviewer hat:** security engineer. **Owns:** `core/Brain/computer-use-program/CONFORMANCE.md`. **Depends on WP-55.**
**Verified fact:** the conformance probes (`FocusProbe`, `PointerProbe`) are implemented for macOS; the matrix nevertheless records PASS for Android and iOS Simulator on I1, I2 and I5.
**Steps:** for every PASS cell write the command or test name that produced it in the notes column, or change the cell to `not run` / `n/a (no pointer on this platform)`. A cell backed only by a fake backend says `fake only`. Add a legend. Do not run new hardware work here.
**Gates:** every non-`not run` cell has a named test or command; `grep -c "PASS"` count matches the number of evidence entries; list the cells you changed.

### WP-58 Repository build gates for the new packages
**Hat:** SRE and release. **Reviewer hat:** staff architect. **Owns:** `core/Brain/computer-use-program/BUILD-CHECK.md`. **Depends on WP-54 and WP-55.**
**Verified fact:** `pnpm run typecheck` in `agent/` lists `TS6307` errors for files of `computer-use`, `mobile-use`, `computer-use-conformance` and `preset` because the new packages are not part of `tsconfig.host.json`; the same class of error already existed for `contracts` and `skills`. `agent/AGENTS.md` requires `build:artifacts` then `build:check` before claiming completion.
**Steps:** run `pnpm run build:artifacts` then `pnpm run build:check` from `agent/` (long; run in the background) and record the real results and which errors mention our files; do NOT edit `tsconfig.host.json` or any build configuration. If the only failures are `TS6307` for unlisted packages, write the exact list of files/entries that would be needed and STOP POINT S5: the person decides whether to register the packages.
**Gates:** `BUILD-CHECK.md` holds the two commands with exit codes and error counts split into "pre-existing" and "ours".

### WP-59 Honest failures in the real macOS client
**Hat:** macOS platform lead. **Reviewer hat:** security engineer. **Owns:** `agent/packages/crewloom/computer-use/src/adapters/macos`, `agent/packages/crewloom/computer-use/tests/adapters/macos`. **Depends on WP-55.**
**Verified defects (second review, 2026-10-26):** in `real-client.ts`: (1) the `catch (_error: unknown)` near line 55 returns a metadata object with the hard-coded `version: '0.28.0'` when the driver metadata call fails, so a version that was not observed is reported as observed; (2) the `catch (_err: unknown) { // best effort }` near line 104 silently continues without `pid`/`windowId` when the target-window lookup fails, so text may be typed into an unintended window; (3) the WP-55 evidence "`grep -rn 'catch {'` clean" passed only because the empty catches were rewritten as `catch (_err: unknown)`; the rule is "no silent failure", not "no `catch {` spelling"; (4) `tests/adapters/macos/live.spec.ts` has four `TS2339` errors under `tsc -p tsconfig.host.json` (strict access to `data` on a `Result` before narrowing).
**Steps:** re-check each defect with a command first (read the lines, run `pnpm run build:check` from `agent/` and filter for `live.spec.ts`). Fix: (1) when metadata fails return a result that says the version is unknown (extend the client type with `version: string | undefined`, and make `getCapabilities`/`probe` report `reason: 'driver version unknown: <message>'`), never a literal version; (2) a failed window lookup must stop the typing action with a typed `BACKEND_FAILURE` (`target window lookup failed: <reason>`); if the lookup is genuinely optional in the driver API, show that from the SDK typings and keep the failure visible through the outcome instead of ignoring it; (3) disposal errors may stay non-fatal but must be reported through an injected `onDisposeError` callback or a logger, not dropped; (4) add unit tests for each of (1) to (3) using the existing fake client; (5) narrow the `Result` before reading `.data` in `live.spec.ts`.
**Gates:** `grep -rnE "catch *(\([^)]*\))? *\{" agent/packages/crewloom/computer-use/src/adapters/macos` and for EACH match you state in the checkpoint what the block does with the error (rethrow, typed result, logged); no block may contain only a comment; unit tests pass; `pnpm run build:check` output contains no `live.spec.ts` error; the live test passes again with `CREWLOOM_LIVE_MACOS=1` (it launches TextEdit and types text on this Mac: run it once, and tell the person before running). Rebaseline WP-20 and WP-55.

### WP-61 Test typing errors and honest classification
**Hat:** SDET. **Reviewer hat:** staff architect. **Owns:** `agent/packages/crewloom/computer-use/tests/policy/policy-gate.spec.ts`, `agent/packages/crewloom/mobile-use/tests/core/policy.spec.ts`, `agent/packages/crewloom/mobile-use/tests/ios/simulator/wda.spec.ts`, `core/Brain/computer-use-program/BUILD-CHECK.md`, `core/Brain/computer-use-program/CONFORMANCE.md`. **Depends on WP-58 and WP-59.**
**Verified defects:** (1) `BUILD-CHECK.md` says "the only failures are TS6307" but its own table lists real type errors in our test files: `TS6133` unused variable `action` in `policy-gate.spec.ts`, `TS2322` in `mobile-use/tests/core/policy.spec.ts`, `TS2379` (exact optional property types) in `wda.spec.ts`; the text calling them artifacts of "missing package options" is an unverified assumption; package-level `tsc` does not check tests (`include` is `src`), so those errors were invisible to the gates; (2) `BUILD-CHECK.md` section 3.1 lists `packages/crewloom/contracts/src/computer-use.ts` under "pre-existing" errors, but that file was created by this programme; (3) `CONFORMANCE.md` legend says PASS means verified against a real driver, system or active emulator/device, yet the Android I4 and I5 cells and the iOS I4 and I5 cells cite unit-test files (`tools.spec.ts`, `client.spec.ts`, `simctl.spec.ts`, `wda.spec.ts`) that use fake `adb`/`simctl`/WDA; (4) RESOLVED by the reviewer on 2026-10-26: the person authorized registering the packages; eight `references` were added to `agent/tsconfig.host.json` and `TS6307` dropped from 85 to 0 (see `BUILD-CHECK.md` section 7). Do not touch `tsconfig.host.json` again; fix section 5 of `BUILD-CHECK.md` so it states the registration was applied and keeps the old snippet only as history.
**Steps:** (1) fix the three test typing errors minimally (no behavior change, no `any`, no `as unknown as`), prove with `pnpm run build:check` output filtered for those files; (2) correct `BUILD-CHECK.md`: reclassify counts by checking each file against `git log --diff-filter=A` or the ledger (our files vs old files), state the real number of non-TS6307 errors before and after, and label the registration snippet "proposed, not tried"; (3) in `CONFORMANCE.md` use `fake only (<test>)` for any cell backed by a fake `adb`/`simctl`/WDA and keep `PASS` only for cells run against the real emulator, simulator or device; if a live Android or iOS run exists in the ledger evidence, cite it, otherwise leave `fake only`; (4) update the legend to match.
**Gates:** `pnpm run build:check` from `agent/` (background): zero errors whose path is one of the three test files or `live.spec.ts`; the only remaining errors are the 9 old ones in `contracts/tests/personalization*.spec.ts` (8 `TS2532`, 1 `TS2345`), which you must NOT fix; counts in `BUILD-CHECK.md` equal a recount from that output (show the command); every PASS cell cites a real-environment run. Rebaseline WP-11, WP-40, WP-57, WP-58 as needed.

---

## Android live runs on a dedicated emulator (added 2026-10-26)

Verified by the reviewer before writing these packages: (1) the three existing files `agent/packages/crewloom/mobile-use/tests/android/{adb,text,ui}/live.spec.ts` pick the FIRST attached device in state `device` and run on it; the text test types `crewloom_test` and pastes `كروولوم` (it overwrites the device clipboard), the UI test dumps the screen; when `adb` or a device is missing they pass with `expect(true).toBe(true)`, so a plain `pnpm exec vitest run packages/crewloom` counts them as passed whether or not anything was verified; (2) on 2026-10-26 the only attached device (`emulator-5554`) had a user app (`com.primocys.chat`) in the foreground, and two user AVDs exist (`Chix_Isolated_QA`, `Flutter_Pixel_API_35_CLEAN_TEST`). **Never run input, clipboard or text actions against `emulator-5554`, against any AVD that is not named `crewloom-conformance-*`, or against a physical device.** Read-only `adb devices -l` is allowed.

### WP-62 Make Android live tests safe and non-vacuous
**Hat:** SDET. **Reviewer hat:** security engineer. **Owns:** `agent/packages/crewloom/mobile-use/tests/android/adb/live.spec.ts`, `agent/packages/crewloom/mobile-use/tests/android/text/live.spec.ts`, `agent/packages/crewloom/mobile-use/tests/android/ui/live.spec.ts`, `agent/packages/crewloom/mobile-use/tests/android/live-support.ts`.
**Steps:** (1) re-verify the defect with commands (read the three files; run `adb devices -l`; do NOT run any live test yet). (2) Create `live-support.ts` exporting `liveAndroidSerial()` that returns the serial from env `CREWLOOM_LIVE_ANDROID_SERIAL` and `undefined` otherwise, and refuses (throws a typed error with a clear message) a serial that is not an emulator whose AVD name starts with `crewloom-conformance-` (query with `adb -s <serial> emu avd name`); physical devices are always refused. (3) In each live spec use `describe.skipIf(!serial)` so that without the env variable the tests are reported as SKIPPED, never passed; delete every `expect(true).toBe(true)` shortcut; use the serial from the environment, never `devices.find(d => d.state === 'device')`. (4) The text live test must first launch a stock editable field in the target emulator only (not any user app), type into it, and read the value back through a fresh UI dump; assert the value, not just `success`. (5) Unit-test `liveAndroidSerial()` with a fake adb: unset env, physical device, wrong AVD name, right AVD name.
**Gates:** with the variable UNSET, `pnpm exec vitest run packages/crewloom/mobile-use` shows the three live files as skipped (paste the counts) and `adb` receives no input command (state how you know: for example run the suite with `PATH` pointing to a wrapper script that logs every adb call to a file, then show the log contains no `shell input`, `keyevent`, `settings`, `cmd clipboard` or `am start` line); package-level `tsc` clean; `pnpm run build:check` shows no new error. Rebaseline WP-31, WP-32, WP-33.

### WP-34 Android emulator recipe (re-scoped, now doable on this machine)
**Depends on WP-32 and WP-62. Owns:** `agent/packages/crewloom/mobile-use/ci/android`.
**Steps:** create `ci/android/emulator.sh` with subcommands `create`, `start`, `wait`, `stop`, `status` that (a) NEVER touches an existing AVD: `create` refuses if the name does not start with `crewloom-conformance-`; (b) takes the system image package id as an argument (find installed ones with `sdkmanager --list_installed` from `~/Library/Android/sdk/cmdline-tools/*/bin`; do not download anything without telling the person); (c) starts the emulator headless on an explicit port (`-port 5580`, so the serial is `emulator-5580`) with `-no-window -no-audio -no-snapshot-save`, as a background process whose pid is stored in a state file; (d) `wait` polls `sys.boot_completed` with a deadline; (e) `stop` kills only that serial with `adb -s emulator-5580 emu kill` and removes the state file; (f) prints the serial on stdout. Add a README with the exact commands. Use `set -euo pipefail`; no `sudo`; no global installs.
**Gates:** `shellcheck` output if installed (else say `unverified`); `emulator.sh create`, `start`, `wait`, `status`, `stop` run end to end and their real output is pasted; `adb devices -l` before and after shows `emulator-5554` untouched and `emulator-5580` gone after `stop`; `~/Library/Android/sdk/emulator/emulator -list-avds` shows the two user AVDs unchanged.

### WP-35 Android virtual display feasibility (now doable on this machine)
**Depends on WP-34. Owns:** `core/Brain/computer-use-program/spikes/android-virtual-display.md`.
**Steps:** boot the dedicated emulator with WP-34, record `getprop ro.build.version.sdk` and the model, then test, only on `emulator-5580`: whether a secondary display can be created (document the exact commands you tried, including `settings put global overlay_display_devices` and `dumpsys display`), whether `am start --display <id>` launches a stock app on it, whether `input -d <id>` targets it, whether `screencap -d <id>` captures it. Verdict: feasible / device-dependent / not feasible, per step, with real output. Stop the emulator afterwards. No claim for devices you did not try.
**Gates:** the document lists every command with its real output and ends with the verdict table; the user emulator is untouched.

### WP-63 Android live conformance and matrix update
**Hat:** SDET. **Reviewer hat:** staff architect. **Depends on WP-34 and WP-62. Owns:** `core/Brain/computer-use-program/CONFORMANCE.md`, `agent/packages/crewloom/computer-use-conformance/src/probes/android-focus.ts`, `agent/packages/crewloom/computer-use-conformance/tests/android-focus.spec.ts`, `agent/packages/crewloom/mobile-use/tests/android/live-conformance.spec.ts`.
**Steps:** (1) add an `AndroidFocusProbe` (reads the focused window from `adb -s <serial> shell dumpsys window` `mCurrentFocus`) to the conformance package behind the existing `Probe` port, unit-tested with recorded `dumpsys` output including a malformed one (typed error, no guess). (2) `live-conformance.spec.ts` (skipped unless `CREWLOOM_LIVE_ANDROID_SERIAL` names a `crewloom-conformance-*` emulator, same guard as WP-62) runs, on a stock app of that emulator: UI tree read, screenshot, tap on a known node, swipe, Arabic and ASCII text into an editable field verified by a fresh UI dump, a secure-surface check if the image has one (otherwise `not run`), cancellation (abort a long `adb` call and show the process is gone), and the focus probe before and after each action. (3) Update only the Android rows of `CONFORMANCE.md`: a cell is `PASS (<spec>:<test name>)` only for a test that ran in this session against the dedicated emulator; the live results from that run are pasted into the notes column; cells you did not run stay `not run` or `n/a (no pointer on this platform)`; keep `fake only` for unit-test-backed cells. (4) Stop the emulator at the end.
**Gates:** the live spec passes with `CREWLOOM_LIVE_ANDROID_SERIAL=emulator-5580` (paste the output) and is skipped without it; `pnpm exec vitest run packages/crewloom` with the variable unset shows 0 adb input calls (wrapper log as in WP-62); every `PASS` in the Android rows cites a test that ran. Rebaseline WP-02 and WP-61.
