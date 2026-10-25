# Browser companion

Crewloom ships an optional manual Chrome/Brave/Edge companion under `extensions/chrome`. Load that folder unpacked in the browser's extension manager. Version 2.3.0 starts disabled; enable it in the side panel or the local dashboard. Activation is extension-wide in this browser, not a project permission or an OS sandbox. It persists in Chrome storage and blocks indexing, inspection, summary reads, click requests and visible-tab capture when off; disabling clears overlays.

The local dashboard at port4317 exchanges state with its content script on the same page. It reports unknown until a response arrives, and loses readiness when the heartbeat expires. Other sites cannot request activation. Remote/token-authenticated dashboards do not bypass Origin policy; open settings from the authenticated dashboard itself. The status API identifies the dashboard only, and does not register a browser or certify computer-control readiness.

Numbered clicks resolve extension-owned element references, not page-controlled attributes. Requests bind tab, frame, document token and indexing generation; late replies after navigation are discarded. Removed, changed, hidden, inert, disabled or covered targets are refused. Re-index after navigation or page changes. Form fields expose labels/placeholders rather than entered values. Context-menu capture is queued for its window for up to30 seconds and consumed when the panel is ready; a changed active tab is refused. Capture requires an explicit window ID. Viewport priority, open Shadow DOM and readable-frame indexing share a400-target budget, with omissions reported. Directory pagination exposes all returned targets. Daemon status refreshes every15 seconds without repeating unchanged logs. Browser-internal pages and the Web Store restrict content scripts.

Visible-tab capture requires broad host access in this version. Review the `<all_urls>` permission before installing. DOM actions need no macOS Accessibility grant. The optional explicit macOS capture probe runs with bounded shell-free argv and removes its temporary image; it does not implement a desktop controller. Accessibility is therefore unverified. Screen-probe success is separate from browser capture and other processes' permissions.

The [Codex plugin](CODEX_PLUGIN.md) is a separate install surface. No model-to-browser action queue, MCP desktop-control server or autonomous computer-use claim is included here.

## Verification

```bash
python3 -m unittest scripts.test_sidepanel
CREWLOOM_REAL_BROWSER=1 python3 -m unittest scripts.test_sidepanel
```

Default rendered checks use mocked Chrome APIs; real browser checks are opt-in and skip when dependencies or the fixture dashboard are unavailable. Screenshots from mocked APIs are layout previews only. New tests reproduce spoofed attributes, stale generations, removed/hidden elements and disabled controls. Dashboard tests exercise actual request authorization and persistent worker state with a controlled Chrome transport.

Version 2.3.1 clears all contacted frame overlays and HUDs after Clear, tab changes or partial scan failures. Unused frame quota remains available under the shared cap. Unverifiable cross-origin embeddings are omitted with a warning instead of exposing unusable click handles; open those frames separately. Permissions are unchanged. Use a stable unpacked-installation directory for future updates.

## Claude-Compatible Computer Use & Tab Groups

Version 2.3.2 introduces full reverse-engineered Claude Computer Use tool compliance (`computer_20241022` and `computer_20250124`):

- **Chat Tab Group Isolation**: Each chat session manages its own dedicated Chrome Tab Group, automatically grouped and color-coded.
- **Background Execution**: Background browsing operations (`create_tab`, `navigate`) run with `active: false` and DOM interaction uses non-scroll focusing (`preventScroll: true`), ensuring the user's workflow is never interrupted by tab switching or window focus stealing.
- **Action Parity**: Complete implementation of mouse coordinates (`mouse_move`, `left_click`, `right_click`, `double_click`, `triple_click`, `middle_click`, `left_click_drag`), realistic typing with native property setters and event dispatches, key presses, scrolling, and viewport screenshots.
- **Visual Feedback**: Real-time agent cursor overlay displays coordinate motion and click triggers on live web pages.
- **CLI and Runtime Tool**: Registered under `scripts/computer_use.py` and invokable directly via `python3 scripts/crewloom.py run computer-use -- <args>`.

The companion adds a `noFocus` option for indexed clicks, typing and computer actions. With it, the content script does not call `focus()` and scrolls a target into view only when it is outside the viewport, so the user's active element is untouched. The side panel exposes it as a persisted "Background browsing (no focus)" checkbox (default on), and `scripts/computer_use.py` forwards `noFocus` in its payload. The target-tab selector now lists the chat tab group followed by all other open tabs in the window, using the new `GET_ALL_TABS` background message. Re-index after any page change, as before; `noFocus` does not relax stale-index, hidden-target or covered-target refusals.
