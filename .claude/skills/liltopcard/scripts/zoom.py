"""Nearest-neighbour zoom of regions of a 1-bit card, for checking labels/ornaments at dot level.

    python zoom.py card.png out.png x0,y0,x1,y1 [x0,y0,x1,y1 ...] [--scale 3]

Boxes are in card dots (card is 384 wide). Multiple boxes are tiled side by side.
"""
import sys

from PIL import Image

args = [a for a in sys.argv[1:] if not a.startswith("--")]
scale = 3
if "--scale" in sys.argv:
    scale = int(sys.argv[sys.argv.index("--scale") + 1])
    args = [a for a in args if a != str(scale)]
src, out, boxes = args[0], args[1], args[2:] or ["0,0,384,9999"]
im = Image.open(src)
tiles = []
for b in boxes:
    x0, y0, x1, y1 = map(int, b.split(","))
    c = im.crop((x0, y0, min(x1, im.width), min(y1, im.height)))
    tiles.append(c.resize((c.width * scale, c.height * scale), Image.NEAREST))
W = sum(t.width for t in tiles) + 10 * (len(tiles) - 1)
H = max(t.height for t in tiles)
sheet = Image.new("1", (W, H), 1)
x = 0
for t in tiles:
    sheet.paste(t, (x, 0))
    x += t.width + 10
sheet.save(out)
print(sheet.size, "->", out)
