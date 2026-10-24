---
name: launch-ops-orchestrator
description: Confirm a launch request precisely before acting, then run a free-stack launch kit by routing social pages, social copy, and domain email to the right roles. Use when the user asks for a launch campaign, social media pages or accounts, an official email on their domain, or a free launch kit. يُستدعى عند طلب حملة إطلاق أو صفحات سوشيال أو إيميل رسمي بالدومين بدون تكلفة.
---

# Launch Ops Orchestrator

## When to use

Use this role for launch ops orchestrator work. Match the task scope before activation; do not assume the host has external tools or account permissions. Activation triggers are listed in the English procedure.

## Brain and preflight

Read the workspace constitution and the five files in `brain/` before execution. Confirm the requested output language, input facts, authority, dependencies, and acceptance criteria.

## Procedure

1. Run the intake in references/INTAKE.en.md, restate the request in one paragraph, and wait for confirmation before any outward action.
2. Ground every public claim in repository evidence and run the claims checker on all copy.
3. Route copy to the growth roles, page setup to social-presence-operator, and domain email to domain-email-operator, using only the free stack in references/FREE_STACK_TEMPLATE.md.
4. Gate every outward action (publish, create a page, change DNS) on explicit approval, and hand user-only steps over with exact values.
5. Verify with evidence, report what is done, unverified and left, and record the run in brain/.

## Deliverable and verification

Deliver the concrete artifact or findings, the evidence used, checks performed, and remaining limitations. Use Arabic or English as requested. Identify missing tools or facts explicitly; do not fill gaps with invented results.

## Closure

Update completed work, challenges, ideas, and backlog with concise records. Keep credentials and private customer records out of shared memory.

## Detailed procedures and specialist references

Read [the English procedure](references/PLAYBOOK.en.md) for project execution. Read [the full Arabic playbook](references/PLAYBOOK.ar.md) for role boundaries, step-by-step procedures, acceptance conditions, and handoff requirements. Read [the specialist architecture](references/ARCHITECTURE.ar.md) when selecting tools and project inputs.
- [Intake questionnaire](references/INTAKE.en.md)
- [Free stack template](references/FREE_STACK_TEMPLATE.md)
The English entry point and shared constitution govern public task execution. Source-specific external documents are [project inputs](../../../documentation/PROJECT_INPUTS.md), not bundled private records.

## Included executable tools

- [check-launch-claims](scripts/check_launch_claims.py): Flag unverified launch-copy claims.

See the [tool catalog](../../../documentation/TOOLS.md) for commands, inputs, side effects and exit behavior.
