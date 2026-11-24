"""Miniature contour map of a real place, styled like a classic survey sheet: a 384-dot wide, 1-bit card.

Data: AWS Terrain Tiles (terrarium), Copernicus GLO-30/GLO-90 and swissALTI3D - public, no API key.
Downloads are cached under ~/.cache/liltopomaps.

    python realtopo.py fuji.png                      # defaults: Mount Fuji
    python realtopo.py out.png --lat 45.9763 --lon 7.6586 --km 12 \
        --title "MATTERHORN" --local "Monte Cervino" --sub "4,478 m · Valais / Aosta" --peak 4478
"""
import argparse
import io
import logging
import math
import os
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from scipy import ndimage  # noqa: E402

from fontfallback import resolve as resolve_font  # noqa: E402  (open stand-ins off macOS)

ap = argparse.ArgumentParser()
ap.add_argument("out", nargs="?", default="realtopo.png")
ap.add_argument("--lat", type=float, default=35.40)
ap.add_argument("--lon", type=float, default=138.73)
ap.add_argument("--km", type=float, default=28, help="map width in km")
ap.add_argument("--aspect", type=float, default=1.25, help="height / width")
ap.add_argument("--title", default="MOUNT FUJI")
ap.add_argument("--local", default="富士山", help="native-script name (big, above title)")
ap.add_argument("--sub", default="3,776 m · Honshu, Japan")
ap.add_argument("--peak", type=float, default=3776, help="true summit height for the label")
ap.add_argument("--ice", action="append", default=[], metavar="LAT0,LON0,LAT1,LON1[,SPACING[,FADE]]",
                help="scatter iceberg symbols over the water inside this box (ice-choked fjords); "
                     "SPACING = mean px between bergs (default 7, larger = sparser); FADE=1 thins them out radially from the "
                     "box centre (a scatter fanning out of a fjord mouth). Repeatable.")
ap.add_argument("--no-summit", action="store_true", help="no summit marker/label (seascapes, archipelagos)")
ap.add_argument("--interval", type=float, default=100)
ap.add_argument("--major", type=float, default=0, help="bold/labelled contour every N m (default 5x interval)")
ap.add_argument("--corner", default="bl", choices=["bl", "br", "tl", "tr"], help="cartouche position")
ap.add_argument("--local-font", default=None, help="font file for the native name (default: Songti TC Bold)")
ap.add_argument("--local-index", type=int, default=2)
ap.add_argument("--local-size", type=float, default=30)
ap.add_argument("--local-tracking", type=float, default=4)
ap.add_argument("--local-bold", type=float, default=0, help="embolden native name by N px (thin hairlines)")
ap.add_argument("--local-dy", type=float, default=0,
                help="nudge the native name up (-) or down (+) by N px, for fonts with very tall line metrics (Nastaliq)")
ap.add_argument("--title-size", type=float, default=15)
ap.add_argument("--emblem", default="none", choices=["none", "swiss", "mining", "eternity", "greenland"],
                help="small emblem beside the native name (swiss cross; mining = crossed miner's hammers; "
                     "eternity = Armenian arevakhach wheel, a mirrored pair flanking the name)")
ap.add_argument("--grid", type=float, default=0, help="dotted km grid spacing (0 = off)")
ap.add_argument("--source", default="terrarium", choices=["terrarium", "copernicus", "copernicus90"],
                help="terrarium: quick global tiles; copernicus: GLO-30, better in mountains")
ap.add_argument("--swiss-patch", type=float, default=0, help="blend swissALTI3D over central N km (Switzerland)")
ap.add_argument("--shade", action="store_true", help="Swiss-style relief shading as a light stipple (light from NW)")
ap.add_argument("--label", action="append", default=[], metavar="KIND|TEXT|LAT|LON",
                help="map label; KIND = glacier/italic (spaced italic), hut, peak, place (dot + text), text; "
                     "optional 5th field font=PATH:INDEX:SIZE")
ap.add_argument("--route", default=None, metavar="LAT,LON;LAT,LON",
                help="dashed climbing route between points, snapped to the ridge crest")
ap.add_argument("--summit", default=None, metavar="LAT,LON", help="mark the highest point near here (default: map max)")
ap.add_argument("--summit-radius", type=float, default=1.0, help="km searched around --summit for the highest point")
ap.add_argument("--local2", default=None, help="second native-script line (e.g. Devanagari under Tibetan)")
ap.add_argument("--local2-font", default=None)
ap.add_argument("--local2-index", type=int, default=0)
ap.add_argument("--local2-size", type=float, default=16)
ap.add_argument("--title-font", default=None, help="font for the spaced title (default Futura Bold)")
ap.add_argument("--title-index", type=int, default=2)
ap.add_argument("--ornament", default="none",
                choices=["none", "meander", "prayerflags", "dongson", "tatau", "knotwork", "girih", "pintadera", "lion"],
                help="cartouche decoration: meander = Greek key friezes; prayerflags; dongson = bronze-drum bands; "
                     "tatau = Tahitian shark-teeth bands; knotwork = Celtic plait; girih = Persian star bands; "
                     "pintadera = Canarian stamp motifs; lion = winged lion of St Mark crest (Venice)")
ap.add_argument("--water", default="hatch", choices=["hatch", "lines"],
                help="water style: hatch (horizontal rules) or lines (engraved water-lining following the shore)")
ap.add_argument("--cartouche-at", default=None, metavar="LAT,LON",
                help="centre the cartouche on this point (over the emptiest ground) instead of a corner")
ap.add_argument("--water-rings", type=int, default=6, help="number of water-lining rings (fewer = water reads as open water)")
ap.add_argument("--minor-width", type=float, default=0.45, help="minor contour weight (pt per supersample)")
ap.add_argument("--major-width", type=float, default=1.35, help="major contour weight")
ap.add_argument("--coast-width", type=float, default=1.0, help="shoreline weight")
ap.add_argument("--north", default="arrow", choices=["arrow", "rose", "none"])
ap.add_argument("--north-corner", default=None, choices=["bl", "br", "tl", "tr"])
ap.add_argument("--route-snap", default="ridge", choices=["ridge", "none"])
ap.add_argument("--route-style", default="dash", choices=["dash", "dot"])
ap.add_argument("--hillshade", default=None, metavar="PNG",
                help="also save a shaded relief of the elevation data used (to check framing and voids)")
ap.add_argument("--cache", default=os.path.expanduser("~/.cache/liltopomaps/tiles"))
args = ap.parse_args()

UA = "liltopomaps"
TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
SF = "/System/Library/Fonts/Supplemental/"
FUTURA = SF + "Futura.ttc"          # 0 Medium, 2 Bold
CJK = SF + "Songti.ttc"             # 2 = Songti TC Bold (mincho-style serif)


