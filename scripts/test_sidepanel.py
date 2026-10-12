#!/usr/bin/env python3
"""Regression coverage for the Crewloom Computer Use Chrome extension.

The panel and the content script are loaded in headless Chromium with a mocked
`chrome` API surface, so the assertions cover real rendered behavior instead of
source text. Playwright is optional: when it or its Chromium build is missing the
suite skips instead of failing the repository gate.
"""
import json
import os
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / 'extensions' / 'chrome'
ASSETS = ROOT / 'assets'

PANEL_MOCK = """
try {
  window.__stored = JSON.parse(sessionStorage.getItem('crewloom.test.store') || '{}');
} catch (error) {
  window.__stored = {};
}
window.__persist = () => sessionStorage.setItem('crewloom.test.store', JSON.stringify(window.__stored));
window.__sent = [];
window.__panelMessages = [];
window.__pendingCapture = %(pending)s;
window.__tab = %(tab)s;
window.__indexResult = %(indexResult)s;
window.chrome = {
  windows: {getCurrent: callback => queueMicrotask(() => callback({id:7}))},
  runtime: {
    lastError: %(lastError)s,
    getURL: (path) => path,
    getManifest: () => ({ version: '2.2.0' }),
    sendMessage: (message, callback) => {
      window.__sent.push(message);
      if (message.type === 'GET_CONTROL' || message.type === 'SET_CONTROL') { callback({ ok: true, enabled: message.enabled ?? true });
      } else if (message.type === 'CHECK_LOCAL_DAEMON') {
        callback(%(daemon)s);
      } else if (message.type === 'PANEL_READY') {
        const pending = window.__pendingCapture; window.__pendingCapture = null; callback({ok:true,pending});
      } else if (message.type === 'GET_ACTIVE_TAB') {
        callback(window.__tab ? { ok: true, tab: window.__tab } : { ok: false, error: 'No active tab' });
      } else if (message.type === 'CAPTURE_TAB') {
        callback(%(capture)s);
      } else if (message.type === 'OPEN_MACOS_SETTINGS') {
        callback({ ok: true, data: { opened: 'x-apple.systempreferences' } });
      } else {
        callback({ ok: false, error: 'unsupported message' });
      }
    },
    onMessage: { addListener: (fn) => window.__panelMessages.push(fn) }
  },
  storage: {
    onChanged: { addListener: () => {} },
    local: {
      get: (key, callback) => callback(window.__stored),
      set: (values) => { Object.assign(window.__stored, values); window.__persist(); }
    }
  },
  tabs: {
    query: (query, callback) => callback(window.__tab ? [window.__tab] : []),
    sendMessage: (tabId, message, callback) => {
      window.chrome.runtime.lastError = %(sendError)s;
      if (message.type === 'INDEX_PAGE' && window.__indexResult) {
        callback(window.__indexResult);
      } else {
        callback({ ok: true });
      }
    },
    onActivated: { addListener: () => {} },
    onUpdated: { addListener: () => {} }
  }
};
"""

SAMPLE_TAB = {'id': 101, 'windowId': 7, 'title': 'Crewloom Autonomous Orchestrator',
              'url': 'http://localhost:4317'}

SAMPLE_ITEMS = [
    {'index': 1, 'tag': 'button', 'text': 'Computer Use Toggle'},
    {'index': 2, 'tag': 'a', 'text': 'Download Chrome Extension'},
    {'index': 3, 'tag': 'input', 'text': 'Agent Command Prompt'},
]

CAPTURE_OK = {'ok': True, 'dataUrl': 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" '
                                     'width="360" height="180"><rect width="360" height="180" fill="%230b1320"/>'
                                     '<rect x="20" y="20" width="320" height="46" rx="8" fill="%23162235" '
                                     'stroke="%2340ddbc"/><text x="180" y="48" fill="%2340ddbc" text-anchor="middle" '
                                     'font-family="sans-serif" font-size="14">Crewloom Active Agent Viewport</text>'
                                     '<text x="180" y="120" fill="%238ca9ff" text-anchor="middle" '
                                     'font-family="monospace" font-size="12">[1] Computer Use Banner</text></svg>'}

