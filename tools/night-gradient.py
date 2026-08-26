#!/usr/bin/env python3
"""
Generates the --night-gradient stops for css/site.css.

Why this exists rather than hand-picked hex values: a dark blue reads as rich
or as washed-out grey depending on its *chroma*, and sRGB gives you no handle
on chroma — it falls out of three channels as a side effect. Two hand-tuned
versions of this gradient failed before this script existed. The first spanned
only ~33 levels of blue and read as flat black on a real monitor. The second
had the right hue and lightness but sat at ~53% saturation, so it read as
washed-out grey fading into black.

So the ramp is defined in OKLCH, where lightness and chroma are separate axes,
and sampled down to sRGB stops. Sampling to many stops (rather than emitting
two endpoints) also means the browser only interpolates short distances between
neighbours, which sidesteps the desaturated-middle problem described in
https://www.joshwcomeau.com/css/make-beautiful-gradients/ without depending on
`in oklch`, whose support is not yet universal.

Run:  python3 tools/night-gradient.py
Then paste the CSS block over --night-gradient in css/site.css, update
--night-low to the final stop, and mirror both into capability-sheet.html.
"""

import math
import colorsys

# --- The ramp, in OKLCH ---------------------------------------------------
# L = perceptual lightness, C = chroma (the richness), H = hue in degrees.
LIGHT_SOURCE = (0.300, 0.120, 264)   # upper-left, where the light falls
FAR_CORNER   = (0.125, 0.050, 258)   # blue-black
STOPS        = 11

# Falloff shaping. Lightness drops fast then trails off, the way real light
# does; chroma is held high through the mid-range so nothing greys out.
EASE_LIGHTNESS = 0.72
EASE_CHROMA    = 1.25

# Anything set on the band, checked against the brightest stop.
ON_NIGHT = {
    'white':        (255, 255, 255),
    'brass':        (194, 161, 99),
    'brass-bright': (226, 203, 149),
    'jewel-bright': (77, 219, 166),
    'cream-dim':    (191, 183, 165),
}
AA = 4.5


def oklch_to_srgb(L, C, H):
    """OKLCH -> 8-bit sRGB. Returns (rgb, out_of_gamut)."""
    a = C * math.cos(math.radians(H))
    b = C * math.sin(math.radians(H))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    linear = (
         4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )
    clipped = any(c < -0.0005 or c > 1.0005 for c in linear)
    out = []
    for c in linear:
        c = max(0.0, min(1.0, c))
        v = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
        out.append(round(v * 255))
    return tuple(out), clipped


def luminance(rgb):
    c = [v / 255 for v in rgb]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def saturation(rgb):
    _, _, s = colorsys.rgb_to_hls(*[v / 255 for v in rgb])
    return round(s * 100)


def build():
    L0, C0, H0 = LIGHT_SOURCE
    L1, C1, H1 = FAR_CORNER
    ramp = []
    for i in range(STOPS):
        p = i / (STOPS - 1)
        tl = p ** EASE_LIGHTNESS
        tc = p ** EASE_CHROMA
        rgb, clipped = oklch_to_srgb(
            L0 + (L1 - L0) * tl,
            C0 + (C1 - C0) * tc,
            H0 + (H1 - H0) * tl,
        )
        ramp.append((round(p * 100), '#%02x%02x%02x' % rgb, rgb, clipped))
    return ramp


def main():
    ramp = build()
    peak = ramp[0][2]

    print('stops')
    for pos, hexv, rgb, clipped in ramp:
        flag = '  OUT OF GAMUT' if clipped else ''
        print(f'  {pos:>3}%  {hexv}  sat {saturation(rgb):>3}%{flag}')

    worst_sat = min(saturation(r[2]) for r in ramp)
    print(f'\nlowest saturation across ramp: {worst_sat}%   (below ~65% reads as grey)')
    print(f'luminance range: {luminance(peak) / luminance(ramp[-1][2]):.0f}x'
          f'   (below ~5x is invisible on most monitors)')

    print('\ncontrast at the brightest stop')
    failed = False
    for name, rgb in ON_NIGHT.items():
        r = contrast(rgb, peak)
        ok = r >= AA
        failed |= not ok
        print(f'  {name:<14}{r:>6.2f}:1  {"pass" if ok else "FAIL"}')

    print('\n--- paste over --night-gradient in css/site.css ---')
    print('    --night-gradient:\n        radial-gradient(130% 100% at 22% -8%,')
    for i, (pos, hexv, _, _) in enumerate(ramp):
        print(f'            {hexv} {pos:>3}%{"," if i < len(ramp) - 1 else ");"}')
    print(f'\n    --night-low: {ramp[-1][1]};   /* must equal the final stop */')

    if failed:
        raise SystemExit('\nA colour fails AA against the brightest stop. '
                         'Lower LIGHT_SOURCE lightness and re-run.')


if __name__ == '__main__':
    main()
