"""Comprehensive test suite for Crewloom Dual-Speed Browser Seam and Tool Engine.

Tests:
1. URL validation, scheme boundaries, and localhost protection.
2. Bot-check and CAPTCHA detection invariants (English and Arabic).
3. Fast HTML to clean Markdown extraction (headings, links, lists, tables).
4. Token economy invariant (>80% reduction compared to raw DOM/HTML).
5. Interactive browser session lifecycle (navigation, snapshot, click, fill, tabs, history).
6. Error handling and reference validation (@e1, @e2).
7. Model function-calling schema definitions.
"""
import os
import sys
import unittest
from pathlib import Path

# Add scripts directory to path for clean import
sys.path.insert(0, str(Path(__file__).resolve().parent))
import browser_tool as bt


class TestBrowserUrlValidation(unittest.TestCase):
    def test_valid_http_and_https_urls(self):
        self.assertEqual(bt.validate_url("https://example.com/page"), "https://example.com/page")
        self.assertEqual(bt.validate_url("http://api.crewloom.dev/v1"), "http://api.crewloom.dev/v1")

    def test_forbidden_schemes_are_rejected(self):
        for bad_url in ("file:///etc/passwd", "javascript:alert(1)", "ftp://ftp.example.com", "data:text/html,hi"):
            with self.subTest(url=bad_url):
                with self.assertRaises(ValueError) as ctx:
                    bt.validate_url(bad_url)
                self.assertIn("Forbidden URL scheme", str(ctx.exception))

    def test_missing_or_invalid_host(self):
        with self.assertRaises(ValueError):
            bt.validate_url("https://")
        with self.assertRaises(ValueError):
            bt.validate_url("")

    def test_localhost_guarded_by_environment_flag(self):
        # Without flag, localhost is denied
        old_val = os.environ.get("CREWLOOM_ALLOW_LOCAL_BROWSER")
        try:
            os.environ.pop("CREWLOOM_ALLOW_LOCAL_BROWSER", None)
            with self.assertRaises(ValueError) as ctx:
                bt.validate_url("http://127.0.0.1:8080/test")
            self.assertIn("rejected", str(ctx.exception))

            # With flag, localhost is permitted
            os.environ["CREWLOOM_ALLOW_LOCAL_BROWSER"] = "1"
            self.assertEqual(
                bt.validate_url("http://127.0.0.1:8080/test", allow_local=True),
                "http://127.0.0.1:8080/test",
            )
        finally:
            if old_val is not None:
                os.environ["CREWLOOM_ALLOW_LOCAL_BROWSER"] = old_val
            else:
                os.environ.pop("CREWLOOM_ALLOW_LOCAL_BROWSER", None)


class TestBrowserChallengeDetection(unittest.TestCase):
    def test_strong_challenge_markers_detected(self):
        self.assertIsNotNone(bt.detect_browser_challenge("<div class='cf-turnstile'></div>"))
        self.assertIsNotNone(bt.detect_browser_challenge("<script src='https://google.com/recaptcha/api.js'></script>"))
        self.assertIsNotNone(bt.detect_browser_challenge("https://google.com/sorry/index?continue=..."))
        self.assertIsNotNone(bt.detect_browser_challenge("Unfortunately, bots use DuckDuckGo too."))

    def test_arabic_challenge_detected(self):
        self.assertIsNotNone(bt.detect_browser_challenge("الرجاء تحقق من أنك إنسان للمتابعة"))

    def test_long_page_mentioning_words_is_not_flagged(self):
        long_text = "In this article we explain how to verify you are human in modern authentication systems. " + ("lorem ipsum " * 400)
        self.assertIsNone(bt.detect_browser_challenge(long_text))

    def test_empty_content_returns_none(self):
        self.assertIsNone(bt.detect_browser_challenge(""))


