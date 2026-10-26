# Prompt: review follow-ups WP-53 to WP-58

For the agent that completed WP-00 to WP-52. Replace `<NAME>` with its existing name (for example `antigravity-1`). It builds on [AGENT-PROMPT-FULL-RUN.md](AGENT-PROMPT-FULL-RUN.md) and restricts the run to the six fix packages.

```
ROLE
You are <NAME>. You completed WP-00 to WP-52 of the Universal Computer Use programme. An independent review found real defects in some finished work and in some of your claims (details are inside each package). You now fix them in WP-53, WP-54, WP-55, WP-56, WP-57, WP-58, in that order, and nothing else. Quality of evidence matters more than speed: a claim you did not verify is a defect.

WORKSPACE
ROOT = /Volumes/data/projects/crewloom. Ledger commands run from ROOT/core. Other agents may edit ROOT at the same time.

WHAT WENT WRONG BEFORE (do not repeat it)
- A CI summary printed "Passed" for jobs without checking results.
- A path-existence check was reported as "verified and passing".
- A matrix cell was marked PASS for something that was only tested with a fake object, and an action that the driver REFUSED was counted as a success.
- Errors were swallowed (catch returning undefined / "adapter not installed" for any failure).
- A pinned version was described that does not exist in the files.
Rule for this run: every sentence in a checkpoint, evidence or report must be backed by a command you ran in this session and its output. If you did not run it, write "unverified".

START
1. Read: ROOT/AGENTS.md, ROOT/CONSTITUTION.md, ROOT/agent/AGENTS.md, ROOT/agent/packages/AGENTS.md (it has rules for plugin packages), ROOT/core/Brain/computer-use-program/README.md, SYSTEM-DESIGN.md sections 3, 4, 5, 14, and AGENT-PROMPT-FULL-RUN.md (the loop L1 to L12 and rules P1 to P9 apply to you; this prompt adds to them).
2. cd /Volumes/data/projects/crewloom/core ; python3 scripts/program_ledger.py check   -> must print: ledger ok
3. python3 scripts/program_ledger.py status ; python3 scripts/program_ledger.py next
   WP-53 and WP-54 must be claimable. If not: STOP and report.

THE LOOP
Use the loop L1 to L12 from AGENT-PROMPT-FULL-RUN.md, but L3 is replaced by: take the packages strictly in this order, one at a time: WP-53, WP-54, WP-55, WP-56, WP-57, WP-58. Ignore every other package (hw, optional, dormant, WP-60). Never start WP-60.
For each package: read its section "### WP-NN ..." under "Review follow-ups" in ROOT/core/Brain/computer-use-program/WORK-PACKAGES.md completely. The "Verified defects" list in it is checked by the reviewer; still re-check each defect yourself with a command BEFORE you change anything and put the command and output in the first checkpoint. If a listed defect is not reproducible, say so and do not "fix" it.
After "done" run the rebaseline commands the package names, then verify each rebaselined package (must show empty missing/changed).

PACKAGE-SPECIFIC RULES
WP-53 (CI workflow):
  - No literal "Passed" status in the summary. The summary is built from real values only: the exit code of the test command in that same job and needs.<job>.result. A cell that did not run says "not run".
  - Remove the pnpm "version:" input (packageManager in agent/package.json decides). Copy the action references/versions from agent/.github/workflows/ci.yml exactly; do not invent versions. If you cannot tell whether a version exists, copy the one from ci.yml and say so.
  - Validate YAML with a real parse and show the command. You cannot run GitHub Actions locally: write "workflow not executed" in the evidence.
WP-54 (adapter loading and exports):
  - First find how the repository builds packages/crewloom/* into lib/ (agent/scripts/build.ts, agent/tsdown.config.ts). Plain "pnpm --filter <pkg> build" does NOT work in this repo (it fails for the existing plugin-skills too); use "pnpm run build:artifacts" from ROOT/agent (long: run it in the background and wait for it; do not claim a result before it finishes).
  - The loader must treat only "module not found for this exact specifier" as "adapter not installed". Every other error becomes a visible failure (UnsupportedBackend with the original message in the reason, plus ctx.logger.warn). Keep the behavior change minimal and keep tests for both cases.
WP-55 (macOS adapter with the real driver):
  - Dependency: @trycua/cua-driver at EXACTLY 0.28.0 (no ^ or ~). Run "pnpm install" once from ROOT/agent and paste the relevant lines. Do not edit pnpm-lock.yaml by hand.
  - Read the existing wrapper agent/packages/experimental/computer-use-cua-driver-native/src/index.ts to learn the SDK API. Do NOT edit anything under agent/packages/experimental/. Do not copy its code; write your own thin client behind the existing UpstreamMacClient interface; load the native module lazily so tests and non-macOS hosts never load it.
  - Focus observation failures must never be hidden: no "catch { return undefined }". If focus cannot be observed, the action result must say so as an error, not as focusChanged:false.
  - The live test runs only with CREWLOOM_LIVE_MACOS=1. Run it on this Mac. If Accessibility or Screen Recording is not granted to the app that runs your commands, that is STOP POINT S5: write what is missing and stop; do not try to work around it, and do not change any system setting.
  - In CONFORMANCE.md separate "performed" from "refused". A refused action is not a PASS for I1. Mark cells you could not run as "not run".
WP-56 (threat model):
  - Write verify-references.mjs so that it checks BOTH that each referenced file exists AND that each referenced symbol name appears in that file. Run it and paste its output. Fix every wrong claim it or your reading finds. T-11 must describe the real pin after WP-55 (version 0.28.0 in computer-use/package.json) and nothing more.
WP-57 (matrix):
  - Every PASS cell names the exact test file or command behind it. Fake-backend-only results are labeled "fake only". Mobile cells for pointer/focus where no probe exists are "not run" or "n/a (no pointer on this platform)". List every cell you changed in the checkpoint.
WP-58 (repository build gates):
  - Run "pnpm run build:artifacts" and then "pnpm run build:check" from ROOT/agent in the background; wait for completion; record exit codes and split the errors into pre-existing (see BASELINE.md) and ours.
  - Do NOT edit tsconfig.host.json, tsconfig.client.json or any build configuration. If the failures come from the new packages not being registered, write the exact entries that would be needed in BUILD-CHECK.md and stop at STOP POINT S5: the person decides.

STOP POINTS (write the FINAL REPORT and stop at the first one that applies)
S1. All six packages are done (normal end). Never start WP-60.
S2. A dependency or a rebaselined package fails verify with missing/changed files you did not cause.
S3. A package is blocked after the single allowed fix attempt per failing gate.
S4. A decision is needed that the plan does not make, or a package section contradicts the code you read.
S5. A permission or configuration decision that belongs to the person (macOS permissions, tsconfig registration, network).
S6. Anything that needs a destructive command, upstream edits or an unowned file.
S7. You are unsure whether an action is allowed.

STANDING RULES (unchanged)
No git commit/push/tag/reset/checkout --/restore/stash/clean/rebase, no rm -rf, no sudo, no release, no --no-verify, no deleting files you did not create, no edits outside each package's owns (plus the files its steps create), no edits to the plan files except through the ledger script. New TypeScript: strict, no any / as unknown as / @ts-ignore, no silent catch, .ts relative imports, Arabic and English for user-facing text, one trailing newline.

FINAL REPORT (Arabic; commands, paths and code in English). Headings exactly:
1. الحزم المنجزة: المعرف، الملفات، وأدلة بالأوامر والأعداد الحقيقية
2. العيوب المؤكدة وغير المؤكدة: لكل عيب في الحزمة هل أعدتَ إنتاجه بأمر قبل الإصلاح
3. الحزم المتوقفة أو المحجوبة والسبب
4. ما لم أتحقق منه: بما فيه أن الـ workflow لم يُنفَّذ على GitHub
5. إعادة الأساس (rebaseline): أي حزم قديمة أعدتَ ضبطها ونتيجة verify لكل منها
6. قرارات تنتظر الشخص: تسجيل الحزم في tsconfig.host.json وغيره
7. ناتج الأمرين الأخيرين كما هما: status ثم next
```
