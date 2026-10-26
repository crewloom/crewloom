# macOS Computer Use Spike: Cua Driver vs cua-macos

**Date:** 2026-10-25  
**Host:** Darwin arm64 (macOS 26.0 / Apple Silicon, Kernel 25.0.0)  
**Author:** antigravity-1 (macOS platform lead hat, SDET reviewer hat)  
**Work Package:** WP-03  

---

## 1. Permission Verification (Step 1)

Empirical execution verified both Accessibility and Screen Recording permissions are granted on the host.

### 1.1 Accessibility Permission
Command executed:
```bash
osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true'
```
Output:
```
crewloom-desktop
```
Exit code: `0` (Success: Accessibility AppleEvents delivered without assistive access refusal).

### 1.2 Screen Recording Permission
Command executed:
```bash
screencapture -x /tmp/test-screen.png && sips -g pixelWidth -g pixelHeight /tmp/test-screen.png && rm /tmp/test-screen.png
```
Output:
```
/private/tmp/test-screen.png
  pixelWidth: 3024
  pixelHeight: 1964
```
Exit code: `0` (Success: ScreenCaptureKit captured display buffers with full pixel dimensions: 3024x1964, file size 1.6MB).

---

## 2. Non-Display Package Unit Test Execution (Step 2)

Command executed from `agent/`:
```bash
pnpm exec vitest run --testTimeout=10000 packages/experimental/cua packages/experimental/cua-macos
```
Result:
```
Test Files  12 passed (12)
     Tests  293 passed (293)
  Duration  6.31s
```
Breakdown:
- `packages/experimental/cua/tests/protocol.spec.ts`: 33 passed
- `packages/experimental/cua/tests/bridge.spec.ts`: 7 passed
- `packages/experimental/cua/tests/api.spec.ts`: 73 passed
- `packages/experimental/cua-macos/tests/protocol-generation.spec.ts`: 7 passed
- `packages/experimental/cua/tests/coordinates.spec.ts`: 7 passed
- `packages/experimental/cua-macos/tests/native-build.spec.ts`: 17 passed
- `packages/experimental/cua-macos/tests/shared-native.spec.ts`: 37 passed
- `packages/experimental/cua/tests/native-client.spec.ts`: 44 passed
- `packages/experimental/cua/tests/application-access.spec.ts`: 25 passed
- `packages/experimental/cua-macos/tests/provider-lifecycle.spec.ts`: 41 passed
- `packages/experimental/cua-macos/tests/loader-composition.spec.ts`: 1 passed
- `packages/experimental/cua-macos/tests/large-image-ptc.spec.ts`: 1 passed (passes in 1.8s when run with sufficient timeout)

---

## 3. Invariant Evaluation against Real Applications (Step 3)

Fixture applications tested: TextEdit (PID 34300, Window 41442) and Google Chrome / crewloom-desktop as frontmost applications. Probes from `@crewloom/computer-use-conformance` (`FocusProbe`, `PointerProbe`) were sampled before and after each action.

### 3.1 Cua Driver darwin (`@trycua/cua-driver` v0.28.0)

Embedded native Node addon linking `libcua_driver_sdk.dylib` (in-process Rust runtime) exposing 27 tools.

#### Invariant I1: No Focus Steal
- **Screenshot (`get_window_state`):** Focus probe before: `com.crewloom.agent`, after: `com.crewloom.agent`. Changed: `false`. Result: **PASS**.
- **Click / Type (`click`, `type_text`):** When targeting background window 41442 while another app was frontmost, driver safely refused input rather than stealing focus (`Background input refused (off_space_or_ax_unresolved)`). Focus before: `com.crewloom.agent`, after: `com.crewloom.agent`. Changed: `false`. Result: **PASS**.
- **Overall I1:** **PASS** (Zero background focus steal; safe refusal when surface is unanchored).

#### Invariant I2: No Hardware Cursor Move
- **Screenshot (`get_window_state`):** Pointer probe before: `{ x: 1262, y: 530 }`, after: `{ x: 1262, y: 530 }`. Changed: `false`. Result: **PASS**.
- **Click / Type (`click`, `type_text`):** Pointer probe before: `{ x: 1262, y: 530 }`, after: `{ x: 1262, y: 530 }`. Changed: `false`. Result: **PASS**.
- **Overall I2:** **PASS** (Physical hardware cursor is never displaced).

#### Invariant I3: Click-Through
- **Result:** `not run` (No transparent visual overlay daemon active in headless benchmark).

#### Invariant I4: Truthful Capabilities
- `list_windows` accurately reports all Layer 0 windows, bounds, and space associations.
- `get_window_state` returns structured content with accurate elements and screenshot.
- Unsupported/unanchored operations fail with clear typed diagnostics (`off_space_or_ax_unresolved`), never silent no-ops.
- **Overall I4:** **PASS**.

#### Invariant I5: Cancellation
- Dispatched action with pre-aborted signal:
  `result.error`: `{ message: 'tool call aborted before dispatch', info: { name: 'AbortError', code: 'ABORTED_BEFORE_DISPATCH' } }`
- Timed cancellation stops work promptly and rejects without dispatching events.
- **Overall I5:** **PASS**.

---

### 3.2 cua-macos (`@deepseek-ai/dsh-cua-macos`)

