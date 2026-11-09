"""Grader-only reference; never supplied in a model prompt."""
def csv_row(line):
    if not isinstance(line, str) or '\n' in line or '\r' in line:
        raise ValueError('Invalid line')
    fields = []
    i = 0
    while True:
        if line[i:i + 1] == '"':
            i += 1
            value = []
            while True:
                if i >= len(line):
                    raise ValueError('Unterminated quote')
                if line[i] == '"':
                    if line[i + 1:i + 2] == '"':
                        value.append('"')
                        i += 2
                        continue
                    i += 1
                    break
                value.append(line[i])
                i += 1
            if i < len(line) and line[i] != ',':
                raise ValueError('Text after closing quote')
            fields.append(''.join(value))
        else:
            j = line.find(',', i)
            j = len(line) if j < 0 else j
            if '"' in line[i:j]:
                raise ValueError('Stray quote')
            fields.append(line[i:j])
            i = j
        if i >= len(line):
            return fields
        i += 1
        if i == len(line):
            fields.append('')
            return fields