# ---------------------------------------------------------------- elevation data
def to_px(lat, lon, z):
    n = 256 * 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def tile(z, x, y):
    os.makedirs(args.cache, exist_ok=True)
    path = os.path.join(args.cache, f"{z}_{x}_{y}.png")
    if not os.path.exists(path):
        req = urllib.request.Request(TILE_URL.format(z=z, x=x, y=y), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r, open(path, "wb") as f:
            f.write(r.read())
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


wkm, hkm = args.km, args.km * args.aspect
dlon = wkm / (111.32 * math.cos(math.radians(args.lat))) / 2
dlat = hkm / 110.57 / 2
north, south, west, east = args.lat + dlat, args.lat - dlat, args.lon - dlon, args.lon + dlon


def load_terrarium():
    z = 14
    while z > 6:
        x0, y0 = to_px(north, west, z)
        x1, y1 = to_px(south, east, z)
        if x1 - x0 <= 1000:
            break
        z -= 1
    tx0, ty0, tx1, ty1 = int(x0 // 256), int(y0 // 256), int(x1 // 256), int(y1 // 256)
    mosaic = np.vstack([np.hstack([tile(z, tx, ty) for tx in range(tx0, tx1 + 1)]) for ty in range(ty0, ty1 + 1)])
    print(f"terrarium zoom {z}")
    return mosaic[int(y0) - ty0 * 256:int(y1) - ty0 * 256, int(x0) - tx0 * 256:int(x1) - tx0 * 256]


def fetch(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r, open(path + ".part", "wb") as f:
            f.write(r.read())
        os.rename(path + ".part", path)
    return path


DEM_CACHE = os.path.expanduser("~/.cache/liltopomaps/dem")


def load_copernicus(arcsec=1):
    """Copernicus GLO-30 (1 arcsec), resampled to square ~30 m pixels. arcsec=3: GLO-90, for tiles
    GLO-30 doesn't publish (e.g. N39E044/N40E044 around Ararat, withheld for Armenia/Azerbaijan)."""
    import tifffile
    rows = []
    for la in range(math.floor(north), math.floor(south) - 1, -1):
        row = []
        for lo in range(math.floor(west), math.floor(east) + 1):
            ns, ew = ("N" if la >= 0 else "S"), ("E" if lo >= 0 else "W")
            name = f"Copernicus_DSM_COG_{arcsec * 10}_{ns}{abs(la):02d}_00_{ew}{abs(lo):03d}_00_DEM"
            bucket = "copernicus-dem-30m" if arcsec == 1 else "copernicus-dem-90m"
            tif = fetch(f"https://{bucket}.s3.amazonaws.com/{name}/{name}.tif",
                        os.path.join(DEM_CACHE, name + ".tif"))
            row.append((lo, tifffile.imread(tif)))
        rows.append((la, row))
    # all tiles in one latitude band share a width; stitch then crop by fractional degrees
    la_top, lo_left = rows[0][0] + 1, rows[0][1][0][0]
    th, tw = rows[0][1][0][1].shape
    mosaic = np.vstack([np.hstack([t for _, t in row]) for _, row in rows])
    r0, r1 = int((la_top - north) * th), int((la_top - south) * th)
    c0, c1 = int((west - lo_left) * tw), int((east - lo_left) * tw)
    crop = mosaic[r0:r1, c0:c1].astype(np.float64)
    res = max(8.0, min(30.0, wkm * 1000 / 800))  # finer grid for small maps (swiss patch has 8 m cells)
    out_w = round(wkm * 1000 / res)
    out_h = round(hkm * 1000 / res)
    return ndimage.zoom(crop, (out_h / crop.shape[0], out_w / crop.shape[1]), order=1)


def wgs84_to_lv95(lat, lon):
    """swisstopo approximate formulas (~1 m)."""
    p = (lat * 3600 - 169028.66) / 10000
    l = (lon * 3600 - 26782.5) / 10000
    e = 2600072.37 + 211455.93 * l - 10938.51 * l * p - 0.36 * l * p ** 2 - 44.54 * l ** 3
    n = (1200147.07 + 308807.95 * p + 3745.25 * l ** 2 + 76.63 * p ** 2
         - 194.56 * l ** 2 * p + 119.79 * p ** 3)
    return e, n


def swiss_patch(elev, km):
    """Blend swissALTI3D (2 m, downsampled) over the central km x km - fixes satellite voids on steep peaks."""
    import json
    import tifffile
    H, W = elev.shape
    half_lat, half_lon = (km / 2) / 110.57, (km / 2) / (111.32 * math.cos(math.radians(args.lat)))
    bbox = f"{args.lon - half_lon},{args.lat - half_lat},{args.lon + half_lon},{args.lat + half_lat}"
    url = f"https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissalti3d/items?bbox={bbox}&limit=100"
    latest = {}
    while url:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
            page = json.load(r)
        for f in page["features"]:
            year, tid = f["id"].split("_")[1:3]
            href = next(a["href"] for k, a in f["assets"].items() if k.endswith("_2_2056_5728.tif"))
            if tid not in latest or year > latest[tid][0]:
                latest[tid] = (year, href)
        url = next((ln["href"] for ln in page.get("links", []) if ln.get("rel") == "next"), None)
    if not latest:
        print("swiss patch: no swissALTI3D coverage here")
        return elev
    tiles = {}
    for tid, (year, href) in latest.items():
        a = tifffile.imread(fetch(href, os.path.join(DEM_CACHE, "swiss", f"{year}_{tid}.tif"))).astype(np.float64)
        a[a < -1000] = np.nan
        tiles[tid] = a.reshape(125, 4, 125, 4).mean(axis=(1, 3))  # 8 m cells
    print(f"swiss patch: {len(tiles)} swissALTI3D tiles")
    ii, jj = np.mgrid[0:H, 0:W]
    lat = north - (ii + 0.5) / H * (north - south)
    lon = west + (jj + 0.5) / W * (east - west)
    e, n = wgs84_to_lv95(lat, lon)
    fine = np.full_like(elev, np.nan)
    ek, nk = np.floor(e / 1000).astype(int), np.floor(n / 1000).astype(int)
    for tid, a in tiles.items():
        te, tn = map(int, tid.split("-"))
        m = (ek == te) & (nk == tn)
        c = np.clip(((e[m] - te * 1000) / 8).astype(int), 0, 124)
        r = np.clip(((tn * 1000 + 1000 - n[m]) / 8).astype(int), 0, 124)
        fine[m] = a[r, c]
    # feathered square window
    dy = np.abs(lat - args.lat) / half_lat
    dx = np.abs(lon - args.lon) / half_lon
    w = np.clip((1 - np.maximum(dx, dy)) / 0.25, 0, 1)
    w[np.isnan(fine)] = 0
    return np.where(w > 0, w * np.nan_to_num(fine) + (1 - w) * elev, elev)


elev = (load_copernicus() if args.source == "copernicus" else
        load_copernicus(3) if args.source == "copernicus90" else load_terrarium())
if args.swiss_patch:
    elev = swiss_patch(elev, args.swiss_patch)
H, W = elev.shape
print(f"{W}x{H} samples, {elev.min():.0f}-{elev.max():.0f} m")
if args.hillshade:  # shaded relief of the data actually used
    gy, gx = np.gradient(elev)
    Image.fromarray(np.clip(128 + (gy - gx) * 1.5, 0, 255).astype(np.uint8)).save(args.hillshade)

smooth = ndimage.gaussian_filter(elev, 1.2)

# lakes: large, perfectly flat patches above sea level
flatness = ndimage.maximum_filter(elev, 5) - ndimage.minimum_filter(elev, 5)
lab, n = ndimage.label((flatness < 0.6) & (elev > 1))
sizes = ndimage.sum(np.ones_like(elev), lab, range(1, n + 1))
cell_m2 = (wkm * 1000 / W) * (hkm * 1000 / H)
min_lake = max(40000, wkm * hkm * 1e6 * 0.0004)  # >= 4 ha, and >= 0.04% of the sheet on big maps
water = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s * cell_m2 > min_lake])
water = ndimage.binary_closing(water, iterations=2)
sea = smooth < 0.5
if sea.mean() < 0.01:  # ignore stray sub-zero samples
    sea[:] = False

# ---------------------------------------------------------------- layout (final px)
OUT_W = 384
FRAME = 9                              # outer rule + gap + inner rule
MAP_W = OUT_W - 2 * FRAME
MAP_H = round(MAP_W * H / W)
OUT_H = MAP_H + 2 * FRAME
S = 2                                  # supersample


# ---------------------------------------------------------------- terrain (matplotlib)
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)  # quiet weight-matching notices
try:
    futura = resolve_font(FUTURA, 0)[0]
    font_manager.fontManager.addfont(futura)
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=futura).get_name()
except Exception:
    pass
