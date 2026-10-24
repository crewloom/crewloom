import contextlib
import io
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import check_social_assets as tool


def chunk(kind, body):
    return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xFFFFFFFF)


def png(width, height, pixel_at, color=6, depth=8):
    channels = {2: 3, 6: 4}[color]
    step = depth // 8
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            values = pixel_at(x, y)
            for value in values[:channels]:
                raw += int(value * (257 if depth == 16 else 1)).to_bytes(step, 'big')
    header = struct.pack('>IIBBBBB', width, height, depth, color, 0, 0, 0)
    return (tool.PNG_MAGIC + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(bytes(raw)))
            + chunk(b'IEND', b''))


def blank(x, y):
    return (11, 15, 20, 255)


def ring(x, y):
    inside = (x - 150) ** 2 + (y - 150) ** 2 < 90 ** 2
    return (45, 212, 191, 255) if inside else (11, 15, 20, 255)


def run(data, *args):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'image.bin'
        path.write_bytes(data)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = tool.main(['--file', str(path), *args])
        return code, out.getvalue(), err.getvalue()


class SocialAssetTests(unittest.TestCase):
    def test_good_square_logo_passes(self):
        code, out, _ = run(png(300, 300, ring), '--platform', 'linkedin', '--kind', 'logo')
        self.assertEqual(code, 0, out)

    def test_blank_render_is_detected(self):
        code, out, _ = run(png(300, 300, blank), '--platform', 'linkedin', '--kind', 'logo')
        self.assertEqual(code, 1)
        self.assertIn('blank', out)

    def test_sixteen_bit_blank_is_detected(self):
        code, out, _ = run(png(300, 300, blank, depth=16), '--platform', 'facebook', '--kind', 'logo')
        self.assertEqual(code, 1)
        self.assertIn('blank', out)

    def test_wrong_cover_ratio_and_size_are_reported(self):
        code, out, _ = run(png(400, 400, ring), '--platform', 'linkedin', '--kind', 'cover')
        self.assertEqual(code, 1)
        self.assertIn('minimum', out)
        self.assertIn('aspect ratio', out)

    def test_non_square_logo_is_reported(self):
        code, out, _ = run(png(400, 300, ring), '--platform', 'x', '--kind', 'logo')
        self.assertEqual(code, 1)
        self.assertIn('square', out)

    def test_garbage_input_exits_two(self):
        code, _, err = run(b'not an image', '--platform', 'x', '--kind', 'logo')
        self.assertEqual(code, 2)
        self.assertIn('Cannot read image', err)

    def test_rgb_paeth_and_sub_filters_decode(self):
        header = struct.pack('>IIBBBBB', 2, 2, 8, 2, 0, 0, 0)
        raw = bytes([1, 10, 20, 30, 1, 1, 1, 4, 5, 5, 5, 1, 1, 1])
        data = (tool.PNG_MAGIC + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(raw))
                + chunk(b'IEND', b''))
        parsed, palette, idat = tool.read_png(data)
        width, height, depth, color, channels, rows = tool.decode_samples(parsed, palette, idat)
        self.assertEqual(tool.pixel(rows, 1, 0, depth, color, channels, palette)[:3], (11, 21, 31))


if __name__ == '__main__':
    unittest.main()
