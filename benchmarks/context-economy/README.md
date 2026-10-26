# Context-economy benchmark

Measures how many tokens an agent processes, and what it costs, on fixed read-only tasks from this repository. Every optimisation (lighter instructions, repo map, routing) must show a drop here **without** a drop in graded correctness.

## What it measures

Per run: API turns, tool calls by name, context size at the first and last turn (`baseContext`, `finalContext`), billed tokens split into input, cache write, cache read and output, cost in USD, duration, and whether the answer matched the task's `mustMatch` patterns.

All token figures come from the provider usage fields in the agent's own transcript. Nothing is estimated.

## Tasks

`tasks.json` holds 8 `specific` tasks (the answer is one file or value) and 2 `vague` tasks (diagnosis across files). Specific tasks and `diagnose-data-loss` have deterministic graders. `diagnose-slow-settings` has `mustMatch: null`, so its stored answer needs a manual read; a cheaper run that answers worse must not count as a win.

## Run

```sh
node run.mjs --label baseline-claude-code            # all tasks, read-only
node run.mjs --label lean --only locate-constant --repeat 3 -- --setting-sources user
node compare.mjs results/<baseline>.jsonl results/<candidate>.jsonl
node --test harness.test.mjs                         # offline checks of the metric and grading logic
```

Arguments after `--` go to the agent CLI, so a variant (for example fewer tools or a different instruction set) is a flag, not a code change. Results are written to `results/` and are not committed.

## Limits

- Only the `claude` CLI adapter exists. Crewloom's own agent (`agent/`) is not measured yet, so its fixed-context baseline is unknown. Adding it means a second adapter that produces the same record fields.
- Model output varies between runs. Use `--repeat 3` or more before trusting a difference, and compare medians (`compare.mjs` does).
- The graders check that the answer names the right files and values. They do not prove the reasoning is sound.
- The tasks encode current file locations. When the code moves, update the matching `mustMatch`.
