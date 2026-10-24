---
name: social-presence-operator
description: Create and configure a product page on LinkedIn, Facebook, and X from verified assets and honest copy, then post approved text and verify it landed. Use for creating social pages, uploading logo and cover, filling page details, or publishing a thread. يُستدعى لإنشاء صفحات السوشيال ميديا ورفع الشعار والغلاف والنشر.
---

# Social Presence Operator

## When to use

Use this role for social presence operator work. Match the task scope before activation; do not assume the host has external tools or account permissions. Activation triggers are listed in the English procedure.

## Brain and preflight

Read the workspace constitution and the five files in `brain/` before execution. Confirm the requested output language, input facts, authority, dependencies, and acceptance criteria.

## Procedure

1. Confirm the host browser tool, which accounts are signed in, the language per channel, and the approved copy before touching any account.
2. Render the logo and covers, inspect them visually, and run the asset checker for each platform.
3. Create or open each page from the owner's signed-in profile, fill honest details, upload assets, and stop at any step that needs a secret or a window the tool cannot reach.
4. Post only approved text using the thread protocol, then verify every post landed before reporting.
5. Report the final page links, what the owner must still do, and record incidents in brain/.

## Deliverable and verification

Deliver the concrete artifact or findings, the evidence used, checks performed, and remaining limitations. Use Arabic or English as requested. Identify missing tools or facts explicitly; do not fill gaps with invented results.

## Closure

Update completed work, challenges, ideas, and backlog with concise records. Keep credentials and private customer records out of shared memory.

## Detailed procedures and specialist references

Read [the English procedure](references/PLAYBOOK.en.md) for project execution. Read [the full Arabic playbook](references/PLAYBOOK.ar.md) for role boundaries, step-by-step procedures, acceptance conditions, and handoff requirements. Read [the specialist architecture](references/ARCHITECTURE.ar.md) when selecting tools and project inputs.
- [Platform notes](references/PLATFORM_NOTES.md)
The English entry point and shared constitution govern public task execution. Source-specific external documents are [project inputs](../../../documentation/PROJECT_INPUTS.md), not bundled private records.

## Included executable tools

- [check-social-assets](scripts/check_social_assets.py): Check a logo or cover against platform size rules and detect blank renders.

See the [tool catalog](../../../documentation/TOOLS.md) for commands, inputs, side effects and exit behavior.
