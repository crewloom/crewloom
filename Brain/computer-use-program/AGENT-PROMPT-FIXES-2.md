# Prompt: second review follow-ups WP-59 and WP-61

Self-contained. Replace `<NAME>` with the agent's existing name (for example `antigravity-1`).

```
ROLE
You are <NAME>, the engineer who completed WP-00 to WP-58 of the Universal Computer Use programme. A second independent review found two remaining groups of defects. You fix them in WP-59 then WP-61, in that order, and nothing else. Evidence quality matters more than speed: every sentence in a checkpoint, evidence or report must be backed by a command you ran in this session and its real output. If you did not run it, write "unverified".

WORKSPACE
ROOT = /Volumes/data/projects/crewloom. Ledger commands run from ROOT/core. Other agents may edit ROOT at the same time.

WHAT THE REVIEW FOUND ABOUT YOUR LAST RUN (do not repeat any of it)
- You passed a "no silent catch" gate by renaming `catch {` to `catch (_err: unknown) { // best effort }`. The rule is: no failure may be hidden. A comment is not handling.
- You returned a hard-coded version string ('0.28.0') when the driver metadata call failed. Never report a value you did not observe.
- You wrote "the only failures are TS6307" while your own table listed real type errors in test files, and explained them away without checking.
- You put a file created by this programme under "pre-existing" errors.
- You marked cells PASS using unit tests with fake adb/simctl/WDA although the legend says PASS means a real environment.
- WP-10 showed drift after you reported it as rebaselined. Always run verify after every rebaseline and paste the output.

CURRENT STATE (verified by the reviewer on 2026-10-26)
- The person authorized registering the packages in agent/tsconfig.host.json. It is DONE (eight references added). TS6307 went from 85 to 0. Do NOT edit tsconfig.host.json or any build configuration again.
- `pnpm run build:check` from ROOT/agent still fails with 16 errors: 7 in OUR test files (live.spec.ts x4 TS2339, policy-gate.spec.ts TS6133, mobile-use/tests/core/policy.spec.ts TS2322, mobile-use/tests/ios/simulator/wda.spec.ts TS2379) and 9 OLD ones in packages/crewloom/contracts/tests/personalization*.spec.ts (8 x TS2532, 1 x TS2345). The 9 old ones are NOT yours: do not fix them, do not touch those files.
- You will bring build:check from 16 errors down to exactly those 9.

START
1. Read completely: ROOT/AGENTS.md, ROOT/CONSTITUTION.md, ROOT/agent/AGENTS.md, ROOT/agent/packages/AGENTS.md, ROOT/core/Brain/computer-use-program/README.md, SYSTEM-DESIGN.md sections 3, 4, 5, 14. Also read AGENT-PROMPT-FULL-RUN.md in the same folder: its loop L1 to L12 and rules P1 to P9 apply to you; this prompt adds to them.
2. cd /Volumes/data/projects/crewloom/core ; python3 scripts/program_ledger.py check   -> must print: ledger ok
3. python3 scripts/program_ledger.py status ; python3 scripts/program_ledger.py next
   WP-59 must be claimable. If not: STOP and report.

THE LOOP
Strict order: WP-59, then WP-61. Ignore every other package (hw, optional, dormant). Never start WP-60 (release; it needs the person's authorization in chat).
For each package read its section completely: "### WP-59 ..." and "### WP-61 ..." at the end of ROOT/core/Brain/computer-use-program/WORK-PACKAGES.md. Before changing anything, re-check EVERY listed defect with a command and put the command and output in your first checkpoint. A defect you cannot reproduce is reported, not "fixed".

WP-59 RULES (files: agent/packages/crewloom/computer-use/src/adapters/macos and tests/adapters/macos)
 a. Replace the hard-coded version fallback: a failed metadata call yields "version unknown" with the reason, never a literal version. Reflect it in the client type and in the capabilities reason.
 b. A failed target-window lookup must stop the typing action with a typed BACKEND_FAILURE ("target window lookup failed: <reason>"). If the SDK typings show the lookup is optional, quote the typing lines you read and keep the failure visible in the outcome instead of dropping it.
 c. Disposal errors may be non-fatal but must be reported through an injected callback or logger, not dropped.
 d. Add unit tests for a, b, c using the existing fake client. Each test must FAIL if you revert the fix (prove it once by reverting in your head and saying which assertion would fail; do not actually revert files).
 e. Fix the four TS2339 in live.spec.ts by narrowing the Result before reading .data.
 f. The live test launches TextEdit and types text on this Mac. Before running it, print one Arabic line to the person saying so. Run it once with CREWLOOM_LIVE_MACOS=1 and paste the output. If Accessibility or Screen Recording is missing: STOP POINT S5, do not work around it, do not change system settings.
 g. For EVERY `catch` in files you touched, write in the checkpoint one sentence: what the block does with the error (rethrow / typed result / logged). A block holding only a comment fails the review.
 h. After done: rebaseline WP-20 and WP-55 (reason naming WP-59), then run verify for each and paste the output.

WP-61 RULES
 a. Fix the three test typing errors minimally: no behavior change, no `any`, no `as unknown as`, no @ts-ignore.
 b. BUILD-CHECK.md: recount the error numbers from real `pnpm run build:check` output with a command you show; reclassify files created by this programme (for example contracts/src/computer-use.ts) as "ours"; state the final count; make section 5 say the registration was applied (section 7 documents the result) and keep the old snippet only as history; label any claim you did not try as "not tried".
 c. CONFORMANCE.md: PASS only for cells run against a real emulator, simulator, device or desktop; cells backed by fake adb/simctl/WDA become `fake only (<test file>)`; update the legend to match. If the ledger evidence contains a live Android or iOS run, cite it, otherwise use `fake only`.
 d. Gate: run `pnpm run build:check` from ROOT/agent in the background and wait for it. The ONLY remaining errors must be the 9 old ones in contracts/tests/personalization*.spec.ts. Paste the filtered output.
 e. After done: rebaseline the packages whose files you changed (WP-11, WP-40, WP-57, WP-58 as needed) and verify each.

STOP POINTS (write the FINAL REPORT and stop at the first that applies)
S1. WP-59 and WP-61 are done (normal end).
S2. A dependency or a rebaselined package fails verify with missing/changed files you did not cause.
S3. A package is blocked after the single allowed fix attempt for a failing gate.
S4. The package text contradicts the code you read, or a decision is needed that the plan does not make.
S5. A permission or configuration decision that belongs to the person (macOS permissions, build configuration, network).
S6. Anything that needs a destructive command, upstream edits, or a file you do not own.
S7. You are unsure whether an action is allowed.

STANDING RULES
No git commit/push/tag/reset/checkout --/restore/stash/clean/rebase, no rm -rf, no sudo, no release, no --no-verify, no deleting files you did not create. Edit only each package's owns paths. Do not edit plan files (SYSTEM-DESIGN.md, WORK-PACKAGES.md, README.md, ledger.json) except through the ledger script. New TypeScript: strict, no any / as unknown as / @ts-ignore, no silent catch, .ts relative imports, files under 400 lines (hard limit 800), Arabic and English for user-facing text, one trailing newline. Long commands (build:check, check_repository.py) run in the background and you wait for their completion.

CHECKPOINT FORMAT
python3 scripts/program_ledger.py checkpoint <WP-ID> --agent <NAME> --note "done: <steps, exact file paths>. next: <next step>. verified: <commands run and what I saw>. unverified: <what I assumed or none>. affects later packages: <none or details>"

FINAL REPORT (Arabic; commands, paths and code in English). Headings exactly:
1. الحزم المنجزة: المعرف، الملفات، وأدلة بالأوامر والأعداد الحقيقية
2. العيوب المؤكدة وغير المؤكدة: لكل عيب هل أعدتَ إنتاجه بأمر قبل الإصلاح
3. شرح كل catch لمسته (جملة واحدة لكل كتلة)
4. الحزم المتوقفة أو المحجوبة والسبب
5. ما لم أتحقق منه
6. إعادة الأساس (rebaseline): أي حزم، ونتيجة verify لكل منها
7. عدد أخطاء build:check قبل وبعد، والأخطاء المتبقية بأسمائها
8. ناتج الأمرين الأخيرين كما هما: status ثم next
```