plt.rcParams["hatch.linewidth"] = 0.9 * S

fig = plt.figure(figsize=(MAP_W * S / 100, MAP_H * S / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W - 1)
ax.set_ylim(H - 1, 0)
ax.axis("off")

step = args.interval
major_every = args.major or step * 5
terrain = np.where(water | sea, np.nan, smooth)
levels = np.arange(math.ceil(max(np.nanmin(terrain), 1) / step) * step, np.nanmax(terrain), step)
minor = [v for v in levels if v % major_every]
major = [v for v in levels if v % major_every == 0]
ax.contour(terrain, levels=minor, colors="k", linewidths=args.minor_width * S)
cs = ax.contour(terrain, levels=major, colors="k", linewidths=args.major_width * S)
ax.clabel(cs, fmt=lambda v: f"{v:,.0f}", fontsize=5.6 * S, inline_spacing=2 * S)

for mask in (water, sea):
    if mask.any():
        m = mask.astype(float)
        ax.contour(m, levels=[0.5], colors="k", linewidths=args.coast_width * S)

if args.summit:
    sla, slo = map(float, args.summit.split(","))
    r0 = int((north - sla) / (north - south) * H)
    c0 = int((slo - west) / (east - west) * W)
    rad = max(3, int(args.summit_radius / (wkm / W)))  # search around the given point
    win = smooth[max(0, r0 - rad):r0 + rad, max(0, c0 - rad):c0 + rad]
    wy, wx = np.unravel_index(np.argmax(win), win.shape)
    py, px = max(0, r0 - rad) + wy, max(0, c0 - rad) + wx
else:
    py, px = np.unravel_index(np.argmax(smooth), smooth.shape)
if not args.no_summit:
    ax.plot(px, py, marker="^", color="k", markersize=4.5 * S, markeredgewidth=0)

buf = io.BytesIO()
fig.savefig(buf, format="png", facecolor="white")
plt.close(fig)
terrain_img = Image.open(buf).convert("L").resize((MAP_W * S, MAP_H * S), Image.LANCZOS)

# ---------------------------------------------------------------- frame + cartouche (PIL)
canvas = Image.new("L", (OUT_W * S, OUT_H * S), 255)
canvas.paste(terrain_img, (FRAME * S, FRAME * S))
d = ImageDraw.Draw(canvas)


def geo_to_px(lat, lon):
    return FRAME + (lon - west) / (east - west) * MAP_W, FRAME + (north - lat) / (north - south) * MAP_H


if args.shade:
    cell = wkm * 1000 / W
    gy, gx = np.gradient(smooth, cell)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)                          # light from the north-west, 45 deg up
    az, alt = math.radians(315), math.radians(45)
    hs = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    shadow = np.clip((0.55 - hs) * 0.5, 0, 0.22)         # only shadowed slopes get dots
    shadow[water | sea] = 0
    sh = np.asarray(Image.fromarray((shadow * 255).astype(np.uint8)).resize((MAP_W, MAP_H), Image.BILINEAR)) / 255
    dots = np.random.default_rng(7).random(sh.shape) < sh
    for yy, xx in zip(*np.nonzero(dots)):
        X, Y = (FRAME + xx) * S, (FRAME + yy) * S
        d.rectangle([X, Y, X + S - 1, Y + S - 1], fill=0)
if args.grid:
    gpx = MAP_W / wkm * args.grid
    for i in range(1, int(MAP_W / gpx) + 1):
        gx = FRAME + i * gpx
        for yy in range(FRAME, FRAME + MAP_H, 4):
            d.rectangle([gx * S, yy * S, gx * S + S - 1, yy * S + S - 1], fill=0)
    for i in range(1, int(MAP_H / gpx) + 1):
        gy = FRAME + i * gpx
        for xx in range(FRAME, FRAME + MAP_W, 4):
            d.rectangle([xx * S, gy * S, xx * S + S - 1, gy * S + S - 1], fill=0)


def font(path, size, index=0):
    path, index = resolve_font(path, index)
    return ImageFont.truetype(path, round(size * S), index=index)


def tracked(xy, text, f, tracking, anchor_center=False, bold=0.0):
    """Draw letter-spaced text; returns width. bold > 0 thickens strokes (stroke in the same colour)."""
    sw = round(bold * S)
    x, y = xy
    if tracking == 0:  # draw as one run so raqm can shape Tibetan / Devanagari / Arabic properly
        total = f.getlength(text)
        d.text((x - (total / 2 if anchor_center else 0), y), text, font=f, fill=0)
        return total
    widths = [f.getlength(c) for c in text]
    total = sum(widths) + tracking * S * (len(text) - 1)
    if anchor_center:
        x -= total / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=f, fill=0, stroke_width=sw, stroke_fill=0)
        x += w + tracking * S
    return total


def box(x0, y0, x1, y1, outer=2.0, gap=2.0, inner=0.8):
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=255)
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], outline=0, width=round(outer * S))
    g = outer + gap
    d.rectangle([(x0 + g) * S, (y0 + g) * S, (x1 - g) * S, (y1 - g) * S], outline=0, width=max(1, round(inner * S)))


# water: clear, then crisp horizontal hatching every 3 dots (classic survey style)
wmask = Image.fromarray(((water | sea) * 255).astype(np.uint8)).resize((MAP_W * S, MAP_H * S), Image.BILINEAR)
wmask = wmask.point(lambda v: 255 if v > 110 else 0)
hatch = Image.new("L", wmask.size, 255)
hd = ImageDraw.Draw(hatch)
if args.water == "lines":
    # engraved water-lining: rings parallel to the shore, spreading out with distance
    dist = ndimage.distance_transform_edt(np.asarray(wmask) > 0) / S  # final px from shore
    ring = np.zeros_like(dist, dtype=bool)
    for r in (2.5, 5.5, 9, 13.5, 19, 26)[:args.water_rings]:
        ring |= (dist >= r) & (dist < r + 1.0)
    hatch = Image.fromarray(np.where(ring, 0, 255).astype(np.uint8))
