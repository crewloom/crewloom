"""Grader-only reference; never supplied in a model prompt."""
def parse_duration(text):
    if not isinstance(text, str) or not text:
        raise ValueError('Invalid duration')
    seconds = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
    order = list(seconds)
    last = -1
    total = 0
    i = 0
    while i < len(text):
        j = i
        while j < len(text) and text[j] in '0123456789':
            j += 1
        if j == i or j == len(text) or text[j] not in seconds:
            raise ValueError('Invalid segment')
        unit = order.index(text[j])
        if unit <= last:
            raise ValueError('Unit repeated or out of order')
        last = unit
        total += int(text[i:j]) * seconds[text[j]]
        i = j + 1
    return total
