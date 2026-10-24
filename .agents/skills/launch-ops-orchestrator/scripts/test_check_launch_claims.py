import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import check_launch_claims as tool


def run(text, inventory=None, *extra):
    with tempfile.TemporaryDirectory() as directory:
        copy = Path(directory) / 'copy.md'
        copy.write_text(text, encoding='utf-8')
        args = ['--file', str(copy), *extra]
        if inventory is not None:
            inv = Path(directory) / 'inventory.md'
            inv.write_text(inventory, encoding='utf-8')
            args += ['--inventory', str(inv)]
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = tool.main(args)
        return code, out.getvalue()


class ClaimTests(unittest.TestCase):
    def test_honest_copy_passes(self):
        code, out = run('Crewloom is an early preview (0.1.0) that shows files changed and test results.')
        self.assertEqual(code, 0, out)

    def test_latency_number_is_flagged(self):
        code, out = run('Reasoning latency of 0.8ms and a 58 KB binary.')
        self.assertEqual(code, 1)
        self.assertIn('measured-number', out)

    def test_competitor_comparison_english_and_arabic(self):
        for text in ('Crewloom is better than Claude Code.', 'Crewloom beats Devin on every task.',
                     'بديل لـ كلود كود وأسرع من ديفين'):
            code, out = run(text)
            self.assertEqual(code, 1, text)
            self.assertIn('competitor-comparison', out, text)

    def test_guarantees_superlatives_and_readiness(self):
        code, out = run('100% safe. The best agent. Production-ready, benchmarked, we guarantee it.')
        self.assertEqual(code, 1)
        for rule in ('absolute-guarantee', 'superlative', 'production-ready', 'unverified-benchmark'):
            self.assertIn(rule, out)

    def test_inventory_whitelists_verified_claim(self):
        text = 'Desktop web build passes 25 node tests.\nIt is 100% offline.'
        code, out = run(text, '# verified\n25 node tests\n')
        self.assertEqual(code, 1)
        self.assertNotIn('line 1', out)
        self.assertIn('line 2', out)

    def test_missing_file_exits_two(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(tool.main(['--file', '/nonexistent/copy.md']), 2)


if __name__ == '__main__':
    unittest.main()
