"""Commit index authority stays in the parent gate, never in fixture subprocesses."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_repository import run_suites
from test_repository_gate import build_root


class GateEnvironmentTests(unittest.TestCase):
    def test_fixture_children_do_not_inherit_the_commit_index(self):
        module = """import os
import unittest

class FixtureEnvironmentTests(unittest.TestCase):
    def test_git_scope(self):
        self.assertFalse('GIT_INDEX_FILE' in os.environ, 'fixture inherited commit index')
        self.assertFalse('GIT_DIR' in os.environ, 'fixture inherited parent repository')
        self.assertEqual(os.environ['CREWLOOM_GATE_SENTINEL'], 'preserved')
"""
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory, {'scripts/test_scope.py': module})
            index = root / 'commit-index'
            index.write_bytes(b'parent index must remain untouched')
            environment = {'GIT_INDEX_FILE': str(index), 'GIT_DIR': str(root / '.git'),
                           'CREWLOOM_GATE_SENTINEL': 'preserved'}
            with patch.dict(os.environ, environment):
                self.assertEqual(run_suites(root), 0)
                self.assertEqual(os.environ['GIT_INDEX_FILE'], str(index))
            self.assertEqual(index.read_bytes(), b'parent index must remain untouched')


if __name__ == '__main__':
    unittest.main()
