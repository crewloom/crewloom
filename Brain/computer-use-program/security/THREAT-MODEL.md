# Universal Computer Use Threat Model · نموذج التهديدات الأمنية

Author: Security Engineer & Staff Architect  
Scope: Universal Computer Use Programme (Desktop & Mobile)  
Date: 2026-10-26  
Status: Active  

---

## 1. Executive Summary & Security Objectives

The Universal Computer Use programme enables autonomous and supervised AI agents to observe and interact with desktop environments (macOS, Windows, Linux) and mobile devices (Android, iOS). Because computer use grants synthetic perception and control capabilities, robust security controls are required to prevent unauthorized access, sensitive data exfiltration, confused deputy execution, and runaway automation.

### Core Security Tenets
1. **Consent First**: No observation or action occurs without verified explicit subject authorization.
2. **Default Deny for Sensitive Subjects**: High-risk applications (banking, payment systems, password managers, authenticators, system settings) are blocked by default via default denylists.
3. **Mandatory Human-in-the-Loop Confirmation**: Destructive verbs (`delete`, `send`, `purchase`, `uninstall`, `reset`) require interactive user confirmation through the registered confirmation handler.
4. **Instant Kill Switch**: Immediate global termination of in-flight operations with input release.
5. **Zero Data Retention of Secrets**: No raw credentials, keystroke text, or unredacted secrets in audit logs.
6. **Network Transport Protection**: Network ADB (`tcpip`) and remote tunnels require explicit separate consent.

---

## 2. Assets Catalog

| Asset ID | Asset Name | Description & Sensitivity |
|---|---|---|
| **A-01** | **Screen Content & Pixel Buffers** | Active desktop displays, window screenshots, UI tree hierarchies. High risk of containing PII, credentials, or confidential business data. |
| **A-02** | **Synthetic Input Channel** | Mouse clicks, taps, swipes, keystrokes, and hardware input injection mechanisms. High risk of arbitrary code execution or state alteration. |
| **A-03** | **Device & OS Management** | Host OS accessibility services, ADB transport daemons, Xcode simctl, WebDriverAgent sessions. |
| **A-04** | **System Clipboard** | Operating system and mobile device clipboard buffers. Frequently holds temporary passwords, 2FA codes, and copied tokens. |
| **A-05** | **Audit Trail & Telemetry** | Historical records of agent actions, error messages, and operational events. |

---

## 3. Comprehensive Threat Analysis Matrix

