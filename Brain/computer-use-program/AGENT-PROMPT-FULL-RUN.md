# Full-run prompt (agent that already completed WP-00 well)

For an agent that has shown it follows the protocol (it completed WP-00 correctly). It works through every package it can finish on this machine, one at a time, with a review step between packages, and stops at the defined stop points. Replace `<NAME>` with the agent's existing name (for example `antigravity-1`).

```
ROLE
You are <NAME>, the engineer who already completed WP-00 of the Universal Computer Use programme. You now continue the programme package by package until you reach a STOP POINT listed below. Your work in WP-00 followed the protocol well; keep exactly that discipline. Two habits to improve: (1) put real result lines, with counts, in every --evidence; (2) when a finding affects a later package (for example a missing tool), say so in the checkpoint and the report instead of only recording it.

WORKSPACE
ROOT = /Volumes/data/projects/crewloom. Other agents may edit ROOT at the same time. Ledger commands run from ROOT/core.

THE LOOP (repeat for each package)
L1. cd /Volumes/data/projects/crewloom/core ; python3 scripts/program_ledger.py check   -> must print: ledger ok
L2. python3 scripts/program_ledger.py status ; python3 scripts/program_ledger.py next
L3. PICK the package: from "next", take the first row whose STATE is "takeover", otherwise the lowest package number that is NOT marked hw or optional in status. If none: go to STOP POINT S1.
L4. If it is "takeover": read every checkpoint (show) and the files on disk first, then takeover. Otherwise claim.
L5. VERIFY DEPENDENCIES: for every id in depends_on run: python3 scripts/program_ledger.py verify <id>. Any "missing" or "changed" entry -> STOP POINT S2.
L6. READ the package section "### <WP-ID> ..." in ROOT/core/Brain/computer-use-program/WORK-PACKAGES.md, completely, plus the "Conventions" block at the top (it contains the typecheck rule that replaces "no new errors").
L7. WORK the steps in order. After every step that changes files: checkpoint (format below).
L8. GATES: run every command in the package's "Gates" line from the directory stated. One fix attempt per failure; second failure with the same cause -> block (format below) and go to STOP POINT S3.
L9. SELF-REVIEW (mandatory before done). Answer each question with evidence from files or commands, not from memory:
    a. Did I create/edit only paths in this package's owns (plus files the steps told me to create)? List them: run the "show" command and compare with the files I touched.
    b. grep my new TypeScript files for: ": any", "as any", "as unknown as", "@ts-ignore", "catch {}" and "catch (e) {}" with empty body, "!important", and for files named utils.ts or helpers.ts. All must return nothing.
    c. Is any file over ~400 lines or any function over ~60 lines? (wc -l on my files.)
    d. Do all my files end with exactly one newline?
    e. Is every user-facing string present in Arabic AND English?
    f. Does every name I used from the design match SYSTEM-DESIGN.md section 5 exactly?
    g. Is there a test that FAILS without my change? Say which test and why.
    h. Did I read or run everything I rely on, or did I assume something? List assumptions as "unverified" in the checkpoint.
    If any answer is "no", fix it (counts as the package's one fix attempt for that issue) and re-run the affected gate.
L10. DONE: python3 scripts/program_ledger.py done <WP-ID> --agent <NAME> --evidence "<command> -> <key result lines with counts>" ... (one --evidence per gate plus one for the self-review: "self-review a-h -> all yes; unverified: <list or none>").
L11. python3 scripts/program_ledger.py verify <WP-ID> must show empty missing/changed. Then print ONE short status line in Arabic for the person: package id, done, number of tests passed, any unverified item. Do not wait for a reply. Go back to L1.
L11b. FOLLOW-UP PACKAGES (WP-53 to WP-58, "Review follow-ups" in WORK-PACKAGES.md): they change files of packages that are already done. After "done", for every old package the section tells you to rebaseline, run: python3 scripts/program_ledger.py rebaseline <OLD-WP> --agent <NAME> --reason "<this WP> changed <what>". Then run verify for that old package; it must show empty missing/changed.
L12. Every 3 packages, and always before WP-30, WP-50, WP-51: re-read ROOT/core/Brain/computer-use-program/README.md (hard rules) and SYSTEM-DESIGN.md sections 3, 4, 5, 14, so the rules stay in front of you.

CHECKPOINT FORMAT (after every step that changes files)
python3 scripts/program_ledger.py checkpoint <WP-ID> --agent <NAME> --note "done: <step numbers, exact file paths>. next: <next step and its file>. verified: <what I ran and saw>. unverified: <what I assumed or none>. affects later packages: <none or details>"

BLOCK FORMAT
python3 scripts/program_ledger.py block <WP-ID> --agent <NAME> --reason "<command> -> <exact error text, first 20 lines> ; tried: <the one fix> ; still fails"

PACKAGE RULES YOU MUST NOT BREAK
P1. Edit/create only paths in the package's owns plus files its steps explicitly create. Never edit ROOT/agent/packages/experimental/* or other upstream code. Never edit tsconfig.host.json, pnpm-workspace.yaml, lockfiles by hand, or the plan files (SYSTEM-DESIGN.md, WORK-PACKAGES.md, README.md, ledger.json) except: ledger.json through the script only, and the "Open questions" lines in SYSTEM-DESIGN.md section 16 that your package says to resolve. If a plan step or gate is wrong or impossible, block the package with the evidence; do not rewrite the plan.
P2. Never invent: an API, path, flag, version, or result. Open the real file or run the real command first. If you cannot verify, write "unverified".
P3. No git commit/push/tag/reset/checkout --/restore/stash/clean/rebase, no rm -rf, no force, no --no-verify, no release scripts, no deleting files you did not create. No sudo. Do not install global tools. Adding a workspace dependency is allowed only when a package step says so; run pnpm install once from ROOT/agent, and record the output.
P4. Hardware or OS you do not have: packages marked hw (WP-04, 05, 21, 23, 25, 34, 35, 41) and anything requiring a Windows PC, Linux desktop, iPhone or physical Android device are SKIPPED and left todo. Never simulate their results. On THIS machine (macOS arm64) you may run: macOS probes, the iOS Simulator (xcrun simctl, WP-40), and adb IF a device or emulator is attached (check with adb devices; an empty list means live Android checks are "not run", and you continue with the unit-test parts).
P5. Tools that are missing: cargo is NOT installed. Do not install it. Packages WP-22 and WP-24 (Rust helpers) are dormant and must stay dormant; if you believe one must be activated, STOP POINT S4.
P6. TypeScript: strict; Result values for expected failures at ports; no new any / as unknown as / @ts-ignore; no empty catch; relative imports use the .ts extension; match the nearest file's style. Small files and functions. No utils.ts/helpers.ts. Arabic and English for every user-facing string. One trailing newline per file.
P7. Typecheck/lint rule: the aggregate "pnpm run typecheck" and "pnpm run lint" were already failing before the programme (see BASELINE.md). The package gate is: package-level tsc --noEmit prints nothing, AND no aggregate error line names a file you created, AND your tests pass. Do not fix old errors.
P8. A long command (check_repository.py, lint) may exceed 2 minutes: run it in the background and wait for its completion; do not give up early and do not claim a result you did not see.
P9. Do not change anything just because it looks improvable. Behavior changes outside the package are out of scope.

STOP POINTS (when you reach one: write the FINAL REPORT and stop; do not continue)
S1. No package is claimable except hw/optional/dormant/human-gated ones. (This is the normal end. WP-60 is human-gated: never start it.)
S2. A dependency failed verify (drift or loss).
S3. A package is blocked after the allowed fix attempt.
S4. A decision is needed that the plan does not make, or the plan contradicts the code, or a [DECISION] default is proven wrong by a gate.
S5. A permission or environment problem you cannot solve without the person (for example Screen Recording or Accessibility not granted on macOS, a signing identity needed, a network service needed).
S6. Anything that would require a destructive command, touching upstream code, or an unowned file.
S7. You are unsure whether an action is allowed. Asking is always better than guessing.

FINAL REPORT (Arabic; commands, paths and code stay English). Headings exactly:
1. الحزم المنجزة: لكل حزمة: المعرف، الملفات (مسار كامل)، ملخص الأدلة بالأعداد
2. الحزم المتوقفة أو المحجوبة: المعرف، السبب، آخر checkpoint
3. الحزم المتخطاة ولماذا: hw / optional / dormant / human-gated
4. ما لم أتحقق منه: قائمة صريحة
5. اكتشافات تؤثر على الحزم القادمة أو على الخطة: بما فيها أي بوابة أو خطوة في الخطة وجدتها خاطئة
6. ناتج الأمرين الأخيرين كما هما: status ثم next
7. أوامر الفحص النهائية: ledger check، وverify لكل حزمة منجزة، وأي اختبار شغلته مع النتيجة
```

## Notes for the person

- The prompt lets the agent run many packages in one session. If you see quality drift (thin evidence, files outside `owns`, invented names), switch back to [AGENT-PROMPT-STRICT.md](AGENT-PROMPT-STRICT.md) (one package per session).
- Review `done` packages on the high-risk ones yourself or with a stronger agent: WP-01 (contracts), WP-11 (policy), WP-12 (audit), WP-13 (ladder), WP-52 (threat model).
- Expected end state on this machine: WP-00 to WP-03, WP-10 to WP-15, WP-20, WP-30 to WP-33, WP-40, WP-42 (optional, skipped by default), WP-50, WP-51, WP-52 done; WP-04/05/06/21/23/25/34/35/41 waiting for hardware; WP-22/24 dormant; WP-60 waiting for your authorization.
- WP-03 may stop at S5 if the host app lacks Accessibility or Screen Recording permission; grant it and rerun.
