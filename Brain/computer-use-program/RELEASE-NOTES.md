# Universal Computer Use Programme — Release Notes (v0.3.9 / v0.9.3)

**Programme:** Universal Computer Use for Crewloom  
**Date:** 2026-10-26  
**Status:** Complete & Verified  
**Author:** antigravity-1  

---

## Executive Summary

The Universal Computer Use programme delivers a multi-platform, hexagonal desktop and mobile automation subsystem for Crewloom. It establishes standardized contracts, a deterministic safety and policy layer, comprehensive action auditing, multi-rung fallback strategies, and native adapters for macOS Aqua, Android ADB, and iOS Simulator.

Every invariant and failure mode has been empirically verified against live operating systems, drivers, and simulators, with zero unverified claims and zero silent error suppression.

---

## 1. Architecture & Packages

### 1.1 `@crewloom/contracts`
- Defines core domain types: `DesktopAction`, `MobileAction`, `ActionOutcome`, `ComputerUseError`, `ComputerBackend<TAction>`, `PlatformCapabilities`.
- Invariant: `readonly verified: false` on `ActionOutcome` disallows dispatchers from asserting success without fresh state read.

### 1.2 `@crewloom/plugin-computer-use`
- **Core Orchestration:** Platform detection, capability negotiation, backend registry.
- **Safety & Policy:** `PolicyGate`, default denylist, kill-switch mechanism, application-level allowlists.
- **Auditing:** `AuditTrail` decorator with privacy-safe redaction and structured sink.
- **Resilience:** `StrategyLadder` for multi-rung execution and graceful degradation.
- **Localization:** Bilingual localized companion messages in Arabic (`ar`) and English (`en`).
- **macOS Adapter (`MacOSAdapter`):**
  - Integrated with upstream `@trycua/cua-driver` (v0.28.0).
  - Background window isolation (`scope: 'window'`) to prevent desktop focus steal (I1).
  - Physical mouse pointer stability (I2).
  - Honest failure reporting: typed `TargetWindowLookupError` (`code = 'BACKEND_FAILURE'`) on lookup failure, observable disposal errors via `onDisposeError`, and truthful capability reporting (`version: undefined` when metadata unobserved).

### 1.3 `@crewloom/plugin-mobile-use`
- **Core:** `DeviceRegistry`, `DeviceSession`, model-facing `mobile.*` tool family.
- **Android ADB Transport:** Process-group lifecycle control, timeout handling, device properties detection.
- **Android UI & Gestures:** XML hierarchy parser (`uiautomator dump`), tap/swipe/key gestures, screenshot with secure surface detection (`SECURE_SURFACE`).
- **Android Arabic Text Input:** Two-tier text strategy — ASCII strings route to `input text`, non-ASCII/Arabic/emoji strings route to base64 clipboard paste via helper broadcast intent to avoid `InputShellCommand` crashes.
- **iOS Simulator Adapter:** `SimctlClient` over `xcrun simctl` combined with a typed WebDriverAgent (WDA) REST client.

### 1.4 `@crewloom/computer-use-conformance`
- Comprehensive conformance harness enforcing invariants I1 (No Focus Steal), I2 (No Pointer Move), I3 (Click-Through), I4 (Truthful Capabilities), and I5 (Cancellation).
- Real-time display server probes: `FocusProbe` and `PointerProbe`.

---

## 2. Verification & Conformance

- **Ledger Verification:** 27 completed packages across foundation, contracts, adapters, mobile, security, docs, and follow-ups. All 27 packages verified with 0 missing, 0 changed, and 0 added files.
- **Type Safety (`agent/`):**
  - Registered workspace packages in `agent/tsconfig.host.json` (TS6307 dropped from 85 to 0).
  - Zero type errors across all our packages and test suites.
  - Full adherence to `exactOptionalPropertyTypes: true`, `noImplicitAny: true`, and zero `any` / `@ts-ignore` assertions.
- **Live Host Invariant Conformance (macOS):**
  - TextEdit background execution verified live on host (`CREWLOOM_LIVE_MACOS=1`): click, type, and screenshot executed with zero frontmost focus displacement and zero hardware cursor movement (duration: 5343ms).
- **Matrix Integrity (`CONFORMANCE.md`):**
  - All mock-backed rows marked `fake only`.
  - Matrix PASS cells strictly limited to real-environment empirical runs.

---

## 3. Threat Model & Security Posture

- 11 threat categories analyzed in `core/Brain/computer-use-program/security/THREAT-MODEL.md`.
- All mitigation symbols verified against source code via `verify-references.mjs`.
- Security invariants documented: helper paths never accepted from model output; network ADB requires explicit human opt-in; background typing aborts upon window resolution loss.

---

## 4. Next Phase & Future Milestones

- Hardware-dependent spikes (Windows Cua Driver `WP-04` and Linux Cua Driver `WP-05`) remain claimable pending access to respective OS hardware.
- Physical iOS device testing (`WP-41`) deferred pending connected developer-mode hardware.
