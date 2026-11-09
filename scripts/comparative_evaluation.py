"""Comparative arm evaluation on the frozen bilingual feature tasks.

An arm is one host and model with either a plain prompt or the Crewloom role prompt.
Running the same model plain and with the role isolates what Crewloom adds; running
different models shows the cross-model spread. Grading reuses the held-out Docker case
grader, so expectations never enter a prompt. This measures code correctness on the
frozen tasks only: no claim about the host's agent loop, tools, or real client work.
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

import comparative_stats as stats
import crewloom_resources as resources
import evaluate_hosts as grading
import model_host
import workflow as w

TASKS = 'examples/bilingual-evaluation/tasks.json'
EXTRA_TASKS = 'examples/bilingual-evaluation/comparative-tasks.json'
ROLE = 'fullstack-mvp-engineer'
PROTOCOL = 'crewloom-comparative-arms-v1'
MODES = ('plain', 'role')
ARM_KEYS = {'label', 'host', 'model', 'mode'}
INSTRUCTION = 'No tools or external files. Return the declared artifact only.\n'
LIMITS = ('Correctness of one function per task against held-out cases, graded in Docker. '
          'Not an agent-loop, tool-use, latency-under-load or real-project comparison. '
          'CLI generation is a native host exception, not an OS sandbox.')


def parse_arm(text):
    """`label=a,host=claude,model=m,mode=role` -> validated arm dict."""
    try:
        arm = dict(part.split('=', 1) for part in text.split(','))
    except ValueError:
        raise ValueError('Arm must be comma-separated key=value pairs: ' + text) from None
    if set(arm) != ARM_KEYS:
        raise ValueError('Arm needs exactly label, host, model, mode: ' + text)
    if arm['mode'] not in MODES:
        raise ValueError('Arm mode must be plain or role: ' + text)
    if not arm['label'].strip() or not arm['model'].strip():
        raise ValueError('Arm label and model must not be empty: ' + text)
    return arm


def validate_arms(arms):
    labels = [a['label'] for a in arms]
    if len(arms) < 2 or len(set(labels)) != len(labels):
        raise ValueError('Provide at least two arms with distinct labels')
    for arm in arms:
        if arm['host'] not in model_host.CLI_HOSTS:
            raise ValueError('Unsupported host: ' + arm['host'])


def load_tasks(root):
    """The frozen pilot tasks plus the comparative extension, ids unique."""
    tasks = [t for name in (TASKS, EXTRA_TASKS) for t in json.loads((root / name).read_text())['tasks']]
    if len({t['id'] for t in tasks}) != len(tasks):
        raise ValueError('Duplicate task id across task files')
    return tasks


def frozen_inputs(root=None):
    root = root or resources.distribution_root()
    paths = [root / TASKS, root / EXTRA_TASKS, root / '.agents/skills' / ROLE / 'SKILL.md', Path(__file__),
             Path(stats.__file__), Path(model_host.__file__), Path(grading.__file__), Path(w.__file__)]
    return {str(p.relative_to(root)) if root in p.parents else p.name:
            hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def build_prompt(arm, task, language, role_text):
    body = INSTRUCTION + 'Task:\n' + task['prompts'][language]
    if arm['mode'] == 'role':
        return 'Follow this developer role. ' + INSTRUCTION + role_text + '\nTask:\n' + task['prompts'][language]
    return body


def plan_trials(arms, tasks, repeats, seed):
    trials = [{'arm': a['label'], 'task': t['id'], 'language': lang, 'repeat': r}
              for a in arms for t in tasks for lang in ('en', 'ar') for r in range(1, repeats + 1)]
    random.Random(seed).shuffle(trials)
    return trials


def run(output, arms, repeats=3, timeout=120, image=w.DEFAULT_IMAGE, seed=20261110):
    validate_arms(arms)
    if type(repeats) is not int or not 1 <= repeats <= 10:
        raise ValueError('Repeats must be from 1 to 10')
    if type(timeout) is not int or not 1 <= timeout <= 600:
        raise ValueError('Timeout must be from 1 to 600 seconds')
    folder = Path(output).absolute()
    if folder.exists() or folder.is_symlink():
        raise ValueError('Select a new output directory; attempts cannot be overwritten')
    root = resources.distribution_root()
    tasks = load_tasks(root)
    image_id = w.inspect_image(image)
    frozen = frozen_inputs(root)
    folder.mkdir(parents=True, mode=0o700)
    by_label = {a['label']: a for a in arms}
    role_text = (root / '.agents/skills' / ROLE / 'SKILL.md').read_text()
    planned = plan_trials(arms, tasks, repeats, seed)
    report = {'protocol': PROTOCOL, 'seed': seed, 'repeats': repeats, 'image_id': image_id,
              'arms': arms, 'frozen_inputs': frozen, 'planned_trials': planned, 'trials': [],
              'limits': LIMITS}
    save = lambda: (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    save()
    failures, stopped = {}, set()
    for index, trial in enumerate(planned):
        if frozen_inputs(root) != frozen:
            raise ValueError('Frozen evaluation inputs changed; report is invalid')
        arm = by_label[trial['arm']]
        task = next(t for t in tasks if t['id'] == trial['task'])
        result = {**trial, 'status': 'pending'}
        if trial['arm'] in stopped:
            result.update(status='blocked', error='Arm stopped after two identical transport failures')
        else:
            try:
                result.update(_attempt(arm, task, trial['language'], role_text, folder, index, image_id, root, timeout))
            except (ValueError, OSError) as exc:
                result.update(status='failed', error=str(exc))
                key = (trial['arm'], str(exc))
                failures[key] = failures.get(key, 0) + 1
                if failures[key] >= 2:
                    stopped.add(trial['arm'])
        report['trials'].append(result)
        save()
        print(json.dumps({k: result[k] for k in ('arm', 'task', 'language', 'repeat', 'status')}), flush=True)
    return finish(report, frozen_inputs(root) == frozen, save)


def _attempt(arm, task, language, role_text, folder, index, image_id, root, timeout):
    prompt = build_prompt(arm, task, language, role_text)
    artifacts, evidence = model_host.generate(arm['host'], prompt, [task['output']], timeout, arm['model'])
    source = artifacts[task['output']].encode()
    (folder / ('candidate-%03d.py' % index)).write_bytes(source)
    cases = [grading._grade_case(source, task, case, 0, image_id, 15, root, (), Path(task['output']).name)
             for case in task['cases']]
    usage = evidence.get('usage_metrics') or {}
    return {'status': 'scored', 'source_sha256': w.digest(source), 'cases': cases,
            'passed': sum(c['passed'] for c in cases), 'total': len(cases),
            'duration_generation_ms': evidence.get('duration_ms'), 'cost_usd': evidence.get('cost_usd'),
            'total_tokens': usage.get('total_tokens')}


def finish(report, inputs_unchanged, save):
    report['inputs_unchanged'] = inputs_unchanged
    report['scored_trials'] = sum(t['status'] == 'scored' for t in report['trials'])
    report['complete'] = inputs_unchanged and report['scored_trials'] == len(report['planned_trials'])
    report['comparison'] = stats.compare(report['trials'], [a['label'] for a in report['arms']], report['seed'])
    save()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', required=True)
    parser.add_argument('--arm', action='append', required=True, type=parse_arm,
                        help='label=NAME,host=claude|codex|opencode,model=ID,mode=plain|role (repeat per arm)')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--timeout', type=int, default=120)
    args = parser.parse_args(argv)
    report = run(args.output, args.arm, args.repeats, args.timeout)
    print(json.dumps(report['comparison'], ensure_ascii=False, indent=2))
    return 0 if report['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
