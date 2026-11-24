"""Verify label/route coordinates against Copernicus GLO-30 before putting them on a card.

    python check_points.py \
        "Hörnlihütte=45.98236,7.67736:3260" "Lake X=30.68,81.46:4590" "Summit=31.0675,81.3119"

Each arg: NAME=LAT,LON[:EXPECTED_M]. Prints DEM elevation at the point, min/max within ±450 m,
and local std (≈0 means flat water). A point is suspect if EXPECTED is far outside [min, max].
Tiles are cached in ~/.cache/liltopomaps/dem (same cache realtopo.py uses).
"""
import math
import os
import sys
import urllib.request

import numpy as np
import tifffile

CACHE = os.path.expanduser("~/.cache/liltopomaps/dem")
_tiles = {}


def tile(la, lo):
    key = (la, lo)
    if key not in _tiles:
        ns, ew = ("N" if la >= 0 else "S"), ("E" if lo >= 0 else "W")
        name = f"Copernicus_DSM_COG_10_{ns}{abs(la):02d}_00_{ew}{abs(lo):03d}_00_DEM"
        path = os.path.join(CACHE, name + ".tif")
        if not os.path.exists(path):
            os.makedirs(CACHE, exist_ok=True)
            url = f"https://copernicus-dem-30m.s3.amazonaws.com/{name}/{name}.tif"
            req = urllib.request.Request(url, headers={"User-Agent": "liltopomaps"})
            with urllib.request.urlopen(req, timeout=180) as r, open(path + ".part", "wb") as f:
                f.write(r.read())
            os.rename(path + ".part", path)
        _tiles[key] = tifffile.imread(path)
    return _tiles[key]


def sample(lat, lon):
    la, lo = math.floor(lat), math.floor(lon)
    t = tile(la, lo)
    h, w = t.shape
    r, c = int((la + 1 - lat) * h), int((lon - lo) * w)
    rad = max(1, int(450 / (111320 / h)))
    win = t[max(0, r - rad):r + rad, max(0, c - rad):c + rad]
    return float(t[r, c]), float(win.min()), float(win.max()), float(t[max(0, r - 3):r + 3, max(0, c - 3):c + 3].std())


for arg in sys.argv[1:]:
    name, rest = arg.split("=", 1)
    coords, _, expected = rest.partition(":")
    lat, lon = map(float, coords.split(","))
    v, lo_, hi_, sd = sample(lat, lon)
    flag = ""
    if expected:
        e = float(expected)
        if not (lo_ - 60 <= e <= hi_ + 60):
            flag = "  <-- SUSPECT: expected %.0f m not near this point" % e
    water = "  (flat: water?)" if sd < 0.3 else ""
    print(f"{name:28} {v:7.0f} m   range ±450m {lo_:5.0f}-{hi_:5.0f}   std {sd:5.1f}{water}{flag}")