CONTENT_MOCK = """
window.chrome = {
  storage: { local: { get: (_, cb) => cb({ 'crewloom.enabled': window.__enabled !== false }) }, onChanged: { addListener: fn => { window.__controlChanged = fn; } } },
  runtime: {
    getURL: (path) => path,
    onMessage: { addListener: (fn) => { window.__contentMessages.push(fn); } }
  }
};
window.__contentMessages = [];
"""


def _playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    return sync_playwright


def _launch(playwright):
    try:
        return playwright.chromium.launch(headless=True)
    except Exception as exc:  # pragma: no cover - depends on local browser install
        raise unittest.SkipTest(f'Chromium unavailable for Playwright: {exc}')


class ManifestContractTest(unittest.TestCase):
    """Static contract the panel and the content script both depend on."""

    def setUp(self):
        self.manifest = json.loads((EXTENSION / 'manifest.json').read_text(encoding='utf-8'))

    def test_side_panel_and_command_surface(self):
        self.assertEqual(self.manifest['manifest_version'], 3)
        self.assertEqual(self.manifest['side_panel']['default_path'], 'sidepanel.html')
        command = self.manifest['commands']['_execute_action']['suggested_key']
        self.assertEqual(command['mac'], 'Command+Shift+L')
        self.assertEqual(command['default'], 'Ctrl+Shift+L')

    def test_content_script_declares_matching_assets(self):
        content = self.manifest['content_scripts'][0]
        self.assertEqual(content['js'], ['content.js'])
        self.assertEqual(content['css'], ['content.css'])
        for name in ('content.js', 'content.css', 'sidepanel.html', 'sidepanel.css', 'sidepanel.js'):
            self.assertTrue((EXTENSION / name).is_file(), name)

    def test_icons_are_web_accessible_for_the_in_page_hud(self):
        resources = self.manifest['web_accessible_resources'][0]
        self.assertIn('icons/icon-32.png', resources['resources'])
        self.assertEqual(resources['matches'], ['<all_urls>'])
        self.assertTrue((EXTENSION / 'icons' / 'icon-32.png').is_file())

    def test_no_unreachable_popup_surface(self):
        self.assertNotIn('default_popup', self.manifest['action'])

    def test_declared_permissions_cover_used_apis(self):
        for permission in ('sidePanel', 'activeTab', 'scripting', 'storage', 'tabs', 'contextMenus'):
            self.assertIn(permission, self.manifest['permissions'])

    def test_host_permissions_allow_tab_capture(self):
        # captureVisibleTab rejects <all_urls>-less extensions unless activeTab happens to be granted
        self.assertIn('<all_urls>', self.manifest['host_permissions'])


class SidePanelHarness(unittest.TestCase):
    """Headless Chromium harness for the side panel; holds no test methods."""

    @classmethod
    def setUpClass(cls):
        cls.playwright = _playwright()
        if cls.playwright is None:
            raise unittest.SkipTest('Playwright is not installed')
        cls.manager = cls.playwright().start()
        cls.browser = _launch(cls.manager)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'browser', None):
            cls.browser.close()
        if getattr(cls, 'manager', None):
            cls.manager.stop()

    def open_panel(self, page, tab=SAMPLE_TAB, index_result=None, daemon=None,
                   capture=None, send_error='null', pending=None):
        index_result = index_result if index_result is not None else {
            'ok': True, 'count': len(SAMPLE_ITEMS), 'total': len(SAMPLE_ITEMS),
            'truncated': False, 'limit': 400, 'generation': 1, 'items': SAMPLE_ITEMS,
        }
        daemon = daemon if daemon is not None else {'ok': True, 'connected': True, 'data': {'ok': True}}
        capture = capture if capture is not None else CAPTURE_OK
        page.add_init_script(PANEL_MOCK % {
            'tab': json.dumps(tab), 'indexResult': json.dumps(index_result),
            'daemon': json.dumps(daemon), 'capture': json.dumps(capture),
            'lastError': 'null', 'sendError': send_error, 'pending': json.dumps(pending),
        })
        page.goto((EXTENSION / 'sidepanel.html').as_uri())
        page.wait_for_timeout(120)
        return page

    def new_page(self):
        context = self.browser.new_context(viewport={'width': 390, 'height': 900})
        return context, context.new_page()