else:
    for yy in range(0, wmask.height, 3 * S):
        hd.line([(0, yy), (wmask.width, yy)], fill=0, width=S)
inner = wmask.filter(__import__("PIL.ImageFilter", fromlist=["MinFilter"]).MinFilter(2 * S + 1))  # keep hatch off the shoreline
region = canvas.crop((FRAME * S, FRAME * S, FRAME * S + MAP_W * S, FRAME * S + MAP_H * S))
region.paste(255, mask=inner)
region.paste(hatch, mask=inner)
canvas.paste(region, (FRAME * S, FRAME * S))

# ice-choked water: chart-style iceberg symbols (small irregular outlines, the tiniest as dots)
if args.ice:
    shore = ndimage.distance_transform_edt(np.asarray(wmask) > 0) / S
    rng = np.random.default_rng(7)
    for spec in args.ice:
        v = [float(q) for q in spec.split(",")]
        la0, lo0, la1, lo1 = v[:4]
        g = v[4] if len(v) > 4 else 7.0
        fade = len(v) > 5 and v[5] > 0
        xa, ya = geo_to_px(max(la0, la1), min(lo0, lo1))
        xb, yb = geo_to_px(min(la0, la1), max(lo0, lo1))
        yy = ya
        while yy < yb:
            xx = xa + rng.uniform(0, g)
            while xx < xb:
                bx, by = xx + rng.uniform(-g, g) * 0.35, yy + rng.uniform(-g, g) * 0.35
                mx, my = int((bx - FRAME) * S), int((by - FRAME) * S)
                rad = rng.choice([0.9, 1.6, 2.2, 2.8, 3.6], p=[0.25, 0.25, 0.22, 0.18, 0.10])
                rn = math.hypot((bx - (xa + xb) / 2) / ((xb - xa) / 2), (by - (ya + yb) / 2) / ((yb - ya) / 2))
                if fade and rng.uniform() > 1 - rn:
                    xx += g
                    continue
                if 0 <= mx < shore.shape[1] and 0 <= my < shore.shape[0] and shore[my, mx] > rad + 2:
                    if rad < 1:
                        d.ellipse([(bx - 0.9) * S, (by - 0.9) * S, (bx + 0.9) * S, (by + 0.9) * S], fill=0)
                    else:
                        k = rng.integers(5, 8)
                        ang = np.sort(rng.uniform(0, 2 * np.pi, k))
                        rr = rad * rng.uniform(0.6, 1.15, k)
                        poly = [((bx + r_ * math.cos(a_) * 1.25) * S, (by + r_ * math.sin(a_)) * S) for a_, r_ in zip(ang, rr)]
                        d.polygon(poly, fill=255, outline=0, width=S)
                xx += g
            yy += g * 0.8

# climbing route: straight segments snapped to the local crest, drawn dashed with a white casing
if args.route:
    pts = [tuple(map(float, q.split(","))) for q in args.route.split(";")]
    cell = wkm * 1000 / W
    path = []
    for (la0, lo0), (la1, lo1) in zip(pts, pts[1:]):
        x0, y0 = geo_to_px(la0, lo0)
        x1, y1 = geo_to_px(la1, lo1)
        n_s = max(2, int(math.hypot(x1 - x0, y1 - y0) / 2))
        for i in range(n_s + 1):
            t = i / n_s
            path.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    # snap each interior point perpendicular to the path onto the highest ground (+-6 px)
    snapped = [path[0]]
    for i in range(1, len(path) - 1):
        if args.route_snap == "none":
            snapped.append(path[i])
            continue
        (xa, ya), (xb, yb) = path[i - 1], path[i + 1]
        nx_, ny_ = -(yb - ya), xb - xa
        nl = math.hypot(nx_, ny_) or 1
        nx_, ny_ = nx_ / nl, ny_ / nl
        best = None
        for off in np.linspace(-6, 6, 25):
            qx, qy = path[i][0] + nx_ * off, path[i][1] + ny_ * off
            r = int(np.clip((qy - FRAME) / MAP_H * H, 0, H - 1))
            c = int(np.clip((qx - FRAME) / MAP_W * W, 0, W - 1))
            v = smooth[r, c] - abs(off) * 2  # mild preference for the straight line
            if best is None or v > best[0]:
                best = (v, qx, qy)
        snapped.append((best[1], best[2]))
    snapped.append(path[-1])
    xs = np.convolve([q[0] for q in snapped], np.ones(5) / 5, mode="same")
    ys = np.convolve([q[1] for q in snapped], np.ones(5) / 5, mode="same")
    xs[:2], ys[:2], xs[-2:], ys[-2:] = [q[0] for q in snapped[:2]], [q[1] for q in snapped[:2]], \
        [q[0] for q in snapped[-2:]], [q[1] for q in snapped[-2:]]
    line = [(x * S, y * S) for x, y in zip(xs, ys)]
    d.line(line, fill=255, width=5 * S, joint="curve")
    if args.route_style == "dot":
        acc = 0.0
        for (xa, ya), (xb, yb) in zip(line, line[1:]):
            acc += math.hypot(xb - xa, yb - ya)
            if acc >= 4 * S:
                acc = 0.0
                d.ellipse([xb - 1.3 * S, yb - 1.3 * S, xb + 1.3 * S, yb + 1.3 * S], fill=0)
        line = []
    acc, on = 0.0, True
    for (xa, ya), (xb, yb) in zip(line, line[1:]):
        seg = math.hypot(xb - xa, yb - ya)
        if on:
            d.line([(xa, ya), (xb, yb)], fill=0, width=2 * S)
        acc += seg
        if acc > (4 if on else 3) * S:
            acc, on = 0.0, not on

def halo_text(xy, text, f, anchor):
    d.text(xy, text, font=f, fill=255, anchor=anchor, stroke_width=round(2.2 * S), stroke_fill=255)
    d.text(xy, text, font=f, fill=0, anchor=anchor)


