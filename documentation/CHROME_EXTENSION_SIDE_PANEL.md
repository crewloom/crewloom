# Browser companion

Crewloom ships an optional manual Chrome/Brave/Edge companion under `extensions/chrome`. Load that folder unpacked in the browser's extension manager. Version 2.2.0 starts disabled; enable it in the side panel or the local dashboard. Activation is extension-wide in this browser, not a project permission or an OS sandbox. It persists in Chrome storage and blocks indexing, inspection, summary reads, click requests and visible-tab capture when off; disabling clears overlays.

The local dashboard at port4317 exchanges state with its content script on the same page. It reports unknown until a response arrives, and loses readiness when the heartbeat expires. Other sites cannot request activation. Remote/token-authenticated dashboards do not bypass Origin policy; open settings from the authenticated dashboard itself. The status API identifies the dashboard only, and does not register a browser or certify computer-control readiness.

Numbered clicks resolve extension-owned element references, not page-controlled attributes. Requests carry the current indexing generation; removed, hidden, disabled or obsolete targets are refused. Re-index after navigation or page changes. The index is capped at400 interactive elements, with omissions reported. Browser-internal pages and the Web Store restrict content scripts.

Visible-tab capture requires broad host access in this version. Review the `<all_urls>` permission before installing. DOM actions need no macOS Accessibility grant. The optional explicit macOS capture probe runs with bounded shell-free argv and removes its temporary image; it does not implement a desktop controller. Accessibility is therefore unverified. Screen-probe success is separate from browser capture and other processes' permissions.

The [Codex plugin](CODEX_PLUGIN.md) is a separate install surface. No model-to-browser action queue, MCP desktop-control server or autonomous computer-use claim is included here.

## Verification

```bash
python3 -m unittest scripts.test_sidepanel
CREWLOOM_REAL_BROWSER=1 python3 -m unittest scripts.test_sidepanel
```

Default rendered checks use mocked Chrome APIs; real browser checks are opt-in and skip when dependencies or the fixture dashboard are unavailable. Screenshots from mocked APIs are layout previews only. New tests reproduce spoofed attributes, stale generations, removed/hidden elements and disabled controls. Dashboard tests exercise actual request authorization and persistent worker state with a controlled Chrome transport.
