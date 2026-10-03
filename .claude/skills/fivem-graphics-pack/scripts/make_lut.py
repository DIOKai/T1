#!/usr/bin/env python3
"""Generate a colour-grading LUT strip for ReShade's LUT.fx.

Layout (from LUT.fx in crosire/reshade-shaders): a strip of `tiles` tiles,
each `tiles` x `tiles` pixels (default 32 -> 1024x32). Inside a tile x = red,
y = green; the tile index = blue. A neutral LUT stores each cell's own colour.

Usage:
    python make_lut.py --preset warm -o lut.png
    python make_lut.py --temperature 0.3 --saturation 1.1 --contrast 1.05 -o mylook.png
    python make_lut.py --preset cinematic --strength 0.7 -o lut.png
    python make_lut.py --neutral -o lut_neutral.png   # to grade by hand in GIMP/Krita

Standard library only (PNG written with zlib). Values are starting points to
tune in game, not measured standards.
"""
import argparse
import struct
import zlib

PRESETS = {
    # temperature: -1 cool .. +1 warm; tint: -1 green .. +1 magenta
    'neutral':   dict(),
    'warm':      dict(temperature=0.35, saturation=1.10, contrast=1.03),
    'cool':      dict(temperature=-0.35, saturation=0.95, contrast=1.03),
    'cinematic': dict(contrast=1.10, saturation=0.92, split_shadows=(0.0, 0.06, 0.10), split_highlights=(0.10, 0.04, -0.04)),
    'realistic': dict(saturation=0.95, contrast=1.05),
    'vivid':     dict(saturation=1.25, contrast=1.08),
    'noir':      dict(saturation=0.0, contrast=1.20),
}


def clamp(x):
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def grade(r, g, b, temperature=0.0, tint=0.0, saturation=1.0, contrast=1.0, exposure=0.0,
          split_shadows=(0.0, 0.0, 0.0), split_highlights=(0.0, 0.0, 0.0)):
    # exposure (stops, small values)
    m = 2.0 ** exposure
    r, g, b = r * m, g * m, b * m
    # white balance: warm adds red, removes blue; tint moves green/magenta
    r *= 1.0 + 0.12 * temperature
    b *= 1.0 - 0.12 * temperature
    g *= 1.0 - 0.08 * tint
    # saturation around Rec.709 luma
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    r, g, b = y + (r - y) * saturation, y + (g - y) * saturation, y + (b - y) * saturation
    # contrast around mid grey
    r, g, b = (r - 0.5) * contrast + 0.5, (g - 0.5) * contrast + 0.5, (b - 0.5) * contrast + 0.5
    # split toning: shadows weighted by (1-y), highlights by y
    y = clamp(0.2126 * r + 0.7152 * g + 0.0722 * b)
    ws, wh = (1.0 - y) ** 2, y ** 2
    r += split_shadows[0] * ws + split_highlights[0] * wh
    g += split_shadows[1] * ws + split_highlights[1] * wh
    b += split_shadows[2] * ws + split_highlights[2] * wh
    return clamp(r), clamp(g), clamp(b)


def write_png(path, width, height, rows):
    raw = b''.join(b'\x00' + bytes(row) for row in rows)

    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

    with open(path, 'wb') as fh:
        fh.write(b'\x89PNG\r\n\x1a\n')
        fh.write(chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)))
        fh.write(chunk(b'IDAT', zlib.compress(raw, 9)))
        fh.write(chunk(b'IEND', b''))


def build(tiles, params, strength):
    n = tiles
    rows = []
    for gy in range(n):
        row = []
        for bt in range(n):
            for rx in range(n):
                r0, g0, b0 = rx / (n - 1), gy / (n - 1), bt / (n - 1)
                r1, g1, b1 = grade(r0, g0, b0, **params)
                r = r0 + (r1 - r0) * strength
                g = g0 + (g1 - g0) * strength
                b = b0 + (b1 - b0) * strength
                row += [round(r * 255), round(g * 255), round(b * 255)]
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser(description='Generate a ReShade LUT.fx strip')
    ap.add_argument('-o', '--output', default='lut.png')
    ap.add_argument('--preset', choices=sorted(PRESETS), default=None)
    ap.add_argument('--neutral', action='store_true', help='identity LUT for grading by hand')
    ap.add_argument('--tiles', type=int, default=32, help='tile size = tile count (LUT.fx default 32; prod80 templates use 64)')
    ap.add_argument('--strength', type=float, default=1.0, help='0..1 blend from neutral to the look')
    ap.add_argument('--temperature', type=float)
    ap.add_argument('--tint', type=float)
    ap.add_argument('--saturation', type=float)
    ap.add_argument('--contrast', type=float)
    ap.add_argument('--exposure', type=float)
    args = ap.parse_args()

    params = {} if args.neutral else dict(PRESETS.get(args.preset or 'neutral', {}))
    for key in ('temperature', 'tint', 'saturation', 'contrast', 'exposure'):
        v = getattr(args, key)
        if v is not None and not args.neutral:
            params[key] = v
    rows = build(args.tiles, params, 0.0 if args.neutral else args.strength)
    write_png(args.output, args.tiles * args.tiles, args.tiles, rows)
    print(f'wrote {args.output} ({args.tiles * args.tiles}x{args.tiles}); settings: {params or "neutral"}')
    if args.tiles != 32:
        print(f'LUT.fx needs: fLUT_TileSizeXY={args.tiles} and fLUT_TileAmount={args.tiles} in PreprocessorDefinitions')


if __name__ == '__main__':
    main()
