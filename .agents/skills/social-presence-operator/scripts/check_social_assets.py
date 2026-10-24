#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check a logo or cover image against a social platform's size rules and detect blank renders.

Read-only; standard library only. PNG files are decoded to detect an image that is almost one
colour (a failed SVG render); JPEG files are checked for size only.
Exit codes: 0 = no findings, 1 = findings, 2 = unreadable input.
"""
import argparse
import json
import struct
import sys
import zlib
from collections import Counter

# (minimum width, minimum height, aspect-ratio range or None for "square").
SPECS = {
    ('linkedin', 'logo'): (300, 300, None),
    ('linkedin', 'cover'): (1128, 191, (3.5, 4.2)),
    ('facebook', 'logo'): (170, 170, None),
    ('facebook', 'cover'): (820, 312, (2.4, 2.8)),
    ('x', 'logo'): (400, 400, None),
    ('x', 'cover'): (1500, 500, (2.8, 3.2)),
}
MAX_PIXELS = 16_000_000
UNIFORM_FRACTION = 0.99
UNIFORM_DISTANCE = 40
PNG_MAGIC = b'\x89PNG\r\n\x1a\n'


def read_png(data):
    """Return (width, height, rows-of-RGBA-tuples sampler) or raise ValueError."""
    if not data.startswith(PNG_MAGIC):
        raise ValueError('not a PNG')
    position, header, palette, idat = 8, None, None, bytearray()
    while position + 8 <= len(data):
        length, kind = struct.unpack('>I4s', data[position:position + 8])
        body = data[position + 8:position + 8 + length]
        position += 12 + length
        if kind == b'IHDR':
            header = struct.unpack('>IIBBBBB', body)
        elif kind == b'PLTE':
            palette = body
        elif kind == b'IDAT':
            idat += body
        elif kind == b'IEND':
            break
    if header is None:
        raise ValueError('missing IHDR')
    return header, palette, bytes(idat)


def decode_samples(header, palette, idat):
    width, height, depth, color, _, _, interlace = header
    if interlace != 0:
        raise ValueError('interlaced PNG not decoded')
    if width * height > MAX_PIXELS:
        raise ValueError('image too large to decode')
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
    if channels is None or depth not in (8, 16) or (color == 3 and depth != 8):
        raise ValueError('unsupported PNG format')
    bytes_per_pixel = channels * depth // 8
    stride = width * bytes_per_pixel
    raw = zlib.decompress(idat)
    if len(raw) < height * (stride + 1):
        raise ValueError('truncated PNG data')
    rows, previous = [], bytearray(stride)
    for y in range(height):
        offset = y * (stride + 1)
        kind, line = raw[offset], bytearray(raw[offset + 1:offset + 1 + stride])
        if kind == 1:
            for i in range(bytes_per_pixel, stride):
                line[i] = (line[i] + line[i - bytes_per_pixel]) & 255
        elif kind == 2:
            for i in range(stride):
                line[i] = (line[i] + previous[i]) & 255
        elif kind == 3:
            for i in range(stride):
                left = line[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
                line[i] = (line[i] + ((left + previous[i]) >> 1)) & 255
        elif kind == 4:
            for i in range(stride):
                left = line[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
                up = previous[i]
                corner = previous[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
                estimate = left + up - corner
                dl, du, dc = abs(estimate - left), abs(estimate - up), abs(estimate - corner)
                predictor = left if dl <= du and dl <= dc else (up if du <= dc else corner)
                line[i] = (line[i] + predictor) & 255
        elif kind != 0:
            raise ValueError('bad PNG filter')
        rows.append(line)
        previous = line
    return width, height, depth, color, channels, rows


def pixel(rows, x, y, depth, color, channels, palette):
    """Return (r, g, b, a) on a 0-255 scale."""
    step = depth // 8
    base = x * channels * step
    row = rows[y]
    values = [row[base + c * step] for c in range(channels)]
    if color == 0:
        return values[0], values[0], values[0], 255
    if color == 4:
        return values[0], values[0], values[0], values[1]
    if color == 2:
        return values[0], values[1], values[2], 255
    if color == 3:
        index = values[0] * 3
        return palette[index], palette[index + 1], palette[index + 2], 255
    return values[0], values[1], values[2], values[3]


def uniformity(width, height, depth, color, channels, rows, palette):
    """Fraction of visible sampled pixels close to the most common colour."""
    sample_x = max(1, width // 64)
    sample_y = max(1, height // 64)
    seen = []
    for y in range(0, height, sample_y):
        for x in range(0, width, sample_x):
            r, g, b, a = pixel(rows, x, y, depth, color, channels, palette)
            if a >= 32:
                seen.append((r, g, b))
    if not seen:
        return 1.0, 0
    common = Counter((r // 16, g // 16, b // 16) for r, g, b in seen).most_common(1)[0][0]
    anchor = tuple(c * 16 + 8 for c in common)
    near = sum(1 for p in seen if max(abs(p[i] - anchor[i]) for i in range(3)) <= UNIFORM_DISTANCE)
    return near / len(seen), len(seen)


def jpeg_size(data):
    if not data.startswith(b'\xff\xd8'):
        raise ValueError('not a JPEG')
    position = 2
    while position + 9 < len(data):
        if data[position] != 0xFF:
            position += 1
            continue
        marker = data[position + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack('>HH', data[position + 5:position + 9])
            return width, height
        position += 2 + struct.unpack('>H', data[position + 2:position + 4])[0]
    raise ValueError('JPEG size not found')


def evaluate(platform, kind, data):
    findings = []
    notes = []
    palette = None
    if data.startswith(PNG_MAGIC):
        header, palette, idat = read_png(data)
        width, height = header[0], header[1]
        fmt = 'png'
    else:
        width, height = jpeg_size(data)
        fmt = 'jpeg'

    min_w, min_h, ratio = SPECS[(platform, kind)]
    if width < min_w or height < min_h:
        findings.append(f'{width}x{height} is below the {platform} {kind} minimum {min_w}x{min_h}.')
    if ratio is None:
        if width != height:
            findings.append(f'{platform} logo must be square; got {width}x{height}.')
    else:
        actual = width / height
        if not ratio[0] <= actual <= ratio[1]:
            findings.append(f'aspect ratio {actual:.2f} is outside {ratio[0]}-{ratio[1]} for a {platform} cover.')

    if fmt == 'png':
        try:
            decoded = decode_samples(header, palette, idat)
            fraction, visible = uniformity(*decoded, palette)
            if fraction >= UNIFORM_FRACTION:
                findings.append(f'image is {fraction:.1%} one colour; it looks blank or failed to render. '
                                'Re-render the source and inspect it before upload.')
        except (ValueError, zlib.error) as exc:
            notes.append(f'pixel check skipped: {exc}')
    else:
        notes.append('pixel check skipped: JPEG is size-checked only')
    return {'width': width, 'height': height, 'format': fmt}, findings, notes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--platform', required=True, choices=sorted({p for p, _ in SPECS}))
    parser.add_argument('--kind', required=True, choices=('logo', 'cover'))
    parser.add_argument('--file', required=True)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        with open(args.file, 'rb') as handle:
            data = handle.read()
        info, findings, notes = evaluate(args.platform, args.kind, data)
    except (OSError, ValueError, struct.error, zlib.error) as exc:
        print(f'Cannot read image: {exc}', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({**info, 'findings': findings, 'notes': notes}, ensure_ascii=False))
    else:
        for note in notes:
            print(f'NOTE {note}')
        if findings:
            for finding in findings:
                print(f'FAIL {finding}')
        else:
            print(f"PASS {args.platform} {args.kind}: {info['width']}x{info['height']} {info['format']}")
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
