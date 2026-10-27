# Universal Computer Use Conformance Matrix

This matrix records empirical verification of invariants I1 through I5 across desktop and mobile backends.

## Invariant Definitions
- **I1 (No Focus Steal):** Background actions do not alter frontmost application or window focus.
- **I2 (No Hardware Cursor Move):** Actions do not displace or click the physical hardware pointer without explicit opt-in.
- **I3 (Click-Through):** Agent overlay does not intercept or swallow user clicks.
- **I4 (Truthful Capabilities):** Declared supported capabilities succeed; unsupported operations return typed errors.
- **I5 (Cancellation):** Execution aborts promptly upon signal and releases all held input states.

## Conformance Matrix

| Platform | Backend | Fixture App / Device | I1 | I2 | I3 | I4 | I5 | Verified Date / Notes |
|---|---|---|---|---|---|---|---|---|
| macOS | FakeBackend | unit-fixture | fake only (packages/crewloom/computer-use-conformance/tests/conformance.spec.ts) | fake only (packages/crewloom/computer-use-conformance/tests/conformance.spec.ts) | not run | fake only (packages/crewloom/computer-use-conformance/tests/conformance.spec.ts) | fake only (packages/crewloom/computer-use-conformance/tests/conformance.spec.ts) | 2026-10-25 (WP-02: in-memory contract harness verification) |
| macOS | cua-macos | TextEdit / Chrome | PASS (core/Brain/computer-use-program/spikes/macos.md) | FAIL (core/Brain/computer-use-program/spikes/macos.md) | not run | PASS (core/Brain/computer-use-program/spikes/macos.md) | PASS (core/Brain/computer-use-program/spikes/macos.md) | 2026-10-25 (WP-03 spike: I2 fails on scroll pointer displacement) |
| macOS | Cua Driver darwin | TextEdit / Chrome | PASS (core/Brain/computer-use-program/spikes/macos.md) | PASS (core/Brain/computer-use-program/spikes/macos.md) | not run | PASS (core/Brain/computer-use-program/spikes/macos.md) | PASS (core/Brain/computer-use-program/spikes/macos.md) | 2026-10-25 (WP-03 spike: recommended backend for WP-20) |
| macOS | MacOSAdapter | TextEdit | PASS (packages/crewloom/computer-use/tests/adapters/macos/live.spec.ts) | PASS (packages/crewloom/computer-use/tests/adapters/macos/live.spec.ts) | not run | fake only (packages/crewloom/computer-use/tests/adapters/macos/adapter.spec.ts) | fake only (packages/crewloom/computer-use/tests/adapters/macos/adapter.spec.ts) | 2026-10-26 (WP-55/WP-59: real Cua Driver 0.28.0; live host background focus preservation & pointer stability) |
| Windows | Cua Driver win32 | Notepad / Chrome | not run | not run | not run | not run | not run | Pending WP-04 spike (hw) |
| Linux X11 | Cua Driver linux | gedit / Chrome | not run | not run | not run | not run | not run | Pending WP-05 spike (hw) |
| Linux Wayland | Cua Driver linux | gedit / Chrome | not run | not run | not run | not run | not run | Pending WP-05 spike (hw) |
| Android | AdbClient + UI | Android 15 Emulator | PASS (packages/crewloom/mobile-use/tests/android/live-conformance.spec.ts:verifies observe-only UI tree dump with real focus equality) | n/a (no pointer on this platform) | not run | not run | PASS (packages/crewloom/mobile-use/tests/android/live-conformance.spec.ts:verifies cancellation aborts active call with positive control and leaves no orphan process) | 2026-10-26 (WP-64: empirical verification on emulator-5580 API 35 ARM64; I1 verified via assertFocusUnchanged in observe-only tests; I2 n/a no pointer; I3 not run; I4 not run; I5 verified via positive-control cancellation in ps -A -o PID,ARGS) |
| iOS | Simulator | iPhone 17 Pro Sim | not run | n/a (no pointer on this platform) | not run | fake only (packages/crewloom/mobile-use/tests/ios/simulator/simctl.spec.ts) | fake only (packages/crewloom/mobile-use/tests/ios/simulator/wda.spec.ts) | 2026-10-26 (WP-40: FocusProbe not supported on iOS Simulator; touch surface; simctl capabilities and WDA cancellation tested via unit mocks) |
| iOS | Device | MobileSafari | not run | not run | not run | not run | not run | Pending WP-41 (hw) |

## Legend
- **`PASS (<test/evidence>)`**: Empirically verified against a real driver, operating system, or active emulator/device; satisfies the invariant with zero observed violations. The exact test file or spike evidence document is cited in parentheses.
- **`FAIL (<test/evidence>)`**: Empirically verified against a real driver/environment; violates the invariant during execution. The citation specifies the observed regression or violation cause.
- **`fake only (<test-file>)`**: Verified in-memory against a mock/fake test fixture (such as `FakeBackend`, mock HTTP server, or fake CLI binaries); verifies harness contract mechanisms, but does not provide empirical evidence of invariant compliance on an actual display server, real device, or active OS session.
- **`n/a (no pointer on this platform)`**: Invariant does not apply because the platform lacks a physical mouse/pointer (e.g. touch/gesture mobile surfaces on Android and iOS).
- **`not run`**: No empirical verification has been executed for this invariant on this backend/platform yet (e.g. pending hardware spike, or probe unavailable on platform).