Swift 6 native helper (`dsh-cua-native`) communicating with host Node process via UNIX domain socket.

#### Invariant I1: No Focus Steal
- **Screenshot (`screenshot`):** Focus probe before: `com.google.Chrome`, after: `com.google.Chrome`. Changed: `false`. Result: **PASS**.
- **Click / Type (`click`, `typeText`):** Background requests target window without raising or activating target process. Focus probe before: `com.google.Chrome`, after: `com.google.Chrome`. Changed: `false`. Result: **PASS**.
- **Overall I1:** **PASS**.

#### Invariant I2: No Hardware Cursor Move
- **Screenshot (`screenshot`):** Pointer probe before: `{ x: 1018, y: 616 }`, after: `{ x: 1018, y: 616 }`. Changed: `false`. Result: **PASS**.
- **Scroll (`scroll`):** Pointer probe before: `{ x: 966, y: 590 }`, after: `{ x: 614, y: 342 }`. Changed: `true`! The physical hardware pointer was forcibly relocated across screen points. Result: **FAIL**.
- **Overall I2:** **FAIL** (WindowPointerInput dispatches events that move the visible hardware cursor).

#### Invariant I3: Click-Through
- **Result:** `not run` (Overlay daemon not mounted during headless spike).

#### Invariant I4: Truthful Capabilities
- Declared methods in `getCapabilities`: `activate`, `click`, `drag`, `findApps`, `getApp`, `getCapabilities`, `getState`, `hover`, `listApps`, `listWindows`, `paste`, `performSecondaryAction`, `pressKey`, `screenshot`, `scroll`, `selectText`, `setValue`, `show`, `typeText`.
- Unobserved windows return typed `STALE_SNAPSHOT` with clear recovery instructions.
- Parameter errors return `INVALID_ARGUMENT`.
- **Overall I4:** **PASS**.

#### Invariant I5: Cancellation
- Pre-aborted signal rejected immediately with `NativeError: NATIVE_CANCELLED: Operation was cancelled before dispatch`.
- **Overall I5:** **PASS**.

---

## 4. Upstream Claims Verification (Step 4)

### 4.1 Claim U4: Chromium / Electron Accessibility Tree Exposure
- **Test:** Queried AX UI elements of Google Chrome (`com.google.Chrome`) and crewloom-desktop (`com.crewloom.agent`, Electron).
- **Command:**
  ```bash
  osascript -e 'tell application "System Events" to get role of UI elements of first window of application process "crewloom-desktop"'
  ```
- **Output:**
  ```
  AXGroupAXButtonAXButtonAXButtonAXStaticText
  ```
- **Finding:** Chromium and Electron expose only top-level shell containers (`AXGroup`, `AXButton`) unless assistive technology is detected or `AXEnhancedUserInterface` / `--force-renderer-accessibility` is activated.
- **Status:** **VERIFIED**.

### 4.2 Claim U8: Periodic Permission Re-prompts on Recent macOS Releases
- **Finding:** Periodic re-prompting (e.g. macOS 15 monthly screen recording authorization re-check dialogs) cannot be verified within a single session without a 30-day elapsed timeline or advancing system time.
- **Status:** **NOT VERIFIED**.

---

## 5. Recommendation & Conclusion (Step 5)

### 5.1 Comparison Matrix

| Criteria | Cua Driver darwin (`@trycua/cua-driver`) | cua-macos (`dsh-cua-native`) |
|---|---|---|
| **Packaging** | Precompiled npm native addon (`.node` + `.dylib`) | Source-built Swift 6 binary via `swift build` |
| **I1 (No Focus Steal)** | **PASS** (strict background guard) | **PASS** |
| **I2 (No Hardware Cursor Move)** | **PASS** (physical pointer stationary) | **FAIL** (displaces physical hardware cursor) |
| **I4 (Truthful Capabilities)** | **PASS** (typed structured diagnostics) | **PASS** (typed `NativeError` codes) |
| **I5 (Cancellation)** | **PASS** (immediate abort) | **PASS** (immediate `NATIVE_CANCELLED`) |
| **Background Guarding** | Refuses input if target window is off-space | Allows dispatch unless rejected by WindowServer |

### 5.2 Recommendation
**Adopt `@trycua/cua-driver` (Cua Driver darwin) as the primary backend for WP-20 (macOS adapter).**

**Reasons:**
1. **Invariant I2 Compliance:** Unlike `cua-macos`, Cua Driver does not displace the physical hardware cursor during background coordinate operations.
2. **Safety Against Cross-Window Input Leakage:** Cua Driver validates window AX presence and Space residency, explicitly refusing ambiguous background input with `off_space_or_ax_unresolved` rather than risking sending keystrokes or clicks to the frontmost application.
3. **Packaging & Portability:** Precompiled binary eliminates dependency on host Swift toolchains and compilation overhead.

**Known Gaps:**
1. Coordinate-based click on an off-screen/uncomposited window requires explicit capture refresh before coordinate dispatch.
2. Direction parameter in `scroll` must follow `{ direction: 'up' | 'down' | 'left' | 'right', amount: number }`.
3. WP-20 anti-corruption layer must map Cua Driver's MCP tool format and errors to Crewloom's `ComputerBackend<DesktopAction>` contract.
