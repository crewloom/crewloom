"""Grader-only reference; never supplied in a model prompt."""
def _number(text):
    if not text or not all(c in '0123456789' for c in text) or (len(text) > 1 and text[0] == '0'):
        raise ValueError('Invalid number')
    return int(text)


def _key(version):
    if not isinstance(version, str):
        raise ValueError('Invalid version')
    core, dash, pre = version.partition('-')
    parts = core.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid core')
    numbers = tuple(_number(p) for p in parts)
    if not dash:
        return numbers, (1,)
    identifiers = pre.split('.')
    ranked = []
    for item in identifiers:
        if not item or not all(c.isascii() and (c.isalnum() or c == '-') for c in item):
            raise ValueError('Invalid prerelease')
        ranked.append((0, _number(item), '') if item.isdigit() else (1, 0, item))
    return numbers, (0, tuple(ranked))


def semver_sort(versions):
    if not isinstance(versions, list):
        raise ValueError('Invalid versions')
    keyed = [(_key(v), v) for v in versions]
    return [v for _key_, v in sorted(keyed, key=lambda pair: pair[0])]
