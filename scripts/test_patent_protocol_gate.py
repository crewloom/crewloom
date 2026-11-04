"""Publication must fail closed when only document structure was checked."""
import contextlib
import io
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path
from verify_patent_protocol import audit_document


class PatentGateTests(unittest.TestCase):
    def test_plausible_structure_does_not_certify_fabricated_evidence(self):
        text = """INVENTOR: The Owner
## 1. ABSTRACT
The fastest mechanism ever; fabricated citation arXiv:9999.99999.
## 2. BACKGROUND
TRIZ
## 3. DETAILED
$$ nonsense $$
| Metric | Baseline |
## 4. CLAIMS
Independent System Claim 1: comprising an imaginary mechanism.
Claim 2: nothing.
Claim 3: nothing.
Claim 4: nothing.
""" + ('Unsupported assertions. ' * 30)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'paper.md'
            path.write_text(text, encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertNotEqual(audit_document(str(path)), 0)

    def test_explicit_structure_mode_cannot_approve_publication(self):
        fixture = """INVENTOR: The Owner
## 1. ABSTRACT
## 2. BACKGROUND
TRIZ
## 3. DETAILED
$$ nonsense $$
| Metric | Baseline |
## 4. CLAIMS
Independent System Claim 1: comprising a mechanism.
Claim 2: nothing.
Claim 3: nothing.
Claim 4: nothing.
""" + ('Unsupported assertions. ' * 30)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'paper.md'
            path.write_text(fixture, encoding='utf-8')
            command = [sys.executable, str(Path(__file__).with_name('verify_patent_protocol.py')), str(path)]
            structure = subprocess.run(command + ['--structure-only'], capture_output=True, text=True)
            self.assertEqual(structure.returncode, 0, structure.stderr)
            self.assertIn('not scientific, legal, or publication approval', structure.stdout)
            self.assertNotIn('fully complies', structure.stdout)
            publication = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(publication.returncode, 0)
            self.assertIn('Publication blocked', publication.stderr)
            path.write_text('invalid manuscript', encoding='utf-8')
            invalid = subprocess.run(command + ['--structure-only'], capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0)


if __name__ == '__main__':
    unittest.main()