for spec in args.label:
    parts = spec.split("|")
    kind, text, la, lo = parts[:4]
    custom = None
    if len(parts) > 4 and parts[4].startswith("font="):
        fp, fi, fs = parts[4][5:].rsplit(":", 2)
        custom = font(fp, float(fs), int(fi))
    x, y = geo_to_px(float(la), float(lo))
    if kind == "place":  # village dot + name to the right
        d.ellipse([(x - 2.2) * S, (y - 2.2) * S, (x + 2.2) * S, (y + 2.2) * S], fill=0, outline=255, width=S)
        halo_text(((x + 5) * S, y * S), text, custom or font(FUTURA, 10, 0), "lm")
    elif kind == "text":  # free text centred on the point (with halo)
        halo_text((x * S, y * S), text, custom or font(FUTURA, 10, 0), "mm")
    elif kind in ("glacier", "italic"):
        f = custom or font(FUTURA, 10, 1)  # Futura Medium Italic
        widths = [f.getlength(c) for c in text]
        total = sum(widths) + 1.6 * S * (len(text) - 1)
        for halo in (True, False):  # all halos first, so they never bite into neighbouring letters
            cx = x * S - total / 2
            for ch, w_ in zip(text, widths):
                if halo:
                    d.text((cx, y * S), ch, font=f, fill=255, anchor="lm", stroke_width=round(1.5 * S), stroke_fill=255)
                else:
                    d.text((cx, y * S), ch, font=f, fill=0, anchor="lm")
                cx += w_ + 1.6 * S
    elif kind == "hut":
        d.rectangle([(x - 4) * S, (y - 4) * S, (x + 4) * S, (y + 4) * S], fill=255)
        d.rectangle([(x - 2.5) * S, (y - 1) * S, (x + 2.5) * S, (y + 2.5) * S], fill=0)
        d.polygon([((x - 3.5) * S, (y - 0.5) * S), (x * S, (y - 4) * S), ((x + 3.5) * S, (y - 0.5) * S)], fill=0)
        d.text(((x + 6) * S, y * S), text, font=font(FUTURA, 10, 0), fill=0, anchor="lm",
               stroke_width=round(1.5 * S), stroke_fill=255)
    elif kind == "summit":  # snap to the highest point within 3 km, then mark like a peak
        rad = max(2, int(3.0 / (wkm / W)))
        r0 = int((y - FRAME) / MAP_H * H)
        c0 = int((x - FRAME) / MAP_W * W)
        win = smooth[max(0, r0 - rad):r0 + rad, max(0, c0 - rad):c0 + rad]
        wy, wx = np.unravel_index(np.argmax(win), win.shape)
        x = FRAME + (max(0, c0 - rad) + wx) / W * MAP_W
        y = FRAME + (max(0, r0 - rad) + wy) / H * MAP_H
        d.ellipse([(x - 5) * S, (y - 5) * S, (x + 5) * S, (y + 5) * S], fill=255)
        d.polygon([(x * S, (y - 3.5) * S), ((x - 3.5) * S, (y + 2.5) * S), ((x + 3.5) * S, (y + 2.5) * S)], fill=0)
        halo_text((x * S, (y + 5) * S), text, custom or font(FUTURA, 9.5, 2), "mt")
    elif kind == "peak":
        d.polygon([(x * S, (y - 3.5) * S), ((x - 3.5) * S, (y + 2.5) * S), ((x + 3.5) * S, (y + 2.5) * S)], fill=0)
        halo_text((x * S, (y - 6) * S), text, custom or font(FUTURA, 9.5, 2), "ms")

# sheet frame: heavy outer rule, thin inner rule
d.rectangle([1 * S, 1 * S, (OUT_W - 2) * S, (OUT_H - 2) * S], outline=0, width=3 * S)
d.rectangle([(FRAME - 1) * S, (FRAME - 1) * S, (OUT_W - FRAME) * S, (OUT_H - FRAME) * S], outline=0, width=1 * S)

# summit label with white halo
if not args.no_summit:
    lx, ly = FRAME + px / (W - 1) * MAP_W, FRAME + py / (H - 1) * MAP_H
    f_peak = font(FUTURA, 10, 2)
    label = f"{args.peak:,.0f}" if args.peak else f"{elev[py, px]:,.0f}"  # measured height at the marked summit
    tw = f_peak.getlength(label) / S
    # clear a halo around the marker and a boxed label above it, so dense summit contours don't crowd them
    d.ellipse([(lx - 6) * S, (ly - 6) * S, (lx + 6) * S, (ly + 6) * S], fill=255)
    d.polygon([(lx * S, (ly - 4) * S), ((lx - 4) * S, (ly + 3) * S), ((lx + 4) * S, (ly + 3) * S)], fill=0)
    bx0, by0, bx1, by1 = lx - tw / 2 - 4, ly - 22, lx + tw / 2 + 4, ly - 8
    d.rectangle([bx0 * S, by0 * S, bx1 * S, by1 * S], fill=255, outline=0, width=S)
    d.text((lx * S, (by1 - 3) * S), label, font=f_peak, fill=0, anchor="ms")

# cartouche
CW = 186
local_h = (args.local_size + 6) if args.local else 0
local2_h = (args.local2_size + 6) if args.local2 else 0
BANDS = ("tatau", "knotwork", "girih", "pintadera")  # top + bottom bands, drawn like dongson
orn_top = {"none": 0, "meander": 13, "prayerflags": 22, "dongson": 15, "lion": 32,
           **{b: 15 for b in BANDS}}[args.ornament]
orn_bot = {"meander": 12, "dongson": 14, **{b: 14 for b in BANDS}}.get(args.ornament, 0)
CH = 9 + orn_top + local_h + local2_h + 77 + orn_bot
M = FRAME + 7
cx0 = M if args.corner in ("bl", "tl") else OUT_W - M - CW
cy0 = OUT_H - M - CH if args.corner in ("bl", "br") else M
if args.cartouche_at:
    cla, clo = map(float, args.cartouche_at.split(","))
    ccx, ccy = geo_to_px(cla, clo)
    cx0 = min(max(M, ccx - CW / 2), OUT_W - M - CW)
    cy0 = min(max(M, ccy - CH / 2), OUT_H - M - CH)
box(cx0, cy0, cx0 + CW, cy0 + CH)
mid = cx0 + CW / 2


def meander(x0, y0, length, g=2.5):
    """Greek key frieze: square-spiral keys on a 4x4 grid (g px per step), on a running baseline."""
    u = 4 * g
    n = int(length // u)
    x0 += (length - n * u) / 2
    key = [(0, 4), (0, 0), (3, 0), (3, 3), (1, 3), (1, 1), (2, 1)]
    for i in range(n):
        bx = x0 + i * u
        d.line([((bx + a * g) * S, (y0 + b * g) * S) for a, b in key], fill=0, width=S)
    d.line([(x0 * S, (y0 + 4 * g) * S), ((x0 + n * u) * S, (y0 + 4 * g) * S)], fill=0, width=S)


def dongson(x0, y0, length, r=3.5):
    """Dong Son bronze-drum band: concentric circles (ring + dot) linked by tangent lines, between two rules."""
    step = r * 2 + 8
    n = int((length - 2 * r) // step) + 1
    x0 += (length - (n - 1) * step) / 2
    cy = y0 + 5
    xa, xb = x0 - r - 4, x0 + (n - 1) * step + r + 4
    for yr in (y0 - 1.5, y0 + 11.5):
        d.line([(xa * S, yr * S), (xb * S, yr * S)], fill=0, width=S)
    for i in range(n):
        cx = x0 + i * step
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], outline=0, width=S)
        d.ellipse([(cx - 0.8) * S, (cy - 0.8) * S, (cx + 0.8) * S, (cy + 0.8) * S], fill=0)
        if i < n - 1:  # tangent from the bottom of this circle to the top of the next
            d.line([((cx + r * 0.5) * S, (cy + r * 0.87) * S), ((cx + step - r * 0.5) * S, (cy - r * 0.87) * S)],
                   fill=0, width=S)


