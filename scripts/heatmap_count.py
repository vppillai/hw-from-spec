#!/usr/bin/env python3
"""heatmap_count.py - count the yellow / red pixels of a vendor thin-wall heat-map capture outside its legend box (stdlib only).

The owner's bar on a printed body is "no yellow, no red on the vendor's map" (`references/dfm-printed-enclosure.md` §1, §13): read six views
(origin, three 90-degree azimuth drags, both poles) and count. The legend (grey / yellow / red bars) sits bottom-right in the viewer, so the
count covers x < legend_x * w and y < legend_y * h (defaults for a 1600 x 1200 capture of the JLC3DP viewer - verify on the first capture).
Reads 8-bit RGB / RGBA non-interlaced PNGs (what a browser screenshot is).
usage: heatmap_count.py [--legend-x 0.78] [--legend-y 0.84] <png>...   -> "<file>: yellow N red N" per file; exit 1 if any view has yellow or red.
       heatmap_count.py --selftest
"""
import argparse, os, struct, sys, tempfile, zlib

def read_png(path):
    """-> (w, h, rows) with rows = list of bytes, each w * 3 RGB bytes."""
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos = 8; idat = b""; w = h = depth = ctype = interlace = None
    while pos < len(data):
        ln, tag = struct.unpack(">I4s", data[pos:pos + 8]); body = data[pos + 8:pos + 8 + ln]; pos += 12 + ln
        if tag == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            break
    assert depth == 8 and ctype in (2, 6) and interlace == 0, f"unsupported PNG (depth {depth}, colour type {ctype}, interlace {interlace})"
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
        rows.append(bytes(line[j:j + 3] for j in range(0, stride, bpp)) if bpp == 4 else bytes(line)); prev = line
    return w, h, rows

def count(path, xf=0.78, yf=0.84):
    w, h, rows = read_png(path); y = r = 0; xmax = int(w * xf)
    for j in range(int(h * yf)):
        row = rows[j]
        for i in range(xmax):
            R, G, B = row[3 * i], row[3 * i + 1], row[3 * i + 2]
            if R > 200 and G > 180 and B < 90: y += 1
            elif R > 200 and G < 80 and B < 80: r += 1
    return y, r

def write_png(path, w, h, pix):
    """minimal RGB writer for the selftest (filter 0)"""
    raw = b"".join(b"\x00" + bytes(v for x in range(w) for v in pix(x, y)) for y in range(h))
    def chunk(tag, body): return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

def selftest():
    def pix(x, y):
        if 10 <= x < 20 and 10 <= y < 20: return (255, 230, 0)      # 100 yellow px in the model area
        if 170 <= x < 190 and 90 <= y < 100: return (255, 0, 0)     # red inside the legend box (ignored by default)
        return (160, 160, 160)
    p = os.path.join(tempfile.mkdtemp(), "t.png"); write_png(p, 200, 100, pix)
    assert count(p) == (100, 0), count(p)
    assert count(p, xf=1.0, yf=1.0) == (100, 200), count(p, 1.0, 1.0)
    print("heatmap_count selftest OK")

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
        y, r = count(p, a.legend_x, a.legend_y); print(f"{os.path.basename(p)}: yellow {y} red {r}"); bad |= (y > 0 or r > 0)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