class SidePanelTest(SidePanelHarness):
    """Rendered side-panel behavior against a mocked chrome runtime."""

    def test_starts_in_english_with_real_boot_log(self):
        context, page = self.new_page()
        try:
            self.open_panel(page)
            self.assertEqual(page.inner_text('#indexBtn .tool-name'), 'Auto-Index Page')
            self.assertEqual(page.inner_text('#daemonLabel'), 'Online :4317')
            logs = page.inner_text('#terminalLogs')
            self.assertIn('Panel ready', logs)
            self.assertIn('2.2.0', logs)
            self.assertIn('Local Crewloom daemon handshake verified', logs)
        finally:
            context.close()

    def test_index_renders_directory_and_note(self):
        context, page = self.new_page()
        try:
            self.open_panel(page)
            page.click('#indexBtn')
            page.wait_for_timeout(120)
            self.assertEqual(page.inner_text('#elemCountBadge'), '3')
            self.assertEqual(page.locator('.directory-item').count(), 3)
            self.assertIn('Showing first 3 of 3 elements.', page.inner_text('.directory-note'))
            self.assertIn('Indexed 3 interactive elements.', page.inner_text('#terminalLogs'))
            self.assertIn('Computer Use Toggle', page.inner_text('.directory-item'))
        finally:
            context.close()

    def test_truncated_index_reports_limit_honestly(self):
        context, page = self.new_page()
        try:
            self.open_panel(page)
            page.evaluate("""() => {
              const items = Array.from({length: 400}, (_, i) => ({
                index: i + 1, tag: 'button', text: 'Item ' + i
              }));
              window.__indexResult = { ok: true, count: 400, total: 900, truncated: true,
                                      limit: 400, items: items };
            }""")
            page.click('#indexBtn')
            page.wait_for_timeout(150)
            self.assertIn('limit 400 reached', page.inner_text('#terminalLogs'))
            self.assertIn('400 of 900', page.inner_text('.directory-note'))
            self.assertEqual(page.locator('.directory-item').count(), 50)
        finally:
            context.close()

    def test_enter_key_executes_click(self):
        context, page = self.new_page()
        try:
            self.open_panel(page)
            page.click('#indexBtn')
            page.wait_for_timeout(120)
            page.fill('#elementInput', '2')
            page.press('#elementInput', 'Enter')
            page.wait_for_timeout(120)
            logs = page.inner_text('#terminalLogs')
            self.assertIn('Executing browser click on element [2]', logs)
            self.assertEqual(page.input_value('#elementInput'), '')
        finally:
            context.close()

    def test_capture_renders_frame_metadata(self):
        context, page = self.new_page()
        try:
            self.open_panel(page)
            page.click('#captureBtn')
            page.wait_for_timeout(150)
            self.assertTrue(page.locator('#visionImg').is_visible())
            self.assertEqual(page.evaluate("() => document.getElementById('visionImg').naturalWidth"), 360)
            self.assertIn('Captured', page.inner_text('#frameMeta'))
            window_id = page.evaluate('() => window.__sent.find((m) => m.type === "CAPTURE_TAB").windowId')
            self.assertEqual(window_id, 7)
        finally:
            context.close()

    def test_first_panel_open_consumes_capture_and_refuses_changed_tab(self):
        for tab_id, expected in ((101, True), (102, False)):
            context, page = self.new_page()
            try:
                self.open_panel(page, pending={'tabId': tab_id})
                self.assertEqual(page.locator('#visionImg').is_visible(), expected)
                count = page.evaluate('window.__sent.filter(m => m.type === "CAPTURE_TAB").length')
                self.assertEqual(count, int(expected))
            finally:
                context.close()

    def test_capture_request_only_affects_its_own_window(self):
        context, page = self.new_page()
        try:
            self.open_panel(page)
            page.evaluate('() => window.__panelMessages.forEach((fn) => fn({ type: "CAPTURE_REQUEST", windowId: 99 }))')
            page.wait_for_timeout(80)
            self.assertIn('No capture yet', page.inner_text('#frameMeta'))
            page.evaluate('() => { window.__pendingCapture = {tabId:101}; window.__panelMessages.forEach((fn) => fn({ type: "CAPTURE_REQUEST", windowId: 7 })); }')
            page.wait_for_timeout(120)
            self.assertIn('Captured', page.inner_text('#frameMeta'))
        finally:
            context.close()

    def test_restricted_page_reports_instead_of_failing_silently(self):
        restricted = dict(SAMPLE_TAB, url='chrome://settings')
        context, page = self.new_page()
        try:
            self.open_panel(page, tab=restricted, send_error="{ message: 'Could not establish connection.' }")
            page.click('#indexBtn')
            page.wait_for_timeout(120)
            self.assertIn('This page blocks extensions', page.inner_text('#terminalLogs'))
        finally:
            context.close()

    def test_daemon_offline_is_reported(self):
        context, page = self.new_page()
        try:
            self.open_panel(page, daemon={'ok': False, 'connected': False, 'error': 'connection refused'})
            self.assertEqual(page.inner_text('#daemonLabel'), 'Standalone')
            self.assertIn('Dashboard API offline on :4317', page.inner_text('#terminalLogs'))
        finally:
            context.close()

    def test_language_switch_flips_rtl_and_persists(self):
        context, page = self.new_page()
        try:
            self.open_panel(page)
            page.click('#captureBtn')
            page.wait_for_timeout(120)
            page.click('#langToggle')
            page.wait_for_timeout(150)
            self.assertEqual(page.get_attribute('html', 'dir'), 'rtl')
            self.assertEqual(page.inner_text('#indexBtn .tool-name'), 'ترقيم الصفحة')
            self.assertIn('تم الالتقاط', page.inner_text('#frameMeta'))
            self.assertEqual(page.evaluate('() => window.__stored["crewloom.lang"]'), 'ar')
            self.assertIn('تم تبديل اللغة', page.inner_text('#terminalLogs'))

            page.reload()
            page.wait_for_timeout(150)
            self.assertEqual(page.get_attribute('html', 'dir'), 'rtl')
            self.assertEqual(page.inner_text('#captureBtn .tool-name'), 'التقاط الرؤية')
        finally:
            context.close()