| Threat ID | Target Asset | Threat Description | Likelihood | Impact | Mitigation in Code (File & Function) | Residual Risk | Test Verification |
|---|---|---|---|---|---|---|---|
| **T-01** | A-01 | **Indirect Prompt Injection via Rendered Text**: Malicious instructions embedded in untrusted web pages, emails, or document UI attempting to hijack agent goals. | High | High | `agent/packages/crewloom/computer-use/src/policy/decide.ts:decide`<br>`agent/packages/crewloom/mobile-use/src/core/denylist.ts:isMobileDefaultDenied`<br>Actions bound to verified subject IDs; high-risk applications denied by default. Destructive actions trigger `CONFIRMATION_REQUIRED`. | Medium (Model reasoning can still be influenced, but action space is restricted by policy gate). | `agent/packages/crewloom/computer-use/tests/policy/policy-gate.spec.ts`<br>`agent/packages/crewloom/mobile-use/tests/core/policy.spec.ts` |
| **T-02** | A-01, A-02 | **Confused Deputy via Granted Application**: Agent interacts with an authorized browser or terminal that is subsequently navigated to a malicious endpoint or script. | Medium | High | `agent/packages/crewloom/computer-use/src/policy/with-policy.ts:PolicyGateBackend`<br>`agent/packages/crewloom/preset/src/computer-use.ts:composeComputerUsePipeline`<br>Destructive verbs require interactive prompt confirmation handled by `PolicyGateBackend`; shell command safety enforcement is independently handled by `IZeroDestructionGuard` (`ZeroDestructionGuard` in `agent/packages/crewloom/skills/src/guard.ts`) for command-line tools. | Low (Destructive execution paused for human approval). | `agent/packages/crewloom/computer-use/tests/policy/policy-gate.spec.ts` |
| **T-03** | A-01 | **Sensitive Financial & Credential Exposure**: Agent observing or manipulating banking apps, password vaults, or OTP authenticators. | High | Critical | `agent/packages/crewloom/mobile-use/src/core/denylist.ts:MOBILE_DEFAULT_DENYLIST`<br>`agent/packages/crewloom/mobile-use/src/core/denylist.ts:isMobileDefaultDenied`<br>Hardcoded default denylist of known banking, vault, authenticator, and settings package IDs, plus keyword heuristics (`bank`, `wallet`, `password`, `keychain`). Returns `POLICY_DENIED`. | Low (Default denylist, not complete; extendable by configuration. Unknown third-party apps outside heuristics require explicit user configuration). | `agent/packages/crewloom/mobile-use/tests/core/policy.spec.ts` |
| **T-04** | A-01 | **Bypassing Protected Window Privacy (DRM / FLAG_SECURE)**: Agent attempting to inspect secure mobile surfaces (e.g. login PIN pads). | Medium | High | `agent/packages/crewloom/mobile-use/src/android/ui/screenshot.ts:isMostlyBlackFrame`<br>`agent/packages/crewloom/mobile-use/src/android/ui/state.ts:getFullUiState`<br>Detects black frame coupled with empty accessibility tree; maps to typed `SECURE_SURFACE` error; never attempts bypass. | Low (Hardware and OS enforcement blocks pixel readout). | `agent/packages/crewloom/mobile-use/tests/android/ui/screenshot.spec.ts` |
| **T-05** | A-02 | **Hardware Pointer Hijacking**: Agent displacing or clicking the physical user pointer without explicit session opt-in, disrupting active human work. | High | Medium | `agent/packages/crewloom/computer-use/src/strategy/ladder.ts:StrategyLadder`<br>`agent/packages/crewloom/contracts/src/computer-use.ts:ExecutionContext`<br>Hardware cursor rung refused unless `allowHardwareInput: true`. Verified by Invariant I2 `PointerProbe`. | Very Low (Enforced in ladder selection). | `agent/packages/crewloom/computer-use/tests/strategy/ladder.spec.ts`<br>`agent/packages/crewloom/computer-use-conformance/tests/conformance.spec.ts` |
| **T-06** | A-02 | **Runaway Automation & Stuck Inputs**: Agent loop becomes unresponsive, keys or mouse buttons remain held down indefinitely. | Medium | High | `agent/packages/crewloom/computer-use/src/policy/kill-switch.ts:KillSwitch`<br>`agent/packages/crewloom/mobile-use/src/core/device-session.ts:DeviceSession`<br>Global kill switch engagement immediately aborts signals, transitions sessions to `closed`, and refuses future calls with `KILL_SWITCH_ENGAGED`. | Low (Signal abort propagated to process groups). | `agent/packages/crewloom/computer-use/tests/policy/policy-gate.spec.ts`<br>`agent/packages/crewloom/mobile-use/tests/core/session.spec.ts` |
| **T-07** | A-03 | **Unauthorized Network ADB Exposure**: Malicious remote actors connecting to insecure ADB TCP/IP ports or tools opening listening ports. | Medium | Critical | `agent/packages/crewloom/mobile-use/src/android/adb/client.ts:isTcpipTarget`<br>`agent/packages/crewloom/mobile-use/src/android/adb/client.ts:AdbClient`<br>Blocks network device targets (`ip:port`) and commands (`tcpip`, `connect`) unless `allowTcpip: true` is explicitly configured. | Low (Network connections rejected by default). | `agent/packages/crewloom/mobile-use/tests/android/adb/client.spec.ts` |
| **T-08** | A-03 | **Binary Path Hijacking & Tool Output Tampering**: Model or untrusted inputs supplying malicious executable paths for `adb` or `xcrun`. | Medium | Critical | `agent/packages/crewloom/mobile-use/src/android/adb/client.ts:AdbClient`<br>`agent/packages/crewloom/mobile-use/src/ios/simulator/simctl-client.ts:SimctlClient`<br>Executable paths sourced exclusively from validated configuration or system `PATH`; never accepted from model tool arguments. | Very Low (Input schemas strictly exclude executable path parameters). | `agent/packages/crewloom/mobile-use/tests/core/tools.spec.ts` |
| **T-09** | A-04 | **Clipboard Data Theft / Poisoning**: Sensitive passwords or keys in clipboard read or overwritten by untrusted text actions. | Medium | High | `agent/packages/crewloom/mobile-use/src/android/text/clipboard.ts:setAndroidClipboard`<br>`agent/packages/crewloom/mobile-use/src/android/text/strategy.ts:selectTextInputStrategy`<br>Clipboard paste used exclusively for text input injection via Base64; agent cannot read arbitrary historical clipboard items. | Low (Direct write followed by paste). | `agent/packages/crewloom/mobile-use/tests/android/text/input.spec.ts` |
| **T-10** | A-05 | **Credential Leakage in Telemetry & Audit Logs**: Typed passwords, API tokens, or session secrets stored in plaintext audit event sinks. | High | High | `agent/packages/crewloom/computer-use/src/audit/redact.ts:redact`<br>`agent/packages/crewloom/computer-use/src/audit/with-audit.ts:AuditDecoratorBackend`<br>Redacts all typed text (`[REDACTED_TEXT]`) and values from action payloads before emitting audit events. | Very Low (Pure redaction pass before event dispatch). | `agent/packages/crewloom/computer-use/tests/audit/audit.spec.ts` |
| **T-11** | All | **Native Supply Chain Tampering**: Compromised upstream dependencies injecting malicious native code. | Medium | Critical | `agent/packages/crewloom/computer-use/package.json`<br>Upstream native dependency pinned to exact version `@trycua/cua-driver: 0.28.0` in `agent/packages/crewloom/computer-use/package.json`. Pnpm lockfile supply-chain verification enforced. | Low (Frozen lockfile and automated audit scans). | `agent/pnpm-lock.yaml` |

