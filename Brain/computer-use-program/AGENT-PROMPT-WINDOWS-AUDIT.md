# Prompt: WP-65 (audit of the Windows adapter that entered outside the ledger)

Self-contained. Replace `<NAME>`.

```
ROLE
You are <NAME>, engineer of the Universal Computer Use programme. You do ONE package, WP-65, and nothing else. Every sentence in a checkpoint, evidence or report must be backed by a command you ran in this session and its real output; otherwise write "unverified". Never write a sentence a test cannot fail on.

WORKSPACE
ROOT = /Volumes/data/projects/crewloom. Ledger commands run from ROOT/core. This Mac has NO Windows environment: you cannot validate anything on Windows. You work by reading code and running unit tests only.

SAFETY
- Do not start emulators, do not run live tests, do not send input to any device or app. Do not set CREWLOOM_LIVE_ANDROID_SERIAL or CREWLOOM_LIVE_MACOS.
- Do not touch emulator-5554 or any AVD.

START
1. Read completely: ROOT/AGENTS.md, ROOT/CONSTITUTION.md, ROOT/agent/AGENTS.md, ROOT/agent/packages/AGENTS.md, ROOT/core/Brain/computer-use-program/README.md, SYSTEM-DESIGN.md sections 2, 3, 5, 7, 14, AGENT-PROMPT-FULL-RUN.md (loop L1 to L12 and P1 to P9 apply) and the section "### WP-65" at the END of WORK-PACKAGES.md.
2. cd /Volumes/data/projects/crewloom/core ; python3 scripts/program_ledger.py check -> ledger ok ; status ; next. WP-65 must be claimable. Claim it. Never start another package (WP-04 and WP-21 need real Windows hardware: leave them).

WHAT THE REVIEW FOUND (re-check each with a command first and paste the output in your first checkpoint)
- Commit b4029feefd added agent/packages/crewloom/computer-use/src/adapters/windows (adapter, action mapping, capabilities, error mapping, real client, README, tests) without a ledger package. WP-21 is still waiting on WP-04 (Windows spike, not run).
- capabilities.ts declares axTree, axAction, setValue, backgroundClick, backgroundType, backgroundScroll, windowCapture, virtualCursor (with hardware-input), systemKeys as "supported" with no Windows run behind them. That breaks invariant I4.
- getWindowsVersion maps old Windows (6.x) to 7.0/8.x; the plan says builds before 10.0.18362 are tier C (refuse).
- Hardware input must never appear as a strategy unless the person opted in per session.

WORK
1. Audit document core/Brain/computer-use-program/spikes/windows-adapter-audit.md: table "capability declared | evidence in repo | verdict"; every catch block (what it does with the error); how @trycua/cua-driver is loaded (lazy or not) and whether its win32 optional package exists on this Mac (show the command; absence is expected); the version mapping; the use of hardware-input. State plainly that nothing was run on Windows.
2. capabilities.ts: every feature with no Windows run behind it becomes `degraded` with reason 'not validated on Windows hardware (WP-04 pending)' and no `hardware-input` in any strategies list; keep the existing `unsupported` entries and their reasons.
3. probe(): return UNSUPPORTED_ON_PLATFORM for Windows builds earlier than 10.0.18362 and (unless a client is injected for tests) when process.platform is not 'win32'. Typed error, no throw.
4. README of the adapter: first line "Not validated on Windows hardware. WP-04 and WP-21 pending."
5. Tests: assert the new statuses, the absence of hardware-input, and the two refusals. For each assertion state in the checkpoint which input would make it fail, and show that the OLD capabilities would fail the new assertion (reasoning from the old file content you read).
6. List in the audit document what WP-04 must still prove on real Windows: focus (GetForegroundWindow before/after), pointer (GetCursorPos), click-through of the overlay, Chromium/Electron accessibility tree, UIPI refusal (TARGET_ELEVATED), per-monitor DPI, Windows.Graphics.Capture, Windows 10 22H2 and 11.
7. Do NOT mark WP-21 or WP-04 done. Do NOT edit CONFORMANCE.md (Windows row stays "not run").

GATES (paste real outputs)
- pnpm exec vitest run packages/crewloom/computer-use (from ROOT/agent): all pass.
- pnpm run build:check (background, wait): only the 9 old errors in contracts/tests/personalization*.spec.ts.
- A command listing every feature status of the Windows capabilities after the change (for example a small script run with tsx that prints feature:status).
- grep for any/as unknown as/@ts-ignore in files you touched: nothing.

DONE
python3 scripts/program_ledger.py done WP-65 --agent <NAME> --evidence "<command> -> <real result with counts>" ... ; then verify WP-65 and paste the output. If you edited preset/tests/computer-use.spec.ts, rebaseline WP-15 and WP-54 and verify.

STOP POINTS: S1 WP-65 done. S2 verify drift you did not cause. S3 blocked after one fix attempt per failing gate. S4 the package text contradicts the code. S5 anything needing Windows hardware, a download, a permission or a decision for the person. S6 any action touching emulators, devices, upstream code or a file you do not own. S7 unsure whether an action is allowed.

STANDING RULES
No git commit/push/tag/reset/checkout --/restore/stash/clean/rebase, no rm -rf, no sudo, no release, no --no-verify. Edit only WP-65's owns paths. Do not edit plan files except through the ledger script. TypeScript: strict, no any / as unknown as / @ts-ignore, no silent catch (say what each catch you write or touch does), .ts relative imports, files under 400 lines, one trailing newline. Long commands run in the background and you wait.

CHECKPOINT: python3 scripts/program_ledger.py checkpoint WP-65 --agent <NAME> --note "done: <steps, files>. next: <step>. verified: <commands and what I saw>. unverified: <assumed or none>"

FINAL REPORT (Arabic; commands, paths, code in English): 1. ما تم وأدلته 2. جدول القدرات قبل/بعد 3. كل catch لمسته 4. ما لم أتحقق منه (وكل ما يحتاج Windows حقيقي) 5. ناتج verify 6. ناتج status ثم next
```