class ContentScriptTest(unittest.TestCase):
    """In-page grounding: bounding cap, overlay isolation, and re-anchoring."""

    @classmethod
    def setUpClass(cls):
        cls.playwright = _playwright()
        if cls.playwright is None:
            raise unittest.SkipTest('Playwright is not installed')
        cls.manager = cls.playwright().start()
        cls.browser = _launch(cls.manager)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'browser', None):
            cls.browser.close()
        if getattr(cls, 'manager', None):
            cls.manager.stop()

    def fixture(self, page, count):
        buttons = ''.join(
            f'<button id="b{i}" style="position:absolute;top:{i * 40}px;left:20px;'
            f'width:120px;height:24px">Item {i}</button>'
            for i in range(count)
        )
        page.set_content(
            f'<html><head><style>body{{margin:0;height:6000px}}</style></head>'
            f'<body>{buttons}<a href="#x">link</a></body></html>'
        )
        page.add_style_tag(path=str(EXTENSION / 'content.css'))
        page.add_script_tag(content=CONTENT_MOCK)
        page.add_script_tag(path=str(EXTENSION / 'content.js'))

    def new_page(self):
        context = self.browser.new_context(viewport={'width': 800, 'height': 600})
        return context, context.new_page()

    def test_index_never_exports_entered_form_values(self):
        context, page = self.new_page()
        try:
            self.fixture(page, 1)
            page.evaluate("""() => {
              document.body.insertAdjacentHTML('beforeend', '<input type="password" aria-label="Password"><input type="text" placeholder="Email"><textarea aria-label="Private note"></textarea>');
              document.querySelectorAll('input,textarea').forEach(el => el.value = 'PRIVATE_SENTINEL_47');
            }""")
            result = page.evaluate('indexInteractiveElements()')
            self.assertNotIn('PRIVATE_SENTINEL_47', json.dumps(result))
            self.assertIn('Password', json.dumps(result))
        finally:
            context.close()

    def test_indexing_is_capped_and_reports_totals(self):
        context, page = self.new_page()
        try:
            self.fixture(page, 450)
            result = page.evaluate('() => indexInteractiveElements()')
            self.assertEqual(result['total'], 451)
            self.assertEqual(len(result['items']), 400)
            self.assertTrue(result['truncated'])
            self.assertEqual(page.locator('.crewloom-indexed-tag').count(), 400)
            self.assertEqual(page.locator('.crewloom-indexed-element').count(), 400)
        finally:
            context.close()

    def test_tags_ignore_page_styling_and_re_anchor_on_scroll(self):
        context, page = self.new_page()
        try:
            self.fixture(page, 20)
            page.evaluate('() => indexInteractiveElements()')
            before = page.evaluate("""() => {
              const el = document.getElementById('b10');
              const tag = [...document.querySelectorAll('.crewloom-indexed-tag')]
                .find((t) => t.textContent === '[11]');
              const r = el.getBoundingClientRect();
              return { dx: parseFloat(tag.style.left) - (r.left + window.scrollX),
                       dy: parseFloat(tag.style.top) - (r.top + window.scrollY) };
            }""")
            self.assertEqual(before['dx'], 0)
            self.assertEqual(before['dy'], -16)

            page.evaluate('() => window.scrollTo(0, 300)')
            page.wait_for_timeout(120)
            after = page.evaluate("""() => {
              const el = document.getElementById('b10');
              const tag = [...document.querySelectorAll('.crewloom-indexed-tag')]
                .find((t) => t.textContent === '[11]');
              const r = el.getBoundingClientRect();
              return { dx: parseFloat(tag.style.left) - (r.left + window.scrollX),
                       dy: parseFloat(tag.style.top) - (r.top + window.scrollY),
                       overlayPointer: getComputedStyle(document.getElementById('crewloom-grounding-overlay')).pointerEvents };
            }""")
            self.assertEqual(after['dx'], 0)
            self.assertEqual(after['dy'], -16)
            self.assertEqual(after['overlayPointer'], 'none')
        finally:
            context.close()

    def test_clear_removes_every_trace(self):
        context, page = self.new_page()
        try:
            self.fixture(page, 12)
            page.evaluate('() => indexInteractiveElements()')
            page.evaluate('() => clearAllIndexTags()')
            self.assertEqual(page.locator('.crewloom-indexed-tag').count(), 0)
            self.assertEqual(page.locator('.crewloom-indexed-element').count(), 0)
            self.assertEqual(page.evaluate("() => document.querySelectorAll('[data-crewloom-index]').length"), 0)
        finally:
            context.close()

    def test_click_refuses_spoofed_attributes_stale_generation_and_hidden_targets(self):
        context, page = self.new_page()
        try:
            self.fixture(page, 3)
            result = page.evaluate("""() => {
              window.hits = [];
              const spoof = document.createElement('div'); spoof.dataset.crewloomIndex = '1';
              spoof.style.display = 'none'; spoof.onclick = () => window.hits.push('spoof');
              document.body.prepend(spoof);
              const intended = document.getElementById('b0'); intended.onclick = () => window.hits.push('intended');
              const indexed = indexInteractiveElements();
              const click = clickElementByIndex(1, indexed.generation);
              intended.style.display = 'none';
              const hidden = clickElementByIndex(1, indexed.generation);
              intended.remove(); const removed = clickElementByIndex(1, indexed.generation);
              indexInteractiveElements(); const stale = clickElementByIndex(1, indexed.generation);
              return {click,hidden,removed,stale,hits:window.hits};
            }""")
            self.assertTrue(result['click']['ok']); self.assertEqual(result['hits'], ['intended'])
            for kind in ('hidden', 'removed', 'stale'): self.assertFalse(result[kind]['ok'])
        finally:
            context.close()

    def test_disabled_control_blocks_content_actions_and_clears_overlay(self):
        context, page = self.new_page()
        try:
            self.fixture(page, 3)
            page.evaluate('() => indexInteractiveElements()')
            result = page.evaluate("""() => {
              window.__enabled = false;
              window.__controlChanged({'crewloom.enabled': {newValue:false}}, 'local');
              let reply; window.__contentMessages[0]({type:'INDEX_PAGE'}, {}, r => reply = r);
              return {reply,tags:document.querySelectorAll('.crewloom-indexed-tag').length};
            }""")
            self.assertFalse(result['reply']['ok']); self.assertEqual(result['tags'], 0)
        finally:
            context.close()

    def test_click_by_index_dispatches_a_real_event(self):
        context, page = self.new_page()
        try:
            self.fixture(page, 5)
            page.evaluate('() => indexInteractiveElements()')
            page.evaluate("() => { window.__hits = 0; document.getElementById('b2').addEventListener('click', () => window.__hits++); }")
            result = page.evaluate('() => clickElementByIndex(3)')
            self.assertTrue(result['ok'])
            self.assertEqual(result['tag'], 'button')
            self.assertEqual(page.evaluate('() => window.__hits'), 1)
            self.assertEqual(page.evaluate('() => clickElementByIndex(99).ok'), False)
        finally:
            context.close()


