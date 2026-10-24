# Social Presence Operator

This English procedure adapts the role for reusable project work. Account access is supplied by the owner's signed-in browser; none is bundled.

## Activation triggers

Create social pages for a product, set up LinkedIn or Facebook or X presence, upload a logo or cover, fill page details, publish a thread or post. Arabic triggers: اعمل صفحة، ارفع الشعار والغلاف، انشر الثريد.

## Inputs and scope

Approved copy and language per channel, brand source files (SVG preferred), the list of platforms, and which accounts are signed in. Read the constitution, `PLATFORM_NOTES.md` and `brain/` first.

## Procedure

1. **Preflight.** Confirm a browser tool exists and each target site is signed in. If a site shows a login page, stop and ask the owner to sign in. Do not enter passwords.
2. **Assets.** Render logo and covers to PNG at platform sizes. Open each image and look at it. Run `crewloom run social-assets -- --platform <p> --kind <logo|cover> --file <png>`; fix every FAIL.
3. **Create or open the page.** Use the owner's signed-in profile. Fill name, tagline, About and website from the approved copy. State only verified facts and the true release status.
4. **Stop conditions.** Stop and hand off at: account creation, passwords, emailed or SMS codes, API or SMTP keys, payment, terms the owner must accept for their own account, and any popup window outside the tool's reach.
5. **Upload and save.** Upload via the file input of the correct dialog (the page may hold several, such as a reel creator). Confirm the preview, then save. Look for the platform's saved confirmation.
6. **Posting.** Post only text the owner approved. Thread protocol: type one post, screenshot, add the next post only when an empty box is focused, compare to the approved text, submit once, wait, then verify the profile counter rose by the expected number. On failure, check state before any retry.
7. **Verify and report.** Open the public page, confirm logo, cover, details and posts. List page links, unverified items, and the owner's remaining steps.
8. **Close.** Add dated notes to `brain/`; never store credentials or account identifiers.

## Deliverable and acceptance

Live pages with verified assets and details, posted content matching the approved text, and an owner checklist. A saved form is not acceptance; the public page is.

## Failure handling

Two identical failures stop that action. Never delete posts or pages on your own; list what to delete and let the owner do it.

## Handoff

Carry project root, page links, approved copy version, checks run, open questions.
