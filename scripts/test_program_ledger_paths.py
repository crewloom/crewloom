"""The shipped ledger belongs to this checkout, regardless of its folder name."""
import runpy
import shutil
import tempfile
import unittest
from pathlib import Path


class LedgerCheckoutPathTests(unittest.TestCase):
    def test_renamed_checkout_resolves_its_own_shipped_ledger(self):
        with tempfile.TemporaryDirectory() as temporary:
            checkout = Path(temporary) / 'renamed-checkout'
            scripts = checkout / 'scripts'
            scripts.mkdir(parents=True)
            source = Path(__file__).with_name('program_ledger.py')
            shutil.copy2(source, scripts / source.name)
            ledger = checkout / 'Brain' / 'computer-use-program' / 'ledger.json'
            ledger.parent.mkdir(parents=True)
            ledger.write_text('{}', encoding='utf-8')
            module = runpy.run_path(str(scripts / source.name))
            self.assertEqual(module['DEFAULT_LEDGER'], ledger.resolve())
            self.assertTrue(module['DEFAULT_LEDGER'].is_file())
