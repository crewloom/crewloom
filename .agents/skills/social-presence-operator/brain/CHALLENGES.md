# Challenges

Record the cause, attempted solution, result, and remaining blocker. Entries below are generalized from a real run; they hold no account identifiers or credentials.

### Logo uploaded as a black square
- Cause: a 16-bit PNG whose strokes were nearly invisible, and an SVG converted with a renderer that dropped semi-transparent strokes.
- Fix: render with a renderer that honors the SVG, open the PNG and look at it, then run `check-social-assets`; it fails images that are almost one colour.

### Clicks landing on the wrong control
- Cause: layouts shifted after a link preview or an error banner appeared, so remembered coordinates were stale.
- Fix: screenshot after every state change and before every click; prefer element references over coordinates.

### Duplicate thread
- Cause: a slow service accepted the thread late; the first attempt looked like a failure and was repeated.
- Fix: after pressing post, wait, then check the profile post counter before any retry.

### Typing went into the wrong box
- Cause: the add-post control had moved, so text was appended to the previous post.
- Fix: confirm a new empty box exists, then type; compare the result with the approved text.

### Browser tab stuck on a leave-site dialog
- Cause: a half-finished setup form held unsaved state.
- Fix: open a new tab instead of retrying navigation; never force-close a form that holds the owner's data.

### Dialog opened as a separate window
- Cause: some settings flows open a popup window outside the controlled tab group.
- Fix: give the owner exact field values and wait; do not guess at the window.

### Account username already taken
- Cause: the preferred page slug belonged to someone else.
- Fix: say so plainly, propose a close alternative, and let the owner decide.