class TestHtmlToMarkdownExtraction(unittest.TestCase):
    def test_extract_headings_and_clean_text(self):
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crewloom Overview</title>
            <meta name="description" content="Autonomous AI Agent Fabric">
            <style>body { background: #000; }</style>
            <script>console.log("secret");</script>
        </head>
        <body>
            <h1>Welcome to Crewloom</h1>
            <p>High-performance multi-agent framework.</p>
            <h2>Core Features</h2>
            <ul>
                <li>Dual-speed browser</li>
                <li>Pulse HRPE local model</li>
            </ul>
        </body>
        </html>
        """
        title, desc, md = bt.html_to_clean_markdown(sample_html)
        self.assertEqual(title, "Crewloom Overview")
        self.assertEqual(desc, "Autonomous AI Agent Fabric")
        self.assertIn("# Welcome to Crewloom", md)
        self.assertIn("## Core Features", md)
        self.assertIn("- Dual-speed browser", md)
        self.assertNotIn("console.log", md)
        self.assertNotIn("body { background", md)

    def test_extract_tables(self):
        table_html = """
        <table>
            <tr><th>Agent</th><th>Role</th></tr>
            <tr><td>Torvalds</td><td>Engineering</td></tr>
            <tr><td>Ada</td><td>Systems</td></tr>
        </table>
        """
        _, _, md = bt.html_to_clean_markdown(table_html)
        self.assertIn("| Agent | Role |", md)
        self.assertIn("| --- | --- |", md)
        self.assertIn("| Torvalds | Engineering |", md)

    def test_extract_links(self):
        link_html = '<p>Check out our <a href="https://crewloom.dev/docs">Documentation</a>.</p>'
        _, _, md = bt.html_to_clean_markdown(link_html)
        self.assertIn("[Documentation](https://crewloom.dev/docs)", md)


class TestTokenEconomyInvariant(unittest.TestCase):
    def test_accessibility_snapshot_reduces_token_consumption_by_over_80_percent(self):
        """Council Invariant: Numbered Accessibility Tree must be >80% smaller than raw HTML."""
        bloated_html = f"""
        <html>
        <head>
            <title>Heavy Web App</title>
            <style>{'.css-class {' + ('color: red; padding: 10px; margin: 5px; ' * 50) + '}'}</style>
            <script>{'function analytics() {' + ('console.log("track"); ' * 100) + '}'}</script>
        </head>
        <body>
            <header><nav><div class="wrapper">{'<span>decor</span>' * 80}</div></nav></header>
            <main>
                <h1>User Dashboard</h1>
                <p>{'Important content text for testing. ' * 20}</p>
                <div class="form-container">
                    <button class="btn btn-primary" id="btn-1">Submit Order</button>
                    <a href="https://example.com/help" class="link-styled">Get Help</a>
                    <input type="text" placeholder="Search items" value="" />
                </div>
            </main>
            <footer>{'<div>Copyright Notice 2026</div>' * 30}</footer>
        </body>
        </html>
        """
        raw_size = len(bloated_html)
        seam = bt.BrowserSeam()
        res = seam.interact_page([
            {"op": "open", "url": "https://test.app/dashboard", "html": bloated_html},
            {"op": "snapshot"},
        ], allow_local=True)

        snapshot_size = len(res.snapshot)
        reduction_percentage = ((raw_size - snapshot_size) / raw_size) * 100

        self.assertGreater(
            reduction_percentage,
            80.0,
            f"Expected >80% size reduction, but got {reduction_percentage:.1f}% (raw: {raw_size}, snapshot: {snapshot_size})",
        )
        self.assertIn("[@e1] (button) \"Submit Order\"", res.snapshot)
        self.assertIn("[@e2] (link) \"Get Help\"", res.snapshot)
        self.assertIn("[@e3] (input:text) \"Search items\"", res.snapshot)


class TestInteractiveBrowserOperations(unittest.TestCase):
    def setUp(self):
        self.seam = bt.BrowserSeam()
        self.html = """
        <html>
        <body>
            <h1>Test Page</h1>
            <button id="b1">Click Me</button>
            <input type="text" placeholder="Username" value="guest" />
            <a href="https://example.com/next">Next Page</a>
        </body>
        </html>
        """

    def test_open_and_snapshot(self):
        res = self.seam.interact_page([
            {"op": "open", "url": "https://example.com/home", "html": self.html},
            {"op": "snapshot"},
        ])
        self.assertFalse(res.is_error)
        self.assertEqual(len(res.elements), 3)
        self.assertEqual(res.elements[0].ref, "@e1")
        self.assertEqual(res.elements[0].role, "button")
        self.assertEqual(res.elements[0].name, "Click Me")

    def test_click_and_fill(self):
        # 1. Open and snapshot
        res1 = self.seam.interact_page([
            {"op": "open", "url": "https://example.com/home", "html": self.html},
            {"op": "snapshot"},
        ], session_id="test_sess_1")

        # 2. Click button @e1 and fill input @e2
        res2 = self.seam.interact_page([
            {"op": "click", "ref": "@e1"},
            {"op": "fill", "ref": "@e2", "text": "ashraf"},
        ], session_id="test_sess_1")

        self.assertFalse(res2.is_error)
        self.assertIn("Clicked @e1 (Click Me)", res2.output)
        self.assertIn("Filled @e2 with 'ashraf'", res2.output)

    def test_invalid_reference_fails_gracefully(self):
        res = self.seam.interact_page([
            {"op": "open", "url": "https://example.com/home", "html": self.html},
            {"op": "click", "ref": "@e999"},
        ])
        self.assertTrue(res.is_error)
        self.assertIn("Invalid or stale element reference '@e999'", res.output)

    def test_tab_lifecycle(self):
        sid = "tabs_test_session"
        # Open tab
        res1 = self.seam.interact_page([{"op": "open", "url": "https://example.com/page1"}], session_id=sid)
        self.assertEqual(res1.active_tab, "t1")

        # Create new tab
        res2 = self.seam.interact_page([{"op": "create_tab", "url": "https://example.com/page2"}], session_id=sid)
        self.assertEqual(res2.active_tab, "t2")

        # List tabs
        res3 = self.seam.interact_page([{"op": "tabs"}], session_id=sid)
        self.assertIn("[t1]", res3.output)
        self.assertIn("[t2]", res3.output)

        # Switch back to t1
        res4 = self.seam.interact_page([{"op": "select_tab", "tab_id": "t1"}], session_id=sid)
        self.assertEqual(res4.active_tab, "t1")

        # Close t2
        res5 = self.seam.interact_page([{"op": "close_tab", "tab_id": "t2"}], session_id=sid)
        self.assertFalse(res5.is_error)

        # Attempting to close last remaining tab is refused
        res6 = self.seam.interact_page([{"op": "close_tab", "tab_id": "t1"}], session_id=sid)
        self.assertTrue(res6.is_error)
        self.assertIn("cannot close the last tab", res6.output)

    def test_history_navigation(self):
        sid = "history_test"
        self.seam.interact_page([{"op": "open", "url": "https://example.com/1", "html": "<h1>P1</h1>"}], session_id=sid)
        self.seam.interact_page([{"op": "open", "url": "https://example.com/2", "html": "<h1>P2</h1>"}], session_id=sid)
        res_back = self.seam.interact_page([{"op": "back"}], session_id=sid)
        self.assertIn("Navigated back to https://example.com/1", res_back.output)

        res_fwd = self.seam.interact_page([{"op": "forward"}], session_id=sid)
        self.assertIn("Navigated forward to https://example.com/2", res_fwd.output)

    def test_screenshot_generation(self):
        res = self.seam.interact_page([
            {"op": "open", "url": "https://example.com/test", "html": "<h1>Visual Page</h1>"},
            {"op": "screenshot"},
        ])
        self.assertIn("Screenshot taken: data:image/svg+xml;base64,", res.output)


class TestToolDefinitions(unittest.TestCase):
    def test_schema_conformance(self):
        defs = bt.get_tool_definitions()
        self.assertEqual(len(defs), 2)
        names = [d["function"]["name"] for d in defs]
        self.assertIn("browse_url", names)
        self.assertIn("browser", names)

        # Verify browse_url schema
        browse_tool = next(d for d in defs if d["function"]["name"] == "browse_url")
        self.assertEqual(browse_tool["function"]["parameters"]["required"], ["url"])

        # Verify browser tool schema
        browser_tool = next(d for d in defs if d["function"]["name"] == "browser")
        self.assertEqual(browser_tool["function"]["parameters"]["required"], ["op"])
        self.assertIn("snapshot", browser_tool["function"]["parameters"]["properties"]["op"]["enum"])


if __name__ == "__main__":
    unittest.main()
