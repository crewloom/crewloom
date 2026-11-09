import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import comparative_evaluation as ev
import comparative_stats as stats
import evaluate_hosts as grading
import workflow as w

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / 'examples/bilingual-evaluation/references'


def scored(arm, task, language, passed, total=10, repeat=1):
    return {'arm': arm, 'task': task, 'language': language, 'repeat': repeat,
            'status': 'scored', 'passed': passed, 'total': total}


class Stats(unittest.TestCase):
    def test_paired_difference_is_underpowered_with_few_tasks(self):
        trials = [scored(a, t, l, p) for t in ('x', 'y') for l in ('en', 'ar')
                  for a, p in (('A', 10), ('B', 5))]
        result = stats.compare(trials, ['A', 'B'], 1)['paired'][0]
        self.assertEqual(result['tasks'], 2)
        self.assertEqual(result['mean_diff'], 0.5)
        self.assertTrue(result['verdict'].startswith('underpowered'))

    def test_clear_gap_with_enough_tasks_names_the_higher_arm(self):
        tasks = ['t%d' % i for i in range(10)]
        trials = [scored(a, t, l, p) for t in tasks for l in ('en', 'ar')
                  for a, p in (('A', 10), ('B', 6))]
        result = stats.compare(trials, ['A', 'B'], 1)['paired'][0]
        self.assertEqual(result['verdict'], 'first arm higher')
        self.assertGreater(result['ci95'][0], 0)

    def test_identical_arms_show_no_difference(self):
        tasks = ['t%d' % i for i in range(10)]
        trials = [scored(a, t, 'en', 7) for t in tasks for a in ('A', 'B')]
        result = stats.compare(trials, ['A', 'B'], 1)['paired'][0]
        self.assertEqual(result['verdict'], 'no demonstrated difference')

    def test_failed_trials_are_counted_not_hidden(self):
        trials = [scored('A', 't', 'en', 10), {'arm': 'A', 'task': 't', 'language': 'ar',
                                               'repeat': 1, 'status': 'failed'}]
        summary = stats.arm_summary(trials, 'A')
        self.assertEqual((summary['planned'], summary['scored'], summary['not_scored']), (2, 1, 1))

    def test_language_gap_is_positive_when_arabic_is_worse(self):
        trials = [scored('A', 't', 'en', 10), scored('A', 't', 'ar', 4)]
        gap = stats.language_gap(trials, 'A', 1)
        self.assertEqual(gap['mean_diff'], 0.6)

    def test_empty_sample_is_rejected(self):
        with self.assertRaises(ValueError):
            stats.bootstrap_ci([], 1)


