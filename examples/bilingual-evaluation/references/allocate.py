"""Grader-only reference; never supplied in a model prompt."""
def allocate(spec):
    if not isinstance(spec, dict) or set(spec) != {'total_cents', 'weights'}:
        raise ValueError('Invalid spec')
    total, weights = spec['total_cents'], spec['weights']
    if type(total) is not int or total < 0 or not isinstance(weights, list) or not weights:
        raise ValueError('Invalid values')
    if any(type(w) is not int or w < 0 for w in weights) or sum(weights) == 0:
        raise ValueError('Invalid weights')
    whole = sum(weights)
    shares = [total * w // whole for w in weights]
    remainders = [total * w % whole for w in weights]
    order = sorted(range(len(weights)), key=lambda i: (-remainders[i], i))
    for i in order[:total - sum(shares)]:
        shares[i] += 1
    return shares
