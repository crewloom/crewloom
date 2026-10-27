# Windows Computer Use Adapter Audit (WP-65)

## 1. Executive Summary & Host Context

- **Host Environment:** macOS (`darwin-arm64`, Darwin 24.1.0).
- **Physical Hardware:** Apple Silicon Mac. **There is NO Windows environment or Windows hardware attached.**
- **Empirical Principle:** In accordance with the Universal Computer Use programme specification and Invariant I4 (Truthful Capabilities), **unverified means not supported**. No live commands or tests have ever been executed against a real Windows OS in this repository.
- **Commit Under Audit:**
  ```text
  commit b4029feefd07a2aedcfa9a4c12803703ab668c61
  Author: elbayoumi
  Date:   Sun Oct 26 16:31:00 2026 +0300
  feat(windows): configure native desktop headroom, cli process discovery, and computer-use adapter
  ```
- **Ledger Status Violation:** Commit `b4029feefd` introduced `agent/packages/crewloom/computer-use/src/adapters/windows` and unit tests without a backing ledger work package. `WP-21` ("Windows adapter") is still in state `waiting-deps` on `WP-04` ("Windows hardware spike").

---

## 2. Capability Audit Table

The table below contrasts the capability declarations introduced in commit `b4029feefd` against the empirical evidence available in this repository, establishing the audited verdict under WP-65.

| Feature ID | Declared in Commit `b4029feefd` | Empirical Evidence in Repo | Audited Verdict (WP-65) | Rationalization & Invariant |
|---|---|---|---|---|
| `axTree` | `supported` (`accessibility`) | None. Tested solely against mock client in `adapter.spec.ts`. | **`degraded`** | `not validated on Windows hardware (WP-04 pending)`. Invariant I4. |
| `axAction` | `supported` (`accessibility`) | None. Tested solely against mock client. | **`degraded`** | `not validated on Windows hardware (WP-04 pending)`. Invariant I4. |
| `setValue` | `supported` (`accessibility`) | None. Tested solely against mock client. | **`degraded`** | `not validated on Windows hardware (WP-04 pending)`. Invariant I4. |
| `backgroundClick` | `supported` (`targeted-input`) | None. No Windows window manager testing. | **`degraded`** | `not validated on Windows hardware (WP-04 pending)`. Invariant I1/I4. |
| `backgroundType` | `supported` (`targeted-input`) | None. No Windows window manager testing. | **`degraded`** | `not validated on Windows hardware (WP-04 pending)`. Invariant I1/I4. |
| `backgroundScroll` | `supported` (`targeted-input`) | None. No Windows window manager testing. | **`degraded`** | `not validated on Windows hardware (WP-04 pending)`. Invariant I1/I4. |
| `windowCapture` | `supported` (`targeted-input`) | None. No `Windows.Graphics.Capture` testing. | **`degraded`** | `not validated on Windows hardware (WP-04 pending)`. Invariant I4. |
| `virtualCursor` | `supported` (`targeted-input`, `hardware-input`) | None. Violation of hardware input invariant. | **`degraded`** | `not validated on Windows hardware (WP-04 pending)`. `hardware-input` stripped from strategies. |
| `systemKeys` | `supported` (`targeted-input`) | None. No Windows keyboard hook testing. | **`degraded`** | `not validated on Windows hardware (WP-04 pending)`. Invariant I4. |
| `isolatedSession` | `unsupported` | Desktop Win32 session architecture documented. | **`unsupported`** | Kept: `Windows standard desktop session does not provide isolated nested display sessions`. |
| `gestures` | `unsupported` | Desktop Win32 mouse/keyboard driver documented. | **`unsupported`** | Kept: `Touch gestures not supported on Windows desktop backend`. |
| `rotation` | `unsupported` | Desktop display orientation fixed. | **`unsupported`** | Kept: `Desktop display orientation is fixed`. |

---

## 3. Hardware Input & Invariant I2 Audit

In commit `b4029feefd`, `capabilities.ts` listed:
```typescript
virtualCursor: {
  support: 'supported',
  strategies: ['targeted-input', 'hardware-input'],
}
```
**Defect:**
Under the Universal Computer Use constitution and Invariant I2 (No Hardware Cursor Move), hardware cursor displacement is strictly prohibited unless explicitly opted in by the user on a per-session basis via `allowHardwareInput: true`. Declaring `hardware-input` as an unconditional general capability strategy breaks Invariant I2 and misleads planning negotiators.

