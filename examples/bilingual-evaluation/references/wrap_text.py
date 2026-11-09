"""Grader-only reference; never supplied in a model prompt."""
def wrap_text(spec):
    if not isinstance(spec, dict) or set(spec) != {'text', 'width'}:
        raise ValueError('Invalid spec')
    text, width = spec['text'], spec['width']
    if not isinstance(text, str) or type(width) is not int or width < 1:
        raise ValueError('Invalid values')
    words = []
    for word in text.split():
        words.extend(word[i:i + width] for i in range(0, len(word), width))
    lines = []
    for word in words:
        if lines and len(lines[-1]) + 1 + len(word) <= width:
            lines[-1] += ' ' + word
        else:
            lines.append(word)
    return lines
