"""Driver-independent bad/clean scope and one-use AX action contracts."""
import asyncio
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import native_desktop as nd
import test_user_context


class FakeDriver:
    def __init__(self): self.calls = []; self.count = 0; self.foreign = False
    async def call_tool(self, name, args):
        self.calls.append((name, args))
        if name == 'check_permissions': value = {'accessibility': True}
        elif name == 'list_apps': value = {'apps': [{'bundle_id': 'foreign' if self.foreign else 'com.crewloom.NativeFixture', 'pid': 42, 'running': True}]}
        elif name == 'list_windows': value = {'windows': [{'pid': 42, 'window_id': 7, 'title': 'Crewloom Native Acceptance'}]}
        elif name == 'get_window_state':
            value = {'elements': [{'role': 'AXButton', 'label': 'Increment', 'actions': ['AXPress'], 'element_token': 'token-1'},
                                  {'role': 'AXButton', 'label': 'Grant permission', 'actions': ['AXPress'], 'element_token': 'protected'},
                                  {'role': 'AXStaticText', 'label': 'count:' + str(self.count)}]}
        elif name == 'click': self.count += 1; value = {'status': 'delivered'}
        else: raise AssertionError(name)
        return SimpleNamespace(is_error=False, structured_content=value)


class NativeScopeTests(unittest.TestCase):
    def setUp(self):
        fixture = test_user_context.UserContextTests()
        with patch('tempfile.tempdir', '/tmp'): fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.root = fixture.root
        self.prepared = nd.prepare(str(self.root), 'sample-project', 'understand-task')
        self.driver = FakeDriver()
        self.controller = nd.Controller(str(self.root), 'sample-project', 'understand-task', self.prepared['policy'], self.driver)

    def test_exact_observe_act_reobserve_and_stale_refusal(self):
        async def run():
            snapshot = await self.controller.snapshot()
            self.assertEqual([b['label'] for b in snapshot['buttons']], ['Increment'])
            handle = snapshot['buttons'][0]['handle']
            after = await self.controller.click(handle)
            self.assertEqual(after['elements'][-1]['label'], 'count:1')
            self.assertFalse(after['action']['postcondition_verified'])
            with self.assertRaisesRegex(ValueError, 'stale'): await self.controller.click(handle)
        asyncio.run(run())
        clicks = [args for name, args in self.driver.calls if name == 'click']
        self.assertEqual(clicks, [{'pid': 42, 'window_id': 7, 'element_token': 'token-1', 'delivery_mode': 'background'}])
        self.assertTrue(all(args.get('prompt') is False for name,args in self.driver.calls if name == 'check_permissions'))

    def test_foreign_target_and_changed_manifest_are_refused_before_click(self):
        async def run():
            snapshot = await self.controller.snapshot()
            self.driver.foreign = True
            with self.assertRaisesRegex(ValueError, 'allowed app'): await self.controller.click(snapshot['buttons'][0]['handle'])
        asyncio.run(run())
        self.assertFalse(any(name == 'click' for name, args in self.driver.calls))
        manifest = self.root / json.loads((self.root / self.prepared['policy']).read_text())['manifest']
        manifest.write_text('version: 3\nallow: all\n')
        with self.assertRaisesRegex(ValueError, 'changed'): self.controller.guard()

    def test_failed_refresh_invalidates_old_handles_and_missing_permission_never_prompts(self):
        async def run():
            snapshot = await self.controller.snapshot()
            self.driver.foreign = True
            with self.assertRaises(ValueError): await self.controller.snapshot()
            self.driver.foreign = False
            with self.assertRaisesRegex(ValueError, 'stale'): await self.controller.click(snapshot['buttons'][0]['handle'])
        asyncio.run(run())

    def test_scope_permissions_and_preparation_are_immutable(self):
        with self.assertRaisesRegex(ValueError, 'cannot be overwritten'):
            nd.prepare(str(self.root), 'sample-project', 'understand-task')
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            nd.Controller(str(self.root), 'foreign-project', 'understand-task', self.prepared['policy'], self.driver)
        policy = self.root / self.prepared['policy']; policy.chmod(0o644)
        with self.assertRaisesRegex(ValueError, 'owner-only'):
            nd.Controller(str(self.root), 'sample-project', 'understand-task', self.prepared['policy'], self.driver)


if __name__ == '__main__': unittest.main()