---

## 4. Claims Not Mitigated in Code (Manual & Policy Controls)

The following security risks cannot be fully eliminated by application-layer TypeScript logic alone and require environmental, hardware, or human operational controls:

1. **Physical Device Tampering & Cable Interception**: A malicious actor with physical access to connected USB debugging cables or host ports can intercept ADB or syslog traffic. Mitigated by physical workstation access control.
2. **OS-Level Keyring and Secure Enclave Access**: Software-level sandboxes cannot prevent an authenticated host user from accessing Keychain or Windows Credential Manager if the user account is compromised.
3. **Physical Mobile Developer Mode Activation**: Enabling Developer Mode and trusting self-signed development certificates on physical iOS devices (WP-41) requires manual human operator interaction on the device touchscreen; this step cannot and should not be automated.
4. **Adversarial LLM Reasoning Jailbreaks**: Prompt injection defenses at the policy gate restrict the executable tool action space (denylists, confirmation gates), but cannot mathematically prevent model reasoning drift when processing adversarial untrusted text.
5. **Wayland Root Sandbox Absence**: On modern Linux Wayland desktop sessions without isolated X11 displays (WP-25), compositors do not provide fine-grained per-window synthetic input injection without portal prompts.

---

## 5. Code Audit & Line-by-Line Verification

### WP-11 (PolicyGate)
- **Files Checked**: `agent/packages/crewloom/computer-use/src/policy/decide.ts` (lines 20-74) and `agent/packages/crewloom/computer-use/src/policy/with-policy.ts` (lines 19-105).
- **Review Finding**: In `decide.ts` (lines 27-73), the five-step evaluation order strictly executes: (1) explicit config deny, (2) default denylist, (3) sensitive verb confirmation check, (4) allowlist match, (5) default fallback. In `with-policy.ts`, `PolicyGateBackend.execute` (lines 44-100) and `probe` (lines 29-41) check `this.options.killSwitch?.engaged` before executing and refuse fast with `KILL_SWITCH_ENGAGED`. Confirmation handlers require interactive prompt resolution (lines 66-94) and fail safely with `CONFIRMATION_REQUIRED` if unhandled.
- **Verdict**: Verified sound.

