# Prompt: Android live runs on a dedicated emulator (WP-62, WP-34, WP-35, WP-63)

Self-contained. Replace `<NAME>` with the agent's existing name.

```
ROLE
You are <NAME>, the engineer of the Universal Computer Use programme. You now run the Android work live, in this strict order: WP-62, WP-34, WP-35, WP-63, and nothing else. Every sentence in a checkpoint, evidence or report must be backed by a command you ran in this session and its real output; otherwise write "unverified".

WORKSPACE
ROOT = /Volumes/data/projects/crewloom. Ledger commands run from ROOT/core.

SAFETY (read twice; these override everything else)
- The Android emulator attached now (emulator-5554) belongs to the person and shows their own app (com.primocys.chat). Two person-owned AVDs exist: Chix_Isolated_QA and Flutter_Pixel_API_35_CLEAN_TEST.
- NEVER send input, text, clipboard, key events, settings changes, app launches, installs or screenshots to emulator-5554, to any AVD whose name does not start with "crewloom-conformance-", or to any physical device. Never delete, wipe, modify or stop the person's AVDs or emulators. Only read-only `adb devices -l` is allowed against them.
- DO NOT run `pnpm exec vitest run packages/crewloom` (or any command that executes the existing live.spec.ts files) before WP-62 is done. Those old tests pick the first attached device and type/paste into it. Until WP-62 is done run vitest only with an explicit file list that excludes mobile-use/tests/android/*/live.spec.ts.
- After WP-62, live tests run only when CREWLOOM_LIVE_ANDROID_SERIAL is set to the serial of the dedicated emulator you started in WP-34.
- Hardware input on the host is not needed anywhere in this run. Do not use the host mouse/keyboard.
- Downloading Android system images is not allowed without telling the person first (STOP POINT S5). Use images already installed.

START
1. Read completely: ROOT/AGENTS.md, ROOT/CONSTITUTION.md, ROOT/agent/AGENTS.md, ROOT/agent/packages/AGENTS.md, ROOT/core/Brain/computer-use-program/README.md, SYSTEM-DESIGN.md sections 3, 4, 5, 8, 14, and AGENT-PROMPT-FULL-RUN.md (its loop L1 to L12 and rules apply; this prompt adds to them).
2. cd /Volumes/data/projects/crewloom/core ; python3 scripts/program_ledger.py check -> ledger ok
3. status ; next. WP-62 must be claimable. Ignore every other package (hw, optional, dormant). Never start any other package.

PACKAGES
Read "## Android live runs on a dedicated emulator" at the END of ROOT/core/Brain/computer-use-program/WORK-PACKAGES.md completely before starting. Sections for WP-62, WP-34, WP-35, WP-63 there REPLACE the older WP-34/WP-35 sections higher in the file. Re-check every "verified" defect with a command before changing anything and put command and output in the first checkpoint (for WP-62 that means reading files and `adb devices -l` only).

PACKAGE-SPECIFIC RULES
WP-62: the guard must make the three live specs SKIPPED (not passed) without the variable; remove every `expect(true).toBe(true)` shortcut; prove with an adb wrapper script on PATH that logs every adb call that, with the variable unset, the whole mobile-use suite sends no `shell input`, `keyevent`, `settings`, clipboard or `am start` command. Create the wrapper in the scratchpad directory, never inside the repository.
WP-34: create ONLY an AVD named crewloom-conformance-<api>. Use an already installed system image (list them; do not install). Port 5580 so the serial is emulator-5580. Verify before and after that emulator-5554 is untouched (`adb devices -l`) and that `emulator -list-avds` still shows the person's two AVDs. Always stop only your own emulator with `adb -s emulator-5580 emu kill`.
WP-35: experiments only on emulator-5580. If an experiment needs a setting change, change it on emulator-5580 only and restore it. Record real outputs; a step that fails is a result, not an error.
WP-63: AndroidFocusProbe must return a typed error on malformed dumpsys output, never a guessed value. Only cells you actually ran become PASS, each citing spec file and test name. Keep `fake only` and `not run` where true. Stop the emulator at the end and show `adb devices -l`.

STOP POINTS (write the FINAL REPORT and stop at the first that applies)
S1. WP-62, WP-34, WP-35 and WP-63 are done (normal end).
S2. A dependency or rebaselined package fails verify with missing/changed files you did not cause.
S3. A package is blocked after the single allowed fix attempt per failing gate.
S4. The package text contradicts the code or the machine you see, or a decision is needed that the plan does not make.
S5. Anything that needs a download, a system setting, a permission, the person's emulator, or a physical device.
S6. Any action that would touch emulator-5554, a person-owned AVD, upstream code, or a file you do not own.
S7. You are unsure whether an action is allowed. Ask.

STANDING RULES
No git commit/push/tag/reset/checkout --/restore/stash/clean/rebase, no rm -rf outside the scratchpad, no sudo, no release, no --no-verify. Edit only each package's owns paths. Do not edit plan files except through the ledger script. New TypeScript: strict, no any / as unknown as / @ts-ignore, no silent catch (every catch you write or touch must rethrow, return a typed error, or log; say which in the checkpoint), .ts relative imports, files under 400 lines, one trailing newline. Long commands run in the background and you wait for completion. After "done" run the rebaseline commands the section names, then verify each and paste the output.

CHECKPOINT FORMAT
python3 scripts/program_ledger.py checkpoint <WP-ID> --agent <NAME> --note "done: <steps, exact file paths>. next: <next step>. verified: <commands run and what I saw>. unverified: <assumed or none>. emulator state: <which serial is running or none>"

FINAL REPORT (Arabic; commands, paths and code in English). Headings exactly:
1. الحزم المنجزة: المعرف، الملفات، وأدلة بالأوامر والنتائج الحقيقية
2. ما فعلته على المحاكي: كل أمر أرسلتَه إلى emulator-5580، وتأكيد أن emulator-5554 والـ AVDs الخاصة بالمستخدم لم تُمسّ (ناتج adb devices -l وemulator -list-avds قبل وبعد)
3. الخلايا التي تغيّرت في CONFORMANCE.md وسبب كل تغيير
4. نتيجة WP-35 لكل خطوة (feasible / device-dependent / not feasible)
5. الحزم المتوقفة أو المحجوبة والسبب
6. ما لم أتحقق منه
7. إعادة الأساس (rebaseline) ونتيجة verify لكل حزمة
8. ناتج الأمرين الأخيرين كما هما: status ثم next
```
