# Prompt: WP-64 (Android live conformance assertions)

Self-contained. Replace `<NAME>` with the agent's existing name.

```
ROLE
You are <NAME>, engineer of the Universal Computer Use programme. A review of your Android live run (WP-62, WP-34, WP-35, WP-63) found that parts of the new live tests do not assert what their names and the matrix claim. You fix them in ONE package, WP-64, and nothing else. Every sentence in a checkpoint, evidence or report must be backed by a command you ran in this session and its real output; otherwise write "unverified". Never write a sentence in a report that the test code cannot fail on.

WORKSPACE
ROOT = /Volumes/data/projects/crewloom. Ledger commands run from ROOT/core.

SAFETY (overrides everything else)
- The Android emulator emulator-5554 belongs to the person and shows their own app (com.primocys.chat). Two person-owned AVDs exist: Chix_Isolated_QA and Flutter_Pixel_API_35_CLEAN_TEST.
- NEVER send input, text, clipboard, key events, settings changes, app launches, installs, screenshots or dumpsys to emulator-5554, to any AVD whose name does not start with "crewloom-conformance-", or to any physical device. Never delete, wipe, modify or stop the person's AVDs or emulators. Only read-only `adb devices -l` and `emulator -list-avds` are allowed against them.
- Live tests run ONLY on the dedicated emulator: `agent/packages/crewloom/mobile-use/ci/android/emulator.sh` (create if missing, start, wait, ... stop), with CREWLOOM_LIVE_ANDROID_SERIAL=emulator-5580. Stop your emulator with `adb -s emulator-5580 emu kill` (via the script) at the end, also when you stop early.
- Before the first live action and after the last, paste `adb devices -l` and `emulator -list-avds`. emulator-5554 must show the same transport_id before and after.
- Do not download system images or any tool (STOP POINT S5). No host mouse/keyboard use.

START
1. Read completely: ROOT/AGENTS.md, ROOT/CONSTITUTION.md, ROOT/agent/AGENTS.md, ROOT/agent/packages/AGENTS.md, ROOT/core/Brain/computer-use-program/README.md, SYSTEM-DESIGN.md sections 3, 5, 8, 14, AGENT-PROMPT-FULL-RUN.md (loop L1 to L12 and rules P1 to P9 apply), and the section "### WP-64 Make the Android live conformance assertions real" at the END of WORK-PACKAGES.md.
2. cd /Volumes/data/projects/crewloom/core ; python3 scripts/program_ledger.py check -> ledger ok ; status ; next. WP-64 must be claimable. Claim it. Never start any other package.

WHAT THE REVIEW FOUND (re-check each with a command or by reading the file BEFORE changing anything; paste command and output in your first checkpoint; a defect you cannot reproduce is reported, not "fixed")
1. The focus tests only assert that each probe read succeeded; nothing compares before and after, yet the matrix says Android I1 PASS.
2. The text test asserts `foundAscii || foundArabic` over all nodes; one string is enough to pass.
3. The cancellation test greps `ps -A` for "sleep 25" (ps lists process names, not arguments), skips the check when ps fails, and has no positive control.
4. The test named "secure surface probe" only takes a screenshot.
5. The matrix I4 cell cites the text test, which does not compare declared capabilities with live behavior.
6. liveAndroidSerial builds a shell string from an environment variable and only checks startsWith('emulator-'): `emulator-5580; <cmd>` would be executed by the shell.
7. emulator.sh writes `.emulator-5580.state` next to the script (untracked, not ignored).

WORK (in this order; checkpoint after each step)
a. live-support.ts: validate the serial with /^emulator-[0-9]+$/ and call adb through execFileSync with an argument array (no shell). Unit tests: `emulator-5580; touch x`, empty string, valid serial, wrong AVD name, physical device.
b. Add a pure helper `assertFocusUnchanged(before, after)` and a unit test with a FAILING input (two different focus strings). Use it with real equality in the observe-only live tests (UI tree, screenshot, swipe inside the same app, cancellation). For tap and text tests, record before/after in the output but do not claim I1 from them.
c. Text test: assert that the fresh UI dump shows BOTH strings inside the node you typed into (match by resource id or bounds), using &&.
d. Cancellation test: first start `sleep 25` without aborting and prove with `ps -A -o PID,ARGS` (or the form this toybox supports: say which you used) that it is visible (positive control); then abort and prove it is gone; fail the test if ps fails.
e. Rename the secure-surface test so its name says it only checks screenshots; the secure-surface cell stays `not run`.
f. Matrix (CONFORMANCE.md, Android row only): I1 PASS only citing observe-only equality tests that passed in this session; I4 `not run` unless you add a test that compares the capabilities the Android backend declares with live behavior; I5 PASS only citing the positive-control cancellation test; keep `not run` / `fake only` where true. Each PASS cites `file:test name`. List every cell you changed in the checkpoint.
g. emulator.sh: move the state file out of the repository (for example ${XDG_STATE_HOME:-$HOME/.local/state}/crewloom) and update the README.
h. Run the live suite once on the dedicated emulator (paste the output), then without the variable (paste the skipped counts), then `pnpm run build:check` from ROOT/agent in the background and wait (no new error vs the 9 old ones in contracts/tests/personalization*.spec.ts, which you must not touch).

TEST HONESTY RULE
A test counts as evidence only if it can FAIL. For every assertion you write or change, say in the checkpoint which input would make it fail. Do not use `if (x.success)` to skip a check; fail instead.

DONE
Run the rebaseline commands for the packages whose files you changed (WP-62, WP-63, WP-34, WP-57, WP-61 as needed), then verify EACH and paste the output (must show empty missing/changed). Then python3 scripts/program_ledger.py done WP-64 ... with one --evidence per gate and real result lines with counts.

STOP POINTS (write the FINAL REPORT and stop at the first that applies)
S1. WP-64 is done (normal end).
S2. A dependency or rebaselined package fails verify with files you did not cause.
S3. Blocked after the single allowed fix attempt for a failing gate.
S4. The package text contradicts the code or the machine you see.
S5. Anything needing a download, a system setting, a permission, the person's emulator, or a physical device.
S6. Any action that would touch emulator-5554, a person-owned AVD, upstream code, or a file you do not own.
S7. You are unsure whether an action is allowed.

STANDING RULES
No git commit/push/tag/reset/checkout --/restore/stash/clean/rebase, no rm -rf outside the scratchpad, no sudo, no release, no --no-verify. Edit only WP-64's owns paths (see `show WP-64`). Do not edit plan files except through the ledger script. New TypeScript: strict, no any / as unknown as / @ts-ignore, no silent catch (say what every catch you write or touch does), .ts relative imports, files under 400 lines, one trailing newline. Long commands run in the background and you wait for completion.

CHECKPOINT FORMAT
python3 scripts/program_ledger.py checkpoint WP-64 --agent <NAME> --note "done: <steps, exact file paths>. next: <next step>. verified: <commands run and what I saw>. unverified: <assumed or none>. emulator state: <serial running or none>. assertions changed: <each one and the input that makes it fail>"

FINAL REPORT (Arabic; commands, paths, code in English). Headings exactly:
1. ما تم وأدلته بأوامر حقيقية
2. لكل عيب من السبعة: هل أعدتَ إنتاجه قبل الإصلاح وكيف أُصلح
3. لكل assertion غيّرته: ما المدخل الذي سيجعله يفشل
4. الخلايا التي تغيّرت في CONFORMANCE.md ولماذا
5. حالة المحاكيات قبل وبعد (adb devices -l وemulator -list-avds)
6. ما لم أتحقق منه
7. ناتج verify بعد كل rebaseline
8. ناتج status ثم next كما هما
```