class Arms(unittest.TestCase):
    def test_parse_arm_accepts_valid_and_rejects_bad_input(self):
        arm = ev.parse_arm('label=a,host=claude,model=m,mode=role')
        self.assertEqual(arm['mode'], 'role')
        for bad in ('label=a,host=claude,model=m', 'label=a,host=claude,model=m,mode=x',
                    'label=,host=claude,model=m,mode=plain', 'junk'):
            with self.assertRaises(ValueError, msg=bad):
                ev.parse_arm(bad)

    def test_validate_arms_needs_two_distinct_supported_arms(self):
        one = ev.parse_arm('label=a,host=claude,model=m,mode=plain')
        with self.assertRaises(ValueError):
            ev.validate_arms([one])
        with self.assertRaises(ValueError):
            ev.validate_arms([one, dict(one)])
        with self.assertRaises(ValueError):
            ev.validate_arms([one, ev.parse_arm('label=b,host=nope,model=m,mode=plain')])

    def test_prompts_differ_only_by_role_and_never_contain_cases(self):
        task = {'prompts': {'en': 'do it', 'ar': 'نفّذ'}}
        plain = ev.build_prompt({'mode': 'plain'}, task, 'en', 'ROLE-TEXT')
        role = ev.build_prompt({'mode': 'role'}, task, 'en', 'ROLE-TEXT')
        self.assertNotIn('ROLE-TEXT', plain)
        self.assertIn('ROLE-TEXT', role)
        self.assertTrue(plain.endswith('Task:\ndo it'))
        self.assertTrue(role.endswith('Task:\ndo it'))

    def test_trial_plan_is_balanced_and_reproducible(self):
        arms = [{'label': 'a'}, {'label': 'b'}]
        tasks = [{'id': 'x'}, {'id': 'y'}]
        first = ev.plan_trials(arms, tasks, 3, 7)
        self.assertEqual(first, ev.plan_trials(arms, tasks, 3, 7))
        self.assertEqual(len(first), 2 * 2 * 2 * 3)
        self.assertEqual(sum(t['arm'] == 'a' for t in first), len(first) // 2)


class Run(unittest.TestCase):
    def test_run_records_failures_stops_failing_arm_and_keeps_inputs_frozen(self):
        def fake_generate(host, prompt, outputs, timeout, model):
            if model == 'broken':
                raise ValueError('transport down')
            return {outputs[0]: 'def f(v):\n return v\n'}, {'duration_ms': 5, 'usage_metrics': {'total_tokens': 9}}
        grade = lambda *a, **k: {'case': 'c', 'passed': 1}
        arms = [ev.parse_arm('label=ok,host=claude,model=good,mode=plain'),
                ev.parse_arm('label=bad,host=codex,model=broken,mode=role')]
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(ev.w, 'inspect_image', return_value='sha256:img'), \
                patch.object(ev.model_host, 'generate', side_effect=fake_generate), \
                patch.object(ev.grading, '_grade_case', side_effect=grade):
            out = Path(folder) / 'run'
            report = ev.run(out, arms, repeats=1)
            self.assertTrue((out / 'report.json').exists())
            with self.assertRaises(ValueError):
                ev.run(out, arms, repeats=1)
        statuses = {t['arm']: set() for t in report['trials']}
        for t in report['trials']:
            statuses[t['arm']].add(t['status'])
        self.assertEqual(statuses['ok'], {'scored'})
        self.assertEqual(statuses['bad'], {'failed', 'blocked'})
        self.assertEqual(sum(t['status'] == 'failed' for t in report['trials']), 2)
        self.assertTrue(report['inputs_unchanged'])
        self.assertFalse(report['complete'])
        self.assertEqual(report['comparison']['summary']['bad']['scored'], 0)
        json.dumps(report, ensure_ascii=False)


class Tasks(unittest.TestCase):
    tasks = ev.load_tasks(ROOT)

    def test_enough_tasks_for_a_verdict_and_ids_are_unique(self):
        self.assertGreaterEqual(len(self.tasks), stats.MIN_TASKS_FOR_VERDICT)
        self.assertEqual(len({t['id'] for t in self.tasks}), len(self.tasks))

    def test_every_task_has_matching_bilingual_prompts_and_balanced_cases(self):
        for task in self.tasks:
            self.assertEqual(set(task['prompts']), {'en', 'ar'}, task['id'])
            for language in ('en', 'ar'):
                prompt = task['prompts'][language]
                self.assertIn(task['output'], prompt, task['id'])
                self.assertIn(task['id'] + '(', prompt, task['id'])
                self.assertIn('ValueError', prompt, task['id'])
            errors = [c for c in task['cases'] if c['expected'] == {'error': 'ValueError'}]
            self.assertGreaterEqual(len(errors), 8, task['id'])
            self.assertGreaterEqual(len(task['cases']) - len(errors), 6, task['id'])

    def test_reference_matches_every_case_without_mutating_input(self):
        for task in self.tasks:
            spec = importlib.util.spec_from_file_location(task['id'], REFS / Path(task['output']).name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for case in task['cases']:
                value = json.loads(json.dumps(case['input']))
                try:
                    envelope = {'outcome': 'value', 'value': getattr(module, task['id'])(value)}
                except Exception as exc:
                    envelope = {'outcome': 'raised', 'exception': type(exc).__name__}
                self.assertTrue(grading.study_score(envelope, grading.expected_outcome(case['expected'])),
                                (task['id'], case['id']))
                self.assertEqual(value, case['input'])

    @unittest.skipUnless(os.environ.get('CREWLOOM_DOCKER_TESTS') == '1', 'requires actual Docker')
    def test_real_grader_accepts_reference_and_rejects_wrong_implementations(self):
        image = w.inspect_image(w.DEFAULT_IMAGE)
        for task in self.tasks:
            name = Path(task['output']).name
            source = (REFS / name).read_bytes()
            for case in task['cases']:
                result = grading._grade_case(source, task, case, 0, image, 15, ROOT, (), name)
                self.assertEqual(result['passed'], 1, (task['id'], case['id'], result))
            case = next(c for c in task['cases'] if c['expected'] != {'error': 'ValueError'})
            for bad in ['def %s(v):\n return None\n' % task['id'],
                        'def %s(v):\n raise ValueError()\n' % task['id']]:
                result = grading._grade_case(bad.encode(), task, case, 0, image, 15, ROOT, (), name)
                self.assertEqual(result['passed'], 0, (task['id'], result))


if __name__ == '__main__':
    unittest.main()
