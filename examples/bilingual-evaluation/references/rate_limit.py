"""Grader-only reference; never supplied in a model prompt."""
def rate_limit(events):
    if not isinstance(events, list):
        raise ValueError('Invalid events')
    accepted = {}
    result = []
    previous = 0
    for event in events:
        if not isinstance(event, dict) or set(event) != {'t', 'key'}:
            raise ValueError('Invalid event')
        t, key = event['t'], event['key']
        if type(t) is not int or t < 0 or not isinstance(key, str) or not key or t < previous:
            raise ValueError('Invalid event value')
        previous = t
        recent = [x for x in accepted.get(key, []) if x > t - 10]
        allowed = len(recent) < 3
        if allowed:
            recent.append(t)
        accepted[key] = recent
        result.append(allowed)
    return result
