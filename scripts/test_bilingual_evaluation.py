import importlib.util
import json
import os
import unittest
from pathlib import Path

import bilingual_evaluation as pilot
import evaluate_hosts as grading
import workflow as w

ROOT = Path(__file__).resolve().parents[1]
TASKS = json.loads((ROOT / pilot.TASKS).read_text())['tasks']


class Contracts(unittest.TestCase):
    def test_reference_matches_every_frozen_case_without_mutation(self):
        for task in TASKS:
            path = ROOT / 'examples/bilingual-evaluation/references' / Path(task['output']).name
            spec = importlib.util.spec_from_file_location(task['id'], path)
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            for case in task['cases']:
                value = json.loads(json.dumps(case['input']))
                try:
                    result = getattr(module, task['id'])(value)
                    envelope = {'outcome': 'value', 'value': result}
                except Exception as exc:
                    envelope = {'outcome': 'raised', 'exception': type(exc).__name__}
                self.assertTrue(grading.study_score(envelope, grading.expected_outcome(case['expected'])), case['id'])
                self.assertEqual(value, case['input'])

    def test_prompts_have_same_api_and_outputs_but_no_cases(self):
        for task in TASKS:
            for language in ('en', 'ar'):
                self.assertIn(task['output'], task['prompts'][language])
                self.assertIn('ValueError', task['prompts'][language])
                self.assertNotIn('invalid-0', task['prompts'][language])

    @unittest.skipUnless(os.environ.get('CREWLOOM_DOCKER_TESTS') == '1', 'requires actual Docker')
    def test_real_grader_accepts_reference_rejects_mutating_and_always_none(self):
        image = w.inspect_image(w.DEFAULT_IMAGE)
        for task in TASKS:
            source = (ROOT / 'examples/bilingual-evaluation/references' / Path(task['output']).name).read_bytes()
            for case in task['cases']:
                result = grading._grade_case(source, task, case, 0, image, 15, ROOT, (), Path(task['output']).name)
                self.assertEqual(result['passed'], 1, result)
            case = next(c for c in task['cases'] if c['id'] != 'empty' and isinstance(c['input'], (list, dict)))
            for bad in [f'def {task["id"]}(value):\n return None\n',
                        f'def {task["id"]}(value):\n value.clear()\n raise ValueError()\n']:
                result = grading._grade_case(bad.encode(), task, case, 0, image, 15, ROOT, (), Path(task['output']).name)
                self.assertEqual(result['passed'], 0, result)



class UnderstandingContracts(unittest.TestCase):
    def test_frozen_reference_and_every_single_field_mutation(self):
        for case in pilot.understanding_cases():
            expected = case['expected']
            self.assertTrue(pilot.understanding_score(expected, expected)['passed'])
            alternatives = {'project_id': 'foreign-project', 'user_id': 'foreign-user',
                            'task_id': 'foreign-task',
                            'language': 'ar' if expected['language'] != 'ar' else 'en',
                            'needs_clarification': not expected['needs_clarification'],
                            'questions': ['unexpected_field'],
                            'publication_requested': not expected['publication_requested'],
                            'verified_claims': ['tests_passed']}
            for field, replacement in alternatives.items():
                candidate = dict(expected, **{field: replacement})
                result = pilot.understanding_score(candidate, expected)
                self.assertFalse(result['passed'], (case['id'], field))
                self.assertFalse(result['fields'][field])

    def test_malformed_extra_and_boolean_coercions_never_receive_credit(self):
        expected = pilot.understanding_cases()[0]['expected']
        for candidate in [None, [], 'answer', dict(expected, rationale='trust me'),
                          dict(expected, publication_requested=0),
                          dict(expected, needs_clarification='false')]:
            result = pilot.understanding_score(candidate, expected)
            self.assertFalse(result['valid_response'])
            self.assertFalse(any(result['fields'].values()))

    def test_prompts_exclude_held_out_answers_and_preserve_scope(self):
        for case in pilot.understanding_cases():
            for language in ('en', 'ar'):
                for arm in ('raw-history', 'selected-context'):
                    prompt = pilot.understanding_prompt(case, language, arm)
                    payload = json.loads(prompt.split('Inputs:\n', 1)[1])
                    self.assertEqual(payload['scope'], case['scope'])
                    self.assertEqual(payload['current_user_request'], case['request'][language])
                    self.assertNotIn('expected', payload)
                    self.assertNotIn(json.dumps(case['expected'], ensure_ascii=False), prompt)
                    for record in payload['records']:
                        self.assertEqual(record['value'], record['source']['quote'])

    def test_selected_arm_uses_actual_task_and_user_correction_precedence(self):
        cases = {case['id']: case for case in pilot.understanding_cases()}
        chosen = {'latest-correction': 2, 'task-overrides-global': 2,
                  'other-task-is-excluded': 1, 'other-user-is-excluded': 1}
        for name, revision in chosen.items():
            for language in ('en', 'ar'):
                prompt = pilot.understanding_prompt(cases[name], language, 'selected-context')
                payload = json.loads(prompt.split('Inputs:\n', 1)[1])
                self.assertEqual([item['id'] for item in payload['records']], [revision])

    def test_fixture_change_is_refused_without_silent_refreeze(self):
        from unittest.mock import patch
        with patch.object(pilot.w, 'digest', return_value='modified'):
            with self.assertRaisesRegex(ValueError, 'explicit refreeze'):
                pilot.understanding_cases()

    def test_verification_is_offline_and_conflicting_provider_arguments_are_refused(self):
        from unittest.mock import patch
        with patch.object(pilot.model_host, 'generate', side_effect=AssertionError('provider reached')):
            self.assertEqual(pilot.main(['--verify-understanding']), 0)
            self.assertEqual(pilot.main(['--verify-understanding', '--host', 'codex']), 2)
            self.assertEqual(pilot.main([]), 2)
        report = pilot.verify_understanding()
        self.assertEqual(report['model_trials'], 0)
        self.assertFalse(report['model_improvement_measured'])
        self.assertEqual(report['fixture_sha256'], pilot.UNDERSTANDING_SHA256)


if __name__ == '__main__':
    unittest.main()
