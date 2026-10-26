#!/usr/bin/env python3
"""Tests for the resumable programme ledger."""
import json
import tempfile
import threading
import unittest
from datetime import timedelta
from pathlib import Path

import scripts.program_ledger as pl


def make_ledger(extra=None):
    packages = {
        "WP-00": {"title": "base", "lane": "foundation", "depends_on": [], "owns": ["src/a"], "status": "todo"},
        "WP-01": {"title": "next", "lane": "core", "depends_on": ["WP-00"], "owns": ["src/b"], "status": "todo"},
        "WP-02": {"title": "overlap", "lane": "core", "depends_on": [], "owns": ["src/a/inner"], "status": "todo"},
        "WP-03": {"title": "later", "lane": "core", "depends_on": [], "owns": ["src/c"], "status": "dormant", "optional": True},
    }
    packages.update(extra or {})
    return {"schema": 1, "lease_minutes": 60, "packages": packages, "log": []}


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "ledger.json"
        pl.write_ledger(self.path, make_ledger())
        self.now = pl.utcnow()

    def test_dependencies_gate_claims(self):
        data = pl.read_ledger(self.path)
        self.assertEqual(pl.claim_state(data, "WP-01", self.now), "waiting-deps")
        with self.assertRaises(pl.LedgerError):
            pl.do_claim(data, "WP-01", "a", self.now)

    def test_overlapping_owned_paths_block_parallel_claim(self):
        data = pl.read_ledger(self.path)
        pl.do_claim(data, "WP-00", "a", self.now)
        self.assertEqual(pl.claim_state(data, "WP-02", self.now), "path-conflict")

    def test_dormant_is_not_offered_until_activated(self):
        data = pl.read_ledger(self.path)
        self.assertNotIn("WP-03", pl.next_candidates(data, self.now))
        pl.do_activate(data, "WP-03", "a", "ADR-001 decided to build", self.now)
        self.assertIn("WP-03", pl.next_candidates(data, self.now))

    def test_done_requires_evidence_and_unlocks_dependents(self):
        data = pl.read_ledger(self.path)
        pl.do_claim(data, "WP-00", "a", self.now)
        with self.assertRaises(pl.LedgerError):
            pl.do_done(data, "WP-00", "a", ["ok"], self.now, self.root)
        (self.root / "src" / "a").mkdir(parents=True)
        (self.root / "src" / "a" / "f.txt").write_text("x")
        count = pl.do_done(data, "WP-00", "a", ["pnpm exec vitest run -> 3 passed, 0 failed"], self.now, self.root)
        self.assertEqual(count, 1)
        self.assertEqual(pl.claim_state(data, "WP-01", self.now), "claimable")

    def test_stale_claim_needs_explicit_takeover(self):
        data = pl.read_ledger(self.path)
        pl.do_claim(data, "WP-00", "a", self.now)
        later = self.now + timedelta(minutes=61)
        self.assertEqual(pl.claim_state(data, "WP-00", later), "takeover")
        with self.assertRaises(pl.LedgerError):
            pl.do_claim(data, "WP-00", "b", later)
        pl.do_claim(data, "WP-00", "b", later, takeover=True)
        self.assertEqual(data["packages"]["WP-00"]["claimed_by"], "b")

    def test_only_owner_can_checkpoint(self):
        data = pl.read_ledger(self.path)
        pl.do_claim(data, "WP-00", "a", self.now)
        with self.assertRaises(pl.LedgerError):
            pl.do_checkpoint(data, "WP-00", "b", "step 1 done, next step 2, file x", self.now)
        pl.do_checkpoint(data, "WP-00", "a", "step 1 done, next step 2, file x", self.now)
        self.assertEqual(len(data["packages"]["WP-00"]["checkpoints"]), 1)

    def test_manifest_detects_drift(self):
        (self.root / "src" / "a").mkdir(parents=True)
        target = self.root / "src" / "a" / "f.txt"
        target.write_text("one")
        recorded = pl.manifest(["src/a"], self.root)
        target.write_text("two")
        (self.root / "src" / "a" / "g.txt").write_text("new")
        drift = pl.manifest_drift(recorded, pl.manifest(["src/a"], self.root))
        self.assertEqual(drift["changed"], ["src/a/f.txt"])
        self.assertEqual(drift["added"], ["src/a/g.txt"])

    def test_rebaseline_accepts_legitimate_followup_changes(self):
        data = pl.read_ledger(self.path)
        pl.do_claim(data, "WP-00", "a", self.now)
        (self.root / "src" / "a").mkdir(parents=True)
        target = self.root / "src" / "a" / "f.txt"
        target.write_text("one")
        pl.do_done(data, "WP-00", "a", ["pnpm exec vitest run -> 3 passed, 0 failed"], self.now, self.root)
        target.write_text("two")
        self.assertEqual(pl.manifest_drift(data["packages"]["WP-00"]["manifest"], pl.manifest(["src/a"], self.root))["changed"], ["src/a/f.txt"])
        with self.assertRaises(pl.LedgerError):
            pl.do_rebaseline(data, "WP-00", "b", "short", self.now, self.root)
        pl.do_rebaseline(data, "WP-00", "b", "WP-99 fixed f.txt after review", self.now, self.root)
        self.assertEqual(pl.manifest_drift(data["packages"]["WP-00"]["manifest"], pl.manifest(["src/a"], self.root))["changed"], [])
        self.assertEqual(len(data["packages"]["WP-00"]["rebaselines"]), 1)

    def test_add_package_rejects_duplicates_and_incomplete_specs(self):
        data = pl.read_ledger(self.path)
        spec = {"title": "fix", "lane": "fix", "role": "r", "depends_on": ["WP-00"], "owns": ["src/z"]}
        pl.do_add_package(data, "WP-90", spec, "a", self.now)
        self.assertEqual(data["packages"]["WP-90"]["status"], "todo")
        with self.assertRaises(pl.LedgerError):
            pl.do_add_package(data, "WP-90", spec, "a", self.now)
        with self.assertRaises(pl.LedgerError):
            pl.do_add_package(data, "WP-91", {"title": "x"}, "a", self.now)

    def test_validate_reports_cycles_unknown_deps_and_missing_sections(self):
        data = make_ledger({"WP-09": {"title": "x", "lane": "l", "depends_on": ["WP-10"], "owns": ["p"], "status": "todo"},
                            "WP-10": {"title": "y", "lane": "l", "depends_on": ["WP-09", "WP-99"], "owns": ["q"], "status": "todo"}})
        problems = "\n".join(pl.validate(data, "### WP-00 \n"))
        self.assertIn("dependency cycle", problems)
        self.assertIn("unknown dependency WP-99", problems)
        self.assertIn("no '### WP-01 ' section", problems)

    def test_concurrent_claims_have_exactly_one_winner(self):
        winners = []

        def attempt(name):
            try:
                pl.mutate(self.path, lambda data: pl.do_claim(data, "WP-00", name, pl.utcnow()))
                winners.append(name)
            except pl.LedgerError:
                pass

        threads = [threading.Thread(target=attempt, args=(f"agent-{index}",)) for index in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(len(winners), 1)
        self.assertEqual(pl.read_ledger(self.path)["packages"]["WP-00"]["claimed_by"], winners[0])

    def test_shipped_ledger_is_structurally_valid(self):
        data = pl.read_ledger(pl.DEFAULT_LEDGER)
        text = pl.DEFAULT_WORK_PACKAGES.read_text(encoding="utf-8")
        self.assertEqual(pl.validate(data, text), [])
        json.dumps(data)


if __name__ == "__main__":
    unittest.main()