**Remediation:**
`hardware-input` is removed from all default `strategies` arrays in `capabilities.ts`.

---

## 4. Native Runtime Binary Audit (`@trycua/cua-driver`)

The Windows adapter architecture relies on `@trycua/cua-driver` v0.28.0 as its upstream native driver client.

### Empirical Host Package Check
```bash
find /Volumes/data/projects/crewloom/agent/node_modules/.pnpm -name "*win32*" 2>/dev/null | grep -i cua
# Exit code: 1 (no files found)

find /Volumes/data/projects/crewloom/agent/node_modules -name "*cua-driver*" 2>/dev/null
# Output:
# .../agent/node_modules/.pnpm/@trycua+cua-driver-darwin-arm64@0.28.0/...
# .../agent/node_modules/.pnpm/@trycua+cua-driver@0.28.0/...
```

### Finding
The optional native package `@trycua/cua-driver-win32-x64-msvc` does NOT exist in `node_modules` on this host. While dynamic imports in `real-client.ts` (`const { CuaDriver } = await import('@trycua/cua-driver')`) succeed at finding the JS wrapper, any attempt to instantiate native bindings on a non-Windows platform or without the platform-specific native binary installed will fail.

### Lazy Loading Verification
`createWindowsAdapter` lazily delegates loading of `./real-client.ts` via dynamic `import('./real-client.ts')` only inside `clientFactory`. This allows unit testing and static analysis to run without loading missing native binaries when a mock client is supplied.

---

## 5. OS Version Mapping & Tier C Refusal Audit

In commit `b4029feefd`, `capabilities.ts` implemented:
```typescript
export function getWindowsVersion(): string {
  const rel = release()
  const parts = rel.split('.')
  const major = Number.parseInt(parts[0] ?? '10', 10)
  const build = Number.parseInt(parts[2] ?? '0', 10)
  if (major === 10) {
    if (build >= 22000) return '11.0'
    return '10.0'
  }
  if (major === 6) {
    if (parts[1] === '3') return '8.1'
    if (parts[1] === '2') return '8.0'
    if (parts[1] === '1') return '7.0'
  }
  return rel
}
```

### Defect
The programme specification states that Windows releases prior to Windows 10 Build 18362 (Version 1903, May 2019 Update) lack modern accessibility trees, per-monitor DPI v2 awareness, and the `Windows.Graphics.Capture` API. Windows 7, 8, and 8.1 (NT 6.1, 6.2, 6.3) are classified as Tier C legacy platforms.
Instead of mapping NT 6.x to `'7.0'` / `'8.1'` and allowing initialization to proceed, the adapter MUST refuse execution with `UNSUPPORTED_ON_PLATFORM`.

### Remediation
- Minimum supported Windows build is set to **`18362`**.
- Adapter `probe()` explicitly inspects the Windows build and returns `UNSUPPORTED_ON_PLATFORM` for builds below `18362`.
- Adapter `probe()` returns `UNSUPPORTED_ON_PLATFORM` when `process.platform !== 'win32'` unless a mock client was injected for testing.

---

## 6. Audit of Every `catch` Block

There are 10 `catch` sites in `agent/packages/crewloom/computer-use/src/adapters/windows/`:

