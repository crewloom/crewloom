# Universal Computer Use programme: start here

Goal: desktop (macOS, Windows, Linux) and mobile (Android, iOS) computer use for Crewloom, built by many agents in parallel or one agent alone, without losing work and without inventing facts.

| File | Purpose |
|---|---|
| [SYSTEM-DESIGN.md](SYSTEM-DESIGN.md) | The architecture, contracts, invariants, patterns, ADRs. The design authority. |
| [WORK-PACKAGES.md](WORK-PACKAGES.md) | Step-by-step instructions for each package (WP-00 to WP-60). |
| `ledger.json` | Machine state: status, dependencies, owned paths, leases, checkpoints, evidence, file hashes. Never edit by hand. |
| `../../scripts/program_ledger.py` | The only tool that changes the ledger. |
| [AGENT-PROMPT.md](AGENT-PROMPT.md) | Copy-paste prompt for any agent, including weaker ones. |
| `BASELINE.md`, `CONFORMANCE.md`, `spikes/`, `adr/`, `security/` | Created by the packages that own them. |

The Arabic overview for people is `universal-computer-use-plan.md` in the Antigravity brain folder; it is a summary, and this directory is the authority.

## Resume protocol (every agent, every session)

Run from `/Volumes/data/projects/crewloom/core`. Replace `<you>` with a unique name (for example `claude-1`).

```bash
python3 scripts/program_ledger.py status
python3 scripts/program_ledger.py next
```

1. Read the repository rules once: `AGENTS.md`, `CONSTITUTION.md`, `agent/AGENTS.md` (workspace root), then [SYSTEM-DESIGN.md](SYSTEM-DESIGN.md).
2. `next` lists packages you may start. `takeover` rows are packages whose previous agent stopped (lease expired). Prefer `takeover` rows, then lower package numbers; required before optional.
3. Claim one package. If it fails, pick another. Never work on an unclaimed package.
   ```bash
   python3 scripts/program_ledger.py claim WP-NN --agent <you>
   ```
   For a `takeover` row: first run `python3 scripts/program_ledger.py show WP-NN`, read every checkpoint, and look at the owned paths on disk (and `git -C <repo> status` in the sub-project that has a git repository: `agent/`, `core/`, `bridge/`, `website/`). Then `takeover WP-NN --agent <you>`. Continue from the last checkpoint; do not restart and do not delete the previous agent's files.
4. Re-verify what you depend on before building on it: for each dependency run `python3 scripts/program_ledger.py verify WP-DEP`. `missing` or `changed` files mean the work was altered after it was marked done: stop, `checkpoint` what you found, and ask the person (another package may have edited it legitimately).
5. Read the package in [WORK-PACKAGES.md](WORK-PACKAGES.md). Do the steps in order. After each meaningful step save a checkpoint (this also renews your lease, which lasts 120 minutes):
   ```bash
   python3 scripts/program_ledger.py checkpoint WP-NN --agent <you> --note "done: steps 1-2 (files: A, B). next: step 3 (write C). open: none"
   ```
6. Run every gate. When all pass:
   ```bash
   python3 scripts/program_ledger.py done WP-NN --agent <you> --evidence "pnpm exec vitest run packages/crewloom/contracts -> 14 passed, 0 failed" --evidence "pnpm run typecheck -> no new errors vs BASELINE"
   ```
   Evidence is the real command and the real result. Never paste a result you did not see.
7. If you cannot continue: `block WP-NN --agent <you> --reason "<command and its output>"`. A blocked package is never marked done.
8. Run `python3 scripts/program_ledger.py next` again and continue, or stop. Your final message states which packages you completed, which you left, and why.

## Hard rules

1. **Do not invent.** No API, flag, path, version, or test result that you did not read or run. If you did not verify it, write `unverified` or `not run`.
2. **Touch only your package's `owns` paths** (see `show WP-NN`). A file you need but do not own: checkpoint it and ask. Files created early and shared by design (`CONFORMANCE.md`, READMEs, preset `package.json`) are intentionally unowned or owned by the documentation package.
3. **Upstream is read-only.** Never edit `agent/packages/experimental/*` or any package outside `agent/packages/crewloom/*` (workspace configuration files that require a one-line registration are the only exception, and you must record each in a checkpoint).
4. **No destructive git or filesystem actions**: no `git reset`, `checkout --`, `restore`, `stash`, `clean`, `rebase`, no force push, no `--no-verify`, no deletion of files you did not create. Other agents work in the same tree at the same time.
5. **No commit, push, tag or release** unless the person explicitly asked in this session. Package WP-60 is the release and needs the person's authorization.
6. **Hardware-gated (`hw`) packages** run only on real hardware of that OS. Without it, leave them `todo`. Never simulate or fabricate their results.
7. **Same failure twice means stop.** One fix attempt per failing gate; on the second failure `block` with the output.
8. **Quality bar** (full list in SYSTEM-DESIGN section 14): strict TypeScript with no new `any`, `as unknown as`, or `@ts-ignore`; typed `Result` errors at ports; no catch-and-ignore; files under about 400 lines and functions under about 60; no `utils.ts`/`helpers.ts`; logical CSS properties for any UI; user-facing text in Arabic and English through the dictionaries; one trailing newline.
9. **Ask when scope-changing ambiguity appears**; otherwise take the `[DECISION]` default, note it in a checkpoint, and continue.

## Working in parallel

- Packages that are `claimable` at the same time and have disjoint `owns` paths can run simultaneously. The tool refuses a claim whose `owns` overlap a live claim.
- Shared build state (`pnpm install`, lockfile) can clash. Run `pnpm install` once at the start of your package if you add a dependency, and say so in the checkpoint.
- Checkpoints are the handoff. Write them as if the next agent has never seen this repository: what is done, which files, what is next, what you tried that failed.

## Working alone (weaker or single agent)

Follow the linear order at the top of [WORK-PACKAGES.md](WORK-PACKAGES.md). Do not skip a gate, do not combine packages, and do not start a package whose dependencies are not `done`. If a step says `[DECISION]`, apply it. If a command's output differs from what the package expects, checkpoint the difference and continue only if the gate still passes; otherwise `block`.

## Maintaining the tool

`scripts/test_program_ledger.py` tests the ledger rules. Run from `core/`: `python3 -m unittest scripts.test_program_ledger -v`. A change to the ledger schema needs a migration note here and a test.
