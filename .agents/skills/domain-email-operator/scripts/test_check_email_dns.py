import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import check_email_dns as tool

GOOD = {
    'MX crewloom.org': ['58 route1.mx.cloudflare.net.'],
    'TXT crewloom.org': ['"v=spf1 include:_spf.mx.cloudflare.net ~all"', '"brevo-code:de41341309511d12b8add3696e44c805"'],
    'TXT _dmarc.crewloom.org': ['"v=DMARC1; p=none; rua=mailto:rua@dmarc.brevo.com"'],
    'CNAME brevo1._domainkey.crewloom.org': ['b1.crewloom-org.dkim.brevo.com.'],
    'CNAME brevo2._domainkey.crewloom.org': ['b2.crewloom-org.dkim.brevo.com.'],
}


def run(records, *extra):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'records.json'
        path.write_text(json.dumps(records), encoding='utf-8')
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = tool.main(['--domain', 'crewloom.org', '--records-json', str(path), *extra])
        return code, out.getvalue(), err.getvalue()


class EmailDnsTests(unittest.TestCase):
    def test_complete_setup_passes(self):
        code, out, _ = run(GOOD, '--sender', 'brevo')
        self.assertEqual(code, 0, out)
        self.assertIn('PASS', out)

    def test_duplicate_spf_is_reported(self):
        records = dict(GOOD)
        records['TXT crewloom.org'] = GOOD['TXT crewloom.org'] + ['"v=spf1 include:spf.brevo.com ~all"']
        code, out, _ = run(records)
        self.assertEqual(code, 1)
        self.assertIn('spf-multiple', out)

    def test_missing_dmarc_and_dkim_are_reported(self):
        records = {key: value for key, value in GOOD.items()
                   if '_dmarc' not in key and 'brevo2' not in key}
        code, out, _ = run(records, '--sender', 'brevo')
        self.assertEqual(code, 1)
        self.assertIn('dmarc-missing', out)
        self.assertIn('dkim-brevo2-missing', out)

    def test_wrong_dkim_target_is_reported(self):
        records = dict(GOOD)
        records['CNAME brevo1._domainkey.crewloom.org'] = ['evil.example.net.']
        code, out, _ = run(records, '--sender', 'brevo')
        self.assertEqual(code, 1)
        self.assertIn('dkim-brevo1-target', out)

    def test_brevo_records_are_optional_without_sender(self):
        records = {key: value for key, value in GOOD.items() if 'brevo' not in key.lower() or key.startswith('TXT _dmarc')}
        records['TXT crewloom.org'] = [GOOD['TXT crewloom.org'][0]]
        code, _, _ = run(records)
        self.assertEqual(code, 0)

    def test_invalid_input_exits_two(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(tool.main(['--domain', 'not a domain']), 2)
        with contextlib.redirect_stderr(err):
            self.assertEqual(tool.main(['--domain', 'crewloom.org', '--records-json', '/nonexistent.json']), 2)

    def test_joined_txt_chunks_are_cleaned(self):
        self.assertEqual(tool.clean('"v=spf1 include:a " "include:b ~all"'), 'v=spf1 include:a include:b ~all')


if __name__ == '__main__':
    unittest.main()
