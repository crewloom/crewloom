"""Paired statistics for the comparative evaluation.

Pure functions over scored trial records. The resampling unit is the task, because the
Arabic and English prompts of one task and its repeats are correlated; resampling
individual trials would report an interval that is too narrow.
"""
import random
import statistics

MIN_TASKS_FOR_VERDICT = 8
BOOTSTRAP_ROUNDS = 10000


def trial_score(trial):
    """Fraction of held-out cases passed by one scored trial."""
    return trial['passed'] / trial['total']


def task_means(trials, arm, language=None):
    """Mean per-task score for one arm, optionally restricted to one language."""
    by_task = {}
    for t in trials:
        if t['arm'] == arm and t['status'] == 'scored' and language in (None, t['language']):
            by_task.setdefault(t['task'], []).append(trial_score(t))
    return {task: statistics.fmean(scores) for task, scores in by_task.items()}


def bootstrap_ci(values, seed, rounds=BOOTSTRAP_ROUNDS):
    """95% percentile interval of the mean of `values`, resampling with replacement."""
    if not values:
        raise ValueError('Cannot bootstrap an empty sample')
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(values, k=len(values))) for _ in range(rounds))
    return means[int(0.025 * rounds)], means[int(0.975 * rounds) - 1]


def paired_difference(a, b, seed):
    """Per-task mean difference a - b over tasks present in both mappings."""
    shared = sorted(set(a) & set(b))
    diffs = [a[t] - b[t] for t in shared]
    if not diffs:
        return {'tasks': 0, 'mean_diff': None, 'ci95': None, 'verdict': 'no shared scored tasks'}
    low, high = bootstrap_ci(diffs, seed)
    return {'tasks': len(diffs), 'mean_diff': round(statistics.fmean(diffs), 4),
            'ci95': [round(low, 4), round(high, 4)], 'verdict': verdict(len(diffs), low, high)}


def verdict(tasks, low, high):
    """Plain-language reading of an interval; never a win without enough tasks."""
    if tasks < MIN_TASKS_FOR_VERDICT:
        return 'underpowered: %d tasks, need at least %d' % (tasks, MIN_TASKS_FOR_VERDICT)
    if low > 0:
        return 'first arm higher'
    if high < 0:
        return 'second arm higher'
    return 'no demonstrated difference'


def language_gap(trials, arm, seed):
    """English minus Arabic per-task score for one arm; positive means Arabic is worse."""
    return paired_difference(task_means(trials, arm, 'en'), task_means(trials, arm, 'ar'), seed)


def arm_summary(trials, arm):
    """Counts and pass rates for one arm, with failed trials kept visible."""
    own = [t for t in trials if t['arm'] == arm]
    scored = [t for t in own if t['status'] == 'scored']
    return {'planned': len(own), 'scored': len(scored), 'not_scored': len(own) - len(scored),
            'mean_case_pass': round(statistics.fmean(map(trial_score, scored)), 4) if scored else None,
            'full_pass_rate': round(sum(t['passed'] == t['total'] for t in scored) / len(scored), 4) if scored else None,
            'mean_generation_ms': _mean(scored, 'duration_generation_ms'),
            'mean_total_tokens': _mean(scored, 'total_tokens'),
            'total_cost_usd': round(sum(t['cost_usd'] for t in scored if t.get('cost_usd') is not None), 6)
            if any(t.get('cost_usd') is not None for t in scored) else None}


def _mean(trials, key):
    values = [t[key] for t in trials if t.get(key) is not None]
    return round(statistics.fmean(values), 1) if values else None


def compare(trials, arms, seed):
    """Every ordered pair of arms plus each arm's language gap."""
    labels = list(arms)
    return {'summary': {a: arm_summary(trials, a) for a in labels},
            'language_gap_en_minus_ar': {a: language_gap(trials, a, seed) for a in labels},
            'paired': [{'first': a, 'second': b,
                        **paired_difference(task_means(trials, a), task_means(trials, b), seed)}
                       for i, a in enumerate(labels) for b in labels[i + 1:]]}