| # | File & Line | Context | Caught Error | Handling & Invariant Audit |
|---|---|---|---|---|
| 1 | `adapter.ts:44` | `ensureClient()` | `err: unknown` | Wraps error into `Result.fail({ code: 'BACKEND_FAILURE' \| 'UNSUPPORTED_ON_PLATFORM', message })`. **Pass**: No error swallowed. |
| 2 | `adapter.ts:60` | `observeFocus()` | `err: unknown` | Wraps into `Result.fail(err.message)`. **Pass**: Propagated to caller. |
| 3 | `adapter.ts:68` | `observeFocus()` | `err: unknown` | Wraps into `Result.fail(err.message)`. **Pass**: Propagated to caller. |
| 4 | `adapter.ts:94` | `probe()` | `err: unknown` | Maps error using `mapUpstreamError` into typed `Result.fail`. **Pass**: Preserves error detail. |
| 5 | `adapter.ts:159` | `execute()` | `err: unknown` | Maps error using `mapUpstreamError` into typed `Result.fail`. **Pass**: Preserves error detail. |
| 6 | `adapter.ts:170` | `dispose()` | `disposeErr: unknown` | Invokes `onDisposeError` callback if provided, else logs warning. **Pass**: Resource teardown reporting. |
| 7 | `real-client.ts:131` | `getCapabilities()` | `error: unknown` | Sets `resolvedVersion = undefined`, returns reason in capability record. **Pass**: Reason preserved. |
| 8 | `real-client.ts:240` | `getFocusedApp()` | `err: unknown` | WP-65 replaced `catch { return undefined }` with a rethrow. WP-66: the catch now wraps only the PowerShell run; output that is not `<process>\t<hwnd>` throws from `parseForegroundWindow`. **Pass** (unit tests only). |
| 9 | `real-client.ts:253` | `dispose()` (`driver.shutdown()`) | `err: unknown` | **WP-65 rated this Pass; corrected by WP-66.** It called `options.onDisposeError?.(err)`, and `createWindowsAdapter` passes that callback only when the caller supplies one, so by default the error was dropped. Now `reportDisposeError` calls the callback or `console.warn`, as the macOS client does. |
| 10 | `real-client.ts:259` | `dispose()` (`driver.uniffiDestroy()`) | `err: unknown` | Same defect and same fix as row 9. |

### 6.1 WP-66: `getFocusedApp()` did not read the foreground window

WP-65 left `getFocusedApp()` running `Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle } | Select-Object -First 1`. That returns the first process with a titled window in `Get-Process` order, not the window with focus, so `focusChanged` in `adapter.ts` (invariant I1) compared values unrelated to focus. WP-66 replaced it with a PowerShell script that calls `GetForegroundWindow` and `GetWindowThreadProcessId` through `Add-Type`, passed with `-EncodedCommand`, and returns `<processName>#<hwnd>`, so a switch between two windows of one process is also a focus change.

Evidence on this Mac: `tests/adapters/windows/real-client.spec.ts` (8 tests) with an injected PowerShell runner; 6 of them failed against the WP-65 code and all 8 pass after the fix. `which pwsh powershell` found neither, so **the script itself has never run**. WP-04 must check that it compiles and returns the expected window, and measure whether `Add-Type` plus PowerShell start-up fits in the 2000 ms `FOCUS_QUERY_TIMEOUT_MS` (unmeasured; a timeout makes every `execute()` fail with `BACKEND_FAILURE`).

---

## 7. WP-04 Real Windows Hardware Spike Checklist

Packages `WP-04` ("Windows hardware spike") and `WP-21` ("Windows adapter") remain **NOT done** in the ledger. When a Windows machine is provisioned, `WP-04` must empirically prove the following:

1. **Invariant I1 (Focus Preservation):**
   - Probe foreground window using Win32 API `GetForegroundWindow` before and after dispatching targeted input to a background window.
   - Assert `focusChanged === false` empirically for background clicks and background typing.
   - Run the `getFocusedApp()` PowerShell script from WP-66 and confirm it returns the foreground window's process and handle within `FOCUS_QUERY_TIMEOUT_MS`.
2. **Invariant I2 (Hardware Pointer Stability):**
   - Query pointer coordinates using Win32 API `GetCursorPos` before and after targeted clicks and scrolls.
   - Assert physical cursor coordinate delta is exactly `(0, 0)`.
3. **Invariant I3 (Click-Through Overlay Window):**
   - Verify non-activating transparent overlay window with `WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_NOACTIVATE`.
   - Verify clicks pass through to targeted background controls without stealing focus.
4. **Chromium & Electron Accessibility Trees:**
   - Verify UIA accessibility tree queries on Chromium and Electron apps.
   - Test whether `--force-renderer-accessibility` is necessary for out-of-process renderer elements.
5. **UIPI (User Interface Privilege Isolation) Refusal:**
   - Execute targeted input against an elevated (`Run as administrator` / UAC) process from a standard integrity token.
   - Verify upstream runtime fails cleanly with `TARGET_ELEVATED` domain error without hanging or crashing.
6. **Per-Monitor DPI Scaling v2:**
   - Test on multi-monitor setup with mixed DPI scaling (e.g. 100%, 150%, 200%).
   - Verify coordinate mapping between DIPs (device-independent pixels) and physical screen pixels.
7. **`Windows.Graphics.Capture` Session:**
   - Test frame capture on Windows 10 (>= 22H2) and Windows 11.
   - Verify capture excludes overlay elements and does not produce screen border flashing.