### WP-12 (AuditTrail)
- **Files Checked**: `agent/packages/crewloom/computer-use/src/audit/redact.ts` (lines 3-22) and `agent/packages/crewloom/computer-use/src/audit/with-audit.ts` (lines 17-64).
- **Review Finding**: In `redact.ts` (lines 9-19), screenshot byte payloads (`bytes`, `base64`, `screenshot`) are completely omitted from audit records, while sensitive user inputs (`text`, `value`, `payload`) are masked to `{ length: val.length }`. In `with-audit.ts`, `AuditDecoratorBackend.execute` (lines 28-59) records monotonically elapsed milliseconds via `performance.now()`, dispatches `ActionStartedEvent` and `ActionFinishedEvent` to the sink, and guarantees that only redacted copies enter event logs.
- **Verdict**: Verified sound.

### WP-31 (Android ADB Transport)
- **Files Checked**: `agent/packages/crewloom/mobile-use/src/android/adb/client.ts` (lines 46-74) and `agent/packages/crewloom/mobile-use/src/android/adb/process.ts` (lines 25-68).
- **Review Finding**: In `client.ts` (lines 51-64), network targets (`isTcpipTarget` matching `:`) and network arguments (`tcpip`, `connect`) are blocked with `POLICY_DENIED` unless `allowTcpip` is true. In `process.ts` (lines 48-65), child process lifecycle uses `detached: true` on Unix and kills the entire negative process group (`process.kill(-child.pid, 'SIGKILL')`) upon timeout or signal abort, preventing zombie background ADB daemons.
- **Verdict**: Verified sound.

### WP-40 (iOS Simulator Adapter)
- **Files Checked**: `agent/packages/crewloom/mobile-use/src/ios/simulator/simctl-client.ts` (lines 25-65) and `agent/packages/crewloom/mobile-use/src/ios/simulator/wda-client.ts` (lines 30-80).
- **Review Finding**: `SimctlClient` wraps `xcrun simctl` using safe argument arrays with process timeouts. `WdaClient` uses standard Node `fetch` with AbortController signal handling and typed JSON payloads. Capabilities truthfully declare `isolatedSession: unsupported` and `virtualCursor: unsupported`.
- **Verdict**: Verified sound.

### WP-55 (macOS Adapter with Cua Driver)
- **Files Checked**: `agent/packages/crewloom/computer-use/src/adapters/macos/real-client.ts` (lines 40-230) and `agent/packages/crewloom/computer-use/src/adapters/macos/adapter.ts` (lines 35-65, 80-140).
- **Review Finding**: `real-client.ts` wraps `@trycua/cua-driver` (v0.28.0) behind the `UpstreamMacClient` port. In `adapter.ts`, `observeFocus()` returns typed `Result<string | undefined, string>` and `execute()` fails with `BACKEND_FAILURE` (`focus observation failed: <reason>`) if focus observation fails before or after action execution. Conformance matrix in `CONFORMANCE.md` explicitly distinguishes between performed background actions and safe refusals.
- **Verdict**: Verified sound.

---

## 6. Residual Risks & Future Roadmap

1. **Wayland Display Sandboxing**: Wayland Linux compositors currently lack standard programmatic isolated window capture APIs without user-facing XDG Desktop Portal dialogs. Isolated sessions on Linux will require dedicated private X11/Xvfb displays (planned in optional WP-25).
2. **Physical Device Trust**: Physical iOS devices (WP-41) require manual Developer Mode activation and Apple Developer certificate trust, which must remain a manual human administrator task to prevent certificate abuse.
