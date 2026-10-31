# Artifact Taxonomy — how Crewloom governs AI behavior

Arabic twin: [`ARTIFACT_TAXONOMY.ar.md`](ARTIFACT_TAXONOMY.ar.md). Precedence: `CONSTITUTION.md` (workspace root) > this file. Status: **draft v0.1**, pending operator review.

Every artifact that shapes what an AI model does in Crewloom has exactly one type. A type is defined by measurable properties, not by its name.

## Classification axes

1. **Answers** — what it tells the model: what is allowed, how to do it, in what order, who to be, what happened.
2. **Enforcement** — *advisory* (the model chooses to comply) or *deterministic* (code, schema or CI makes non-compliance impossible or visible).
3. **Loading** — *always* in context, or *on demand* by trigger (progressive disclosure).
4. **Verification** — how compliance is proven.

## Types

| Type | Answers | Enforcement | Loading | Example |
|---|---|---|---|---|
| **Constitution** | What never changes | Deterministic + human review | Always | `CONSTITUTION.md` |
| **Rule** | What is forbidden or required of any output (stateless) | Advisory, backed by a Guard | Always, short | "No `any`", "No `!important`" |
| **Contract** | The interface between two components | Deterministic (types, schemas, validators) | In code, not in the prompt | `Result<T,E>`, `contracts` package |
| **Protocol** | Ordered steps with a trigger and a verifiable exit condition (stateful, mandatory) | Advisory, with deterministic checkpoints | On trigger | Release Protocol |
| **Skill** | How to do a class of task (knowledge, optional) | Advisory | On demand | `tdd`, `frontend-design` |
| **Role** | Who the agent is: identity, tool permissions, allowed skills | Deterministic (tool allowlist) | At agent start | Team agents |
| **Memory** | Facts and history (data, not instructions) | n/a | On recall | `core/Brain/` |
| **Guard / Hook** | Runtime enforcement of a Rule or Protocol | Deterministic | Outside the model | `PromptGuard`, pre-commit, CI |
| **Eval** | Whether the work is correct | Measurement | On check | tests, benchmarks |

## Decision tests

- **Rule vs Protocol:** a Rule holds at any instant. A Protocol has order, a trigger and an exit condition. If ordering or an exit condition exists, it is a Protocol.
- **Protocol vs Skill:** a Skill is optional ("when doing X, this is the best way"). A Protocol is mandatory ("when X happens, do exactly this").
- **Workflow** is not a type: mandatory → Protocol, optional → Skill.
- **Role vs Skill:** a Role holds identity and permissions only. Knowledge lives in Skills.

## Governing principles

1. **Prompt text is a request, not a guarantee.** Any Rule or Protocol that matters must be backed by a Guard, Hook, schema or CI check. This is the same principle as Pulse: the model proposes, deterministic code decides.
2. **Context economy.** Only the Constitution and Rules load always, and they stay minimal (aggregate budget under 20k tokens). Everything else loads on demand.
3. **One home per fact.** Each type has one location and one owner; everything else links to it.
4. **A Protocol is complete only with:** trigger, ordered steps, exit condition, failure handling, owner file.
5. **Claims need evidence.** No Protocol is "enforced" until the check that enforces it exists and was run (Constitution Art. VII.7).

## Protocol template

```
name:        <kebab-case>
trigger:     <the event that starts it>
steps:       <ordered, each verifiable>
exit:        <condition checkable by command or schema>
on_failure:  <what to do, who to tell>
enforced_by: <Guard / Hook / CI that checks it, or "advisory">
owner:       <the one file that holds it>
```

## Existing artifacts (not yet migrated)

Protocols currently living inside `AGENTS.md`: Release, Post-Push CI Verification, Context Memory boundaries, Pulse invariants. Migration to one file each is a separate, behavior-preserving change with a backward-compatible pointer left in `AGENTS.md`.
