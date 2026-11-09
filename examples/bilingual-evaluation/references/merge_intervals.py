"""Grader-only reference; never supplied in a model prompt."""
def merge_intervals(intervals):
    if not isinstance(intervals, list):
        raise ValueError('Invalid intervals')
    pairs = []
    for item in intervals:
        if not isinstance(item, list) or len(item) != 2 or any(type(n) is not int for n in item) or item[0] > item[1]:
            raise ValueError('Invalid interval')
        pairs.append((item[0], item[1]))
    merged = []
    for start, end in sorted(pairs):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
