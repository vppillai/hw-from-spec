#!/usr/bin/env python3
"""heatmap_count.py - count the yellow / red pixels of a vendor thin-wall heat-map capture outside its legend box (stdlib only).

The owner's bar on a printed body is "no yellow, no red on the vendor's map" (`references/dfm-printed-enclosure.md` §0, §13): read the six views of §7 step 4
(origin, three 90-degree azimuth drags, both poles) and count. The viewer frames the model in the top-left area: the legend panel (grey / yellow / red bars) stands in the RIGHT column and the tool bar
(with coloured icons) fills the BOTTOM strip, so the count covers x < legend_x * w AND y < legend_y * h and skips both strips (an L shape).
Defaults = the JLC3DP viewer at 1600 x 1200; verify on the first capture that the model never enters a skipped strip.
Reads 8-bit RGB / RGBA non-interlaced PNGs (what a browser screenshot is).
Colour read in HSV (stdlib colorsys), because the viewer shades faces: a pixel counts when saturation > 0.5 and value > 0.3,
as yellow for hue 25..70 deg (amber, shaded (191,191,0)) and as red for hue below 25 or from 335 deg (shaded red). Grey stays out (saturation 0).
usage: heatmap_count.py [--legend-x 0.78] [--legend-y 0.84] <png>...   -> "<file>: yellow N red N" per file; exit 1 if any view has yellow or red.
       heatmap_count.py --selftest
"""
import argparse, colorsys, os, struct, sys, tempfile, zlib

def read_png(path):
    """-> (w, h, rows) with rows = list of bytes, each w * 3 RGB bytes."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos = 8; idat = b""; w = h = depth = ctype = interlace = None
    while pos < len(data):
        ln, tag = struct.unpack(">I4s", data[pos:pos + 8]); body = data[pos + 8:pos + 8 + ln]; pos += 12 + ln
        if tag == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            break
    if not (depth == 8 and ctype in (2, 6) and interlace == 0):
        raise ValueError(f"unsupported PNG (depth {depth}, colour type {ctype}, interlace {interlace}) - 8-bit RGB / RGBA non-interlaced only")
    bpp = 3 if ctype == 2 else 4; stride = w * bpp; raw = zlib.decompress(idat); rows = []; prev = bytearray(stride); p = 0
    for _ in range(h):
        f = raw[p]; line = bytearray(raw[p + 1:p + 1 + stride]); p += 1 + stride
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0; b = prev[i]; c = prev[i - bpp] if i >= bpp else 0
            if f == 1: line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c); pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        rows.append(b"".join(line[j:j + 3] for j in range(0, stride, bpp)) if bpp == 4 else bytes(line)); prev = line
    return w, h, rows

def count(path, xf=0.78, yf=0.84):
    w, h, rows = read_png(path); y = r = 0; xmax = int(w * xf); ymax = int(h * yf)
    for j in range(ymax):                                                  # above the tool bar
        row = rows[j]
        for i in range(xmax):                                              # left of the legend column
            k = classify(row[3 * i], row[3 * i + 1], row[3 * i + 2])
            if k == "y": y += 1
            elif k == "r": r += 1
    return y, r

def classify(R, G, B):
    """'y' / 'r' / None by HSV: saturation > 0.5, value > 0.3; yellow hue 25..70 deg, red below 25 or from 335 deg"""
    hi = max(R, G, B)
    if hi <= 0.3 * 255 or hi - min(R, G, B) <= 0.5 * hi: return None          # dark or grey: the fast path skips colorsys
    hue = colorsys.rgb_to_hsv(R / 255, G / 255, B / 255)[0] * 360
    return "y" if 25 <= hue < 70 else ("r" if hue < 25 or hue >= 335 else None)

def write_png(path, w, h, pix, rgba=False):
    """minimal RGB / RGBA writer for the selftest (filter 0)"""
    raw = b"".join(b"\x00" + bytes(v for x in range(w) for v in (pix(x, y) + ((255,) if rgba else ()))) for y in range(h))
    def chunk(tag, body): return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6 if rgba else 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

def selftest():
    def pix(x, y):
        if 10 <= x < 20 and 10 <= y < 20: return (255, 230, 0)      # 100 yellow px in the model area
        if 180 <= x < 190 and 5 <= y < 15: return (255, 230, 0)     # 100 yellow px in the legend column (any height): skipped
        if 170 <= x < 190 and 90 <= y < 100: return (255, 0, 0)     # red inside the legend box (ignored by default)
        return (160, 160, 160)
    shades = {"y": [(255, 230, 0), (191, 191, 0), (180, 160, 0), (124, 112, 0), (255, 191, 0)],   # pure, viewer-shaded, amber
              "r": [(255, 0, 0), (178, 0, 0), (255, 69, 0)], None: [(160, 160, 160), (60, 60, 60), (0, 0, 255), (0, 200, 0), (40, 36, 0)]}
    for want, cs in shades.items():
        for c in cs: assert classify(*c) == want, (c, classify(*c), want)
    d = tempfile.mkdtemp()
    sh = os.path.join(d, "shaded.png"); write_png(sh, 40, 20, lambda x, y: (191, 191, 0) if x < 10 else ((178, 0, 0) if x < 20 else (160, 160, 160)))
    assert count(sh, 1.0, 1.0) == (200, 200), count(sh, 1.0, 1.0)
    for rgba in (False, True):
        p = os.path.join(d, f"t{int(rgba)}.png"); write_png(p, 200, 100, pix, rgba=rgba)
        assert count(p) == (100, 0), (rgba, count(p))
        assert count(p, xf=1.0, yf=1.0) == (200, 200), count(p, 1.0, 1.0)
    try:
        read_png(os.path.join(d, "missing.png")); raise AssertionError("missing file must raise")
    except OSError:
        pass
    print("heatmap_count selftest OK: HSV read counts pure, shaded and amber yellow and shaded red; grey, blue, green and near-black stay out; legend / tool-bar strips skipped")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pngs", nargs="*"); ap.add_argument("--legend-x", type=float, default=0.78); ap.add_argument("--legend-y", type=float, default=0.84)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); return 0
    if not a.pngs:
        ap.print_help(); return 2
    bad = 0
    for p in a.pngs:
        try:
            y, r = count(p, a.legend_x, a.legend_y)
        except (OSError, ValueError, zlib.error) as e:
            print(f"{os.path.basename(p)}: cannot read - {e}", file=sys.stderr); return 2
        print(f"{os.path.basename(p)}: yellow {y} red {r}"); bad |= (y > 0 or r > 0)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