def prayer_flags(x0, y0, length):
    """A sagging string of lung-ta flags; the five colours as five 1-bit patterns."""
    n = int(length // 15)
    sag = 6
    xs_ = np.linspace(x0, x0 + length, 60)
    ys_ = y0 + sag * (1 - ((xs_ - x0) / length * 2 - 1) ** 2)
    d.line([(a * S, b * S) for a, b in zip(xs_, ys_)], fill=0, width=S)
    for i in range(n):
        fx = x0 + (i + 0.5) * length / n - 4.5
        t = (fx + 4.5 - x0) / length
        fy = y0 + sag * (1 - (t * 2 - 1) ** 2) + 1.5
        box_ = [fx * S, fy * S, (fx + 9) * S, (fy + 10) * S]
        kind_ = i % 5  # blue, white, red, green, yellow
        d.rectangle(box_, fill=0 if kind_ == 0 else 255, outline=0, width=S)
        if kind_ == 2:
            for yy in range(1, 10, 2):
                d.line([(fx * S, (fy + yy) * S), ((fx + 9) * S, (fy + yy) * S)], fill=0, width=S)
        elif kind_ == 3:
            for yy in range(2, 10, 3):
                for xx in range(2, 9, 3):
                    d.rectangle([(fx + xx) * S, (fy + yy) * S, (fx + xx + 1) * S - 1, (fy + yy + 1) * S - 1], fill=0)
        elif kind_ == 4:
            for k in range(-10, 10, 3):
                d.line([((fx + max(0, k)) * S, (fy + max(0, -k)) * S),
                        ((fx + min(9, k + 10)) * S, (fy + min(10, 10 - k)) * S)], fill=0, width=S)


def band_rules(xa, xb, y0, h):
    for yr in (y0 - 1.5, y0 + h + 1.5):
        d.line([(xa * S, yr * S), (xb * S, yr * S)], fill=0, width=S)


def tatau(x0, y0, length, w=6.0, h=11.0):
    """Tahitian tatau band: two rows of niho mano (shark teeth), offset half a tooth so a white zigzag runs between."""
    n = int(length // w)
    x0 += (length - n * w) / 2
    band_rules(x0, x0 + n * w, y0, h)
    t = h * 0.42
    for i in range(n):
        bx = x0 + i * w
        d.polygon([(bx * S, (y0 + h) * S), ((bx + w / 2) * S, (y0 + h - t) * S), ((bx + w) * S, (y0 + h) * S)], fill=0)
        if i < n - 1:
            tx = bx + w / 2
            d.polygon([(tx * S, y0 * S), ((tx + w / 2) * S, (y0 + t) * S), ((tx + w) * S, y0 * S)], fill=0)


def knotwork(x0, y0, length, h=11.0, P=14.0):
    """Celtic interlace: two ribbons plaited over and under, as on Pictish stones and in the Iona manuscripts."""
    n = max(1, int(length // P))
    x0 += (length - n * P) / 2
    xb = x0 + n * P
    cy, A = y0 + h / 2, h / 2 - 1.6
    xs = np.linspace(x0, xb, int(n * P * 4) + 1)

    def strand(sign, xa, xz):
        return [(x * S, (cy + sign * A * math.sin((x - x0) / P * 2 * math.pi)) * S) for x in xs[(xs >= xa) & (xs <= xz)]]

    def ribbon(pts, casing=False):
        if len(pts) > 1:
            if casing:
                d.line(pts, fill=255, width=round(5.2 * S), joint="curve")
            d.line(pts, fill=0, width=round(3.4 * S), joint="curve")
            d.line(pts, fill=255, width=round(1.2 * S), joint="curve")

    ribbon(strand(1, x0, xb))
    ribbon(strand(-1, x0, xb))
    for k in range(1, 2 * n):  # a crossing every half twist; the ribbon on top alternates
        xc = x0 + k * P / 2
        ribbon(strand(1 if k % 2 else -1, xc - P / 6, xc + P / 6), casing=True)
    band_rules(x0 - 2, xb + 2, y0, h)


def girih(x0, y0, length, h=11.0):
    """Persian girih band: eight-pointed khatam stars (two interlaced squares) linked by small cross tiles."""
    R = h / 2 + 0.6
    step = 2 * R + 5
    n = int((length - 2 * R) // step) + 1
    x0 += (length - (n - 1) * step) / 2
    cy = y0 + h / 2
    band_rules(x0 - R - 3, x0 + (n - 1) * step + R + 3, y0, h)
    for i in range(n):
        cx = x0 + i * step
        for rot in (0, math.pi / 4):  # two squares make the star; a white octagon opens its heart
            sq = [((cx + R * math.cos(rot + k * math.pi / 2)) * S, (cy + R * math.sin(rot + k * math.pi / 2)) * S)
                  for k in range(4)]
            d.polygon(sq, fill=0)
        oc = [((cx + R * 0.42 * math.cos(math.pi / 8 + k * math.pi / 4)) * S,
               (cy + R * 0.42 * math.sin(math.pi / 8 + k * math.pi / 4)) * S) for k in range(8)]
        d.polygon(oc, fill=255)
        if i < n - 1:
            mx, q = cx + step / 2, 1.8
            d.polygon([(mx * S, (cy - q) * S), ((mx + q) * S, cy * S), (mx * S, (cy + q) * S), ((mx - q) * S, cy * S)], fill=0)


def pintadera(x0, y0, length, h=11.0):
    """Canarian pintadera band: clay seal stamps, concentric rings alternating with triangle-chequered squares."""
    step = h + 5
    n = int((length - h) // step) + 1
    x0 += (length - (n - 1) * step - h) / 2
    band_rules(x0 - 3, x0 + (n - 1) * step + h + 3, y0, h)
    for i in range(n):
        bx = x0 + i * step
        if i % 2 == 0:
            cx, cy = bx + h / 2, y0 + h / 2
            for r, w in ((h / 2, 1), (h / 2 * 0.52, 1)):
                d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], outline=0, width=w * S)
            d.ellipse([(cx - 1) * S, (cy - 1) * S, (cx + 1) * S, (cy + 1) * S], fill=0)
        else:
            d.rectangle([bx * S, y0 * S, (bx + h) * S, (y0 + h) * S], outline=0, width=S)
            c = h / 3
            for a in range(3):
                for b in range(3):
                    if (a + b) % 2 == 0:
                        X, Y = bx + a * c, y0 + b * c
                        d.polygon([(X * S, (Y + c) * S), ((X + c) * S, (Y + c) * S), ((X + c) * S, Y * S)], fill=0)


def lion_band(x0, y0, length, h=28.0):
    """Crest: the winged lion of St Mark (haloed, wing raised, paw on the gospel book) between double rules."""
    lw = h * 1.4
    k = h * S * 4                                          # mask pixels per unit of lion height
    m_ = Image.new("L", (round(lw * S * 4), round(h * S * 4)), 0)
    md = ImageDraw.Draw(m_)

    def P(*pts):
        return [(px * k, py * k) for px, py in pts]

    def ell(xa, ya, xb, yb, **kw):
        md.ellipse([xa * k, ya * k, xb * k, yb * k], **kw)

    md.polygon(P((0.46, 0.47), (0.47, 0.22), (0.55, 0.07), (0.70, 0.00), (0.90, 0.01), (1.10, 0.07), (0.99, 0.15),
                 (1.05, 0.21), (0.93, 0.25), (0.97, 0.32), (0.85, 0.35), (0.87, 0.42), (0.73, 0.44), (0.64, 0.50)),
               fill=255)                                                                    # wing, scalloped edge
    for tip in ((0.66, 0.05), (0.98, 0.13), (0.92, 0.24), (0.85, 0.34)):                    # feather lines
        md.line(P((0.55, 0.47), tip), fill=0, width=round(0.03 * k))
    ell(0.07, 0.05, 0.45, 0.43, outline=255, width=round(0.05 * k))                        # halo
    ell(0.12, 0.10, 0.40, 0.38, fill=0)
    md.polygon(P(*[(0.27 + (0.125 if i % 2 == 0 else 0.095) * math.cos(i / 20 * 2 * math.pi),
                    0.25 + (0.125 if i % 2 == 0 else 0.095) * math.sin(i / 20 * 2 * math.pi)) for i in range(20)]),
               fill=255)                                                                    # shaggy mane
    ell(0.06, 0.20, 0.22, 0.33, fill=255)                                                   # muzzle
    md.polygon(P((0.20, 0.28), (0.38, 0.22), (0.50, 0.52), (0.30, 0.60)), fill=255)         # chest
    ell(0.32, 0.42, 1.12, 0.64, fill=255)                                                   # body
    for x_ in (0.41, 0.85, 1.00):                                                           # standing legs + paws
        md.rectangle([x_ * k, 0.55 * k, (x_ + 0.065) * k, 0.95 * k], fill=255)
        md.rectangle([(x_ - 0.05) * k, 0.91 * k, (x_ + 0.065) * k, 0.97 * k], fill=255)
    md.polygon(P((0.30, 0.46), (0.40, 0.54), (0.17, 0.56), (0.15, 0.50)), fill=255)         # paw raised on the book
    md.rectangle([0.02 * k, 0.56 * k, 0.24 * k, 0.92 * k], outline=255, width=round(0.05 * k))  # the gospel
    md.line(P((0.13, 0.57), (0.13, 0.91)), fill=255, width=round(0.04 * k))
    md.line(P((1.10, 0.50), (1.22, 0.47), (1.28, 0.36), (1.25, 0.24), (1.31, 0.15)), fill=255,
            width=round(0.05 * k), joint="curve")                                           # tail
    ell(1.27, 0.07, 1.38, 0.18, fill=255)                                                   # tuft
    m_ = m_.resize((round(lw * S), round(h * S)), Image.LANCZOS).point(lambda v: 255 if v > 110 else 0)
    lx = x0 + (length - lw) / 2
    canvas.paste(0, (round(lx * S), round(y0 * S)), m_)
    cy = y0 + h * 0.62
    for yr in (cy - 1.2, cy + 1.2):
        d.line([(x0 * S, yr * S), ((lx - 4) * S, yr * S)], fill=0, width=S)
        d.line([((lx + lw + 4) * S, yr * S), ((x0 + length) * S, yr * S)], fill=0, width=S)


y = cy0 + 9
if args.ornament == "meander":
    meander(cx0 + 9, cy0 + 8, CW - 18)
    meander(cx0 + 9, cy0 + CH - 8 - 10, CW - 18)
    y += orn_top
elif args.ornament == "dongson":
    dongson(cx0 + 9, cy0 + 9, CW - 18)
    dongson(cx0 + 9, cy0 + CH - 9 - 11, CW - 18)
    y += orn_top
elif args.ornament == "prayerflags":
    prayer_flags(cx0 + 7, cy0 + 9, CW - 14)
    y += orn_top
elif args.ornament in BANDS:
    band = {"tatau": tatau, "knotwork": knotwork, "girih": girih, "pintadera": pintadera}[args.ornament]
    band(cx0 + 9, cy0 + 9, CW - 18)
    band(cx0 + 9, cy0 + CH - 9 - 11, CW - 18)
    y += orn_top
elif args.ornament == "lion":
    lion_band(cx0 + 9, cy0 + 8, CW - 18)
    y += orn_top
if args.local:
    f_local = font(args.local_font or CJK, args.local_size, args.local_index)
    lw = tracked((mid * S, (y + args.local_dy) * S), args.local, f_local, args.local_tracking, anchor_center=True,
                 bold=args.local_bold) / S
    if args.emblem == "mining":  # Schlägel und Eisen: two crossed miner's hammers
        e = args.local_size * 0.95
        ex, ey = mid - lw / 2 - e - 6, y + args.local_size * 0.08
        cxm, cym = ex + e / 2, ey + e / 2
        for sgn in (1, -1):
            ang = math.radians(45 * sgn)
            ux, uy = math.sin(ang), -math.cos(ang)       # handle direction (towards the head)
            hx0, hy0 = cxm - ux * e * 0.46, cym - uy * e * 0.46
            hx1, hy1 = cxm + ux * e * 0.36, cym + uy * e * 0.36
            d.line([(hx0 * S, hy0 * S), (hx1 * S, hy1 * S)], fill=0, width=round(1.6 * S))
            px_, py_ = -uy, ux                           # head runs perpendicular to the handle
            L, Wh = e * 0.26, e * 0.11
            hc = (hx1 + ux * Wh, hy1 + uy * Wh)
            head = [(hc[0] + px_ * L + ux * Wh, hc[1] + py_ * L + uy * Wh), (hc[0] + px_ * L - ux * Wh, hc[1] + py_ * L - uy * Wh),
                    (hc[0] - px_ * L - ux * Wh, hc[1] - py_ * L - uy * Wh), (hc[0] - px_ * L + ux * Wh, hc[1] - py_ * L + uy * Wh)]
            d.polygon([(a * S, b * S) for a, b in head], fill=0)
    if args.emblem == "eternity":  # Armenian eternity sign (arevakhach), as carved on khachkars
        e = args.local_size * 0.85
        n = round(e * S)
        for side in (-1, 1):
            yy_, xx_ = np.mgrid[0:n * 4, 0:n * 4] + 0.5
            ux_, uy_ = (xx_ - n * 2) / (n * 2), (yy_ - n * 2) / (n * 2)
            r_ = np.hypot(ux_, uy_)
            u_ = (6 * (np.arctan2(uy_, ux_) * side + 2.3 * r_) / (2 * np.pi)) % 1.0
            wdt = 0.62 * np.clip(1 - r_ ** 2.2, 0, 1) ** 0.6   # blades taper to hooked tips
            m_ = (((np.abs(u_ - 0.5) < wdt / 2) & (r_ < 1)) | (r_ < 0.13)).astype(np.uint8) * 255
            m_ = Image.fromarray(m_).resize((n, n), Image.LANCZOS).point(lambda v: 255 if v > 110 else 0)
            ex = mid + side * (lw / 2 + 7 + e / 2) - e / 2
            ey = y + args.local_size * 0.62 - e / 2
            canvas.paste(0, (round(ex * S), round(ey * S)), m_)
    if args.emblem == "greenland":  # Erfalasorput: white over red, circle counterchanged (red -> black)
        fh = args.local_size * 0.55
        fw = fh * 1.5
        ex, ey = mid - lw / 2 - fw - 7, y + args.local_size * 0.62 - fh / 2
        d.rectangle([ex * S, (ey + fh / 2) * S, (ex + fw) * S, (ey + fh) * S], fill=0)
        d.rectangle([ex * S, ey * S, (ex + fw) * S, (ey + fh) * S], outline=0, width=S)
        cxf, cyf, rf = ex + fw * 7 / 18, ey + fh / 2, fh * 4 / 12
        d.pieslice([(cxf - rf) * S, (cyf - rf) * S, (cxf + rf) * S, (cyf + rf) * S], 180, 360, fill=0)
        d.pieslice([(cxf - rf) * S, (cyf - rf) * S, (cxf + rf) * S, (cyf + rf) * S], 0, 180, fill=255)
    if args.emblem == "swiss":  # white cross on a black square
        e = args.local_size * 0.62
        ex, ey = mid - lw / 2 - e - 7, y + args.local_size * 0.22
        d.rectangle([ex * S, ey * S, (ex + e) * S, (ey + e) * S], fill=0)
        a, b = e * 0.2, e * 0.6 / 2
        cxm, cym = ex + e / 2, ey + e / 2
        d.rectangle([(cxm - a / 2 * 1.0) * S, (cym - b) * S, (cxm + a / 2) * S, (cym + b) * S], fill=255)
        d.rectangle([(cxm - b) * S, (cym - a / 2) * S, (cxm + b) * S, (cym + a / 2) * S], fill=255)
    y += local_h
if args.local2:
    tracked((mid * S, y * S), args.local2, font(args.local2_font or CJK, args.local2_size, args.local2_index), 0,
            anchor_center=True)
    y += local2_h
f_title = font(args.title_font or FUTURA, args.title_size, args.title_index if args.title_font else 2)
tracked((mid * S, y * S), args.title, f_title, 2.6, anchor_center=True)
y += args.title_size + 6
d.line([((mid - 62) * S, y * S), ((mid + 62) * S, y * S)], fill=0, width=S)
d.ellipse([(mid - 2) * S, (y - 2) * S, (mid + 2) * S, (y + 2) * S], fill=0)
y += 6
f_sub = font(FUTURA, 10.5, 0)
d.text((mid * S, y * S), args.sub, font=f_sub, fill=0, anchor="mt")
y += 17

# scale bar: round length ~ 1/5 of map width
km_per_px = wkm / MAP_W
nice = min((v for v in (0.5, 1, 2, 2.5, 5, 10, 20, 50) if v >= wkm / 6), default=50)
bar = nice / km_per_px
bx0, by = mid - bar / 2 - 18, y + 2
for i in range(4):
    seg = bar / 4
    d.rectangle([(bx0 + i * seg) * S, by * S, (bx0 + (i + 1) * seg) * S, (by + 4) * S],
                fill=0 if i % 2 == 0 else 255, outline=0, width=S)
f_small = font(FUTURA, 9, 0)
d.text(((bx0 + bar + 4) * S, (by + 2) * S), f"{nice:g} km", font=f_small, fill=0, anchor="lm")
d.text((mid * S, (by + 9) * S), f"contours {step:g} m  ·  "
       f"{abs(args.lat):.2f}°{'N' if args.lat >= 0 else 'S'} {abs(args.lon):.2f}°{'E' if args.lon >= 0 else 'W'}",
       font=f_small, fill=0, anchor="mt")

# north arrow: slim, half-filled head, top corner opposite the cartouche side
nc = args.north_corner or {"bl": "tr", "br": "tl", "tl": "br", "tr": "bl"}[args.corner]
if args.north == "rose":
    R = 21
    rx = M + R + 4 if nc in ("bl", "tl") else OUT_W - M - R - 4
    ry = M + R + 10 if nc in ("tl", "tr") else OUT_H - M - R - 4
    d.ellipse([(rx - R - 3) * S, (ry - R - 3) * S, (rx + R + 3) * S, (ry + R + 3) * S], fill=255)
    d.ellipse([(rx - R * 0.62) * S, (ry - R * 0.62) * S, (rx + R * 0.62) * S, (ry + R * 0.62) * S], outline=0, width=S)
    d.ellipse([(rx - R * 0.66) * S, (ry - R * 0.66) * S, (rx + R * 0.66) * S, (ry + R * 0.66) * S], outline=0, width=S)
    for k in range(8):  # 8-point star: long cardinal points, short intercardinals, each half filled
        ang = math.radians(k * 45 - 90)
        L = R if k % 2 == 0 else R * 0.55
        w_ = R * 0.17
        tip = (rx + L * math.cos(ang), ry + L * math.sin(ang))
        lft = (rx + w_ * math.cos(ang - math.pi / 2), ry + w_ * math.sin(ang - math.pi / 2))
        rgt = (rx + w_ * math.cos(ang + math.pi / 2), ry + w_ * math.sin(ang + math.pi / 2))
        d.polygon([(tip[0] * S, tip[1] * S), (lft[0] * S, lft[1] * S), (rx * S, ry * S)], fill=0)
        d.polygon([(tip[0] * S, tip[1] * S), (rgt[0] * S, rgt[1] * S), (rx * S, ry * S)], fill=255, outline=0, width=S)
    d.text((rx * S, (ry - R - 2) * S), "N", font=font(FUTURA, 10, 2), fill=0, anchor="mb",
           stroke_width=S, stroke_fill=255)
nx = OUT_W - M - 10 if nc in ("tr", "br") else M + 10
ny = M + 6 if nc in ("tl", "tr") else OUT_H - M - 46
if args.north == "arrow":
    d.rectangle([(nx - 9) * S, (ny - 4) * S, (nx + 9) * S, (ny + 42) * S], fill=255)
    d.polygon([(nx * S, ny * S), ((nx - 6) * S, (ny + 18) * S), (nx * S, (ny + 14) * S)], fill=0)
    d.polygon([(nx * S, ny * S), ((nx + 6) * S, (ny + 18) * S), (nx * S, (ny + 14) * S)], outline=0, width=S)
    d.line([(nx * S, (ny + 14) * S), (nx * S, (ny + 28) * S)], fill=0, width=S)
    d.text((nx * S, (ny + 30) * S), "N", font=font(FUTURA, 11, 2), fill=0, anchor="mt")

out = canvas.resize((OUT_W, OUT_H), Image.LANCZOS).point(lambda v: 0 if v < 165 else 255).convert("1")
out.save(args.out)
print(out.size, "->", args.out, f"| lakes: {int(water.sum())} samples")