@unittest.skipUnless(os.environ.get('CREWLOOM_REAL_BROWSER') == '1',
                     'set CREWLOOM_REAL_BROWSER=1 to load the unpacked extension in a real browser')
class RealBrowserExtensionTest(unittest.TestCase):
    """Load the unpacked extension in Chromium against a synthetic HTTP page.

    Headless Chromium does not load unpacked extensions, so this class needs a headed
    browser and a synthetic HTTP fixture. It is the only check that can catch a
    manifest the browser rejects, such as a missing capture permission.
    """

    DASHBOARD = 'http://localhost:4317/'

    @classmethod
    def setUpClass(cls):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        import threading
        class Fixture(BaseHTTPRequestHandler):
            def do_GET(self):
                data = b'<html><body><button id="fixture-button">Synthetic fixture</button><input placeholder="fixture"></body></html>'
                self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(data)
            def log_message(self, *args): pass
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Fixture)
        cls.DASHBOARD = 'http://127.0.0.1:' + str(cls.server.server_port) + '/'
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.server_thread.start()
        cls.playwright = _playwright()
        if cls.playwright is None:
            raise unittest.SkipTest('Playwright is not installed')
        cls.manager = cls.playwright().start()
        cls.profile = tempfile.mkdtemp(prefix='crewloom-extension-')
        try:
            cls.context = cls.manager.chromium.launch_persistent_context(
                cls.profile,
                headless=False,
                viewport={'width': 1280, 'height': 900},
                args=[f'--disable-extensions-except={EXTENSION}',
                      f'--load-extension={EXTENSION}'],
            )
        except Exception as exc:  # pragma: no cover - depends on local browser build
            cls.manager.stop()
            raise unittest.SkipTest(f'could not launch a browser for extension loading: {exc}')

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'context', None):
            cls.context.close()
        if getattr(cls, 'manager', None):
            cls.manager.stop()
        if getattr(cls, 'server', None): cls.server.shutdown(); cls.server.server_close()
        if getattr(cls, 'profile', None):
            import shutil
            shutil.rmtree(cls.profile)

    def worker_id(self):
        for _ in range(40):
            if self.context.service_workers:
                return self.context.service_workers[0].url.split('/')[2]
            time.sleep(0.25)
        self.fail('the extension service worker never registered')

    def setUp(self):
        self.page = self.context.new_page()
        self.page.goto(self.DASHBOARD, wait_until='domcontentloaded')
        self.extension_id = self.worker_id()
        self.panel = self.context.new_page()
        self.panel.goto(f'chrome-extension://{self.extension_id}/sidepanel.html')
        self.panel.wait_for_timeout(1200)
        self.panel.evaluate("async () => await chrome.runtime.sendMessage({type:'SET_CONTROL',enabled:true})")
        self.page.bring_to_front()

    def tearDown(self):
        for page in (self.panel, self.page):
            if page and not page.is_closed():
                page.close()

    def tab_id(self):
        return self.panel.evaluate(
            """async () => {
              const [active] = await chrome.tabs.query({ active: true, currentWindow: true });
              return active?.id ?? null;
            }"""
        )

    def send_to_tab(self, message):
        return self.panel.evaluate(
            """async ([tabId, message]) => await chrome.tabs.sendMessage(tabId, message)""",
            [self.tab_id(), message],
        )

    def test_browser_accepts_the_manifest(self):
        manifest = self.panel.evaluate('() => chrome.runtime.getManifest()')
        declared = json.loads((EXTENSION / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['version'], declared['version'])
        self.assertIn('<all_urls>', manifest['host_permissions'],
                      'captureVisibleTab needs <all_urls> or a transient activeTab grant')

    def test_panel_reports_the_live_dashboard(self):
        self.assertIn(self.panel.inner_text('#daemonLabel'), ('Online :4317', 'Standalone'))
        self.assertIn('Panel ready', self.panel.inner_text('#terminalLogs'))

    def test_indexing_paints_grounding_tags_and_hud(self):
        result = self.send_to_tab({'type': 'INDEX_PAGE'})
        self.assertTrue(result['ok'])
        self.assertGreater(result['count'], 0)
        self.page.wait_for_timeout(400)
        self.assertEqual(self.page.locator('.crewloom-indexed-tag').count(), result['count'])
        self.assertTrue(self.page.evaluate(
            "() => { const i = document.querySelector('.crewloom-hud-logo');"
            ' return !!i && i.complete && i.naturalWidth > 0; }'
        ), 'the HUD logo needs a web_accessible_resources entry')

    def test_click_by_index_dispatches_a_real_event(self):
        result = self.send_to_tab({'type': 'INDEX_PAGE'})
        self.assertFalse(self.send_to_tab({'type': 'CLICK_INDEX', 'index': 1})['ok'])
        self.page.evaluate("() => { window.__hits = 0;"
                           " document.addEventListener('click', () => window.__hits++, true); }")
        response = self.send_to_tab({'type': 'CLICK_INDEX', 'index': result['items'][0]['index'], 'generation': result['generation']})
        self.assertTrue(response['ok'])
        self.page.wait_for_timeout(500)
        self.assertGreaterEqual(self.page.evaluate('() => window.__hits'), 1)

    def test_disabled_content_and_capture_are_refused_and_state_survives_reload(self):
        self.panel.evaluate("async () => await chrome.runtime.sendMessage({type:'SET_CONTROL',enabled:false})")
        self.assertFalse(self.send_to_tab({'type':'INDEX_PAGE'})['ok'])
        reply = self.panel.evaluate("async () => await chrome.runtime.sendMessage({type:'CAPTURE_TAB',windowId:1})")
        self.assertFalse(reply['ok'])
        self.panel.reload()
        state = self.panel.evaluate("async () => await chrome.runtime.sendMessage({type:'GET_CONTROL'})")
        self.assertFalse(state['enabled'])

    def test_visible_tab_capture_returns_a_frame(self):
        self.page.bring_to_front()
        capture = self.panel.evaluate("""async () => {
          const [active] = await chrome.tabs.query({ active: true, currentWindow: true });
          return await new Promise((resolve) => chrome.runtime.sendMessage(
            { type: 'CAPTURE_TAB', windowId: active.windowId }, resolve));
        }""")
        self.assertTrue(capture['ok'], capture.get('error'))
        self.assertTrue(capture['dataUrl'].startswith('data:image/png;base64,'))

    def test_clear_removes_the_overlay_from_the_real_page(self):
        self.send_to_tab({'type': 'INDEX_PAGE'})
        self.page.wait_for_timeout(300)
        self.send_to_tab({'type': 'CLEAR_INDEX'})
        self.page.wait_for_timeout(200)
        self.assertEqual(self.page.locator('.crewloom-indexed-tag').count(), 0)


@unittest.skipUnless(os.environ.get('CREWLOOM_SCREENSHOTS') == '1', 'set CREWLOOM_SCREENSHOTS=1 to refresh preview images')
class SidePanelScreenshotTest(SidePanelHarness):
    """Opt-in preview refresh for the documentation images."""

    def test_write_preview_images(self):
        ASSETS.mkdir(parents=True, exist_ok=True)
        context, page = self.new_page()
        try:
            self.open_panel(page)
            page.click('#indexBtn')
            page.wait_for_timeout(150)
            page.click('#captureBtn')
            page.wait_for_timeout(150)
            page.screenshot(path=str(ASSETS / 'crewloom_sidepanel_en.png'), full_page=True)
            page.click('#langToggle')
            page.wait_for_timeout(250)
            page.screenshot(path=str(ASSETS / 'crewloom_sidepanel_ar.png'), full_page=True)
        finally:
            context.close()


if __name__ == '__main__':
    unittest.main()