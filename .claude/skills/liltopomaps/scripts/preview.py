"""Preview a card: dot-exact enlargement on a little paper mock-up, opened in the default image viewer.

    python preview.py card.png [--scale 3] [--no-open]

Writes previews/<card>_preview.png under the current directory (kept, so it can be found again) and opens it
unless --no-open. Nearest-neighbour scaling, so every dot of the card is visible as-is.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

args = [a for a in sys.argv[1:] if not a.startswith("--")]
scale = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 3
if "--scale" in sys.argv:
    args = [a for a in args if a != str(scale)]
src = args[0]

card = Image.open(src).convert("L")
big = card.resize((card.width * scale, card.height * scale), Image.NEAREST)

# paper mock-up: a narrow strip with blank margins either side of the card, ink a soft dark grey
margin = round(big.width * 5 / 48)
feed = 14 * scale  # blank paper above/below
paper = Image.new("L", (big.width + 2 * margin, big.height + 2 * feed), 250)
paper.paste(big.point(lambda v: 40 if v < 128 else 250), (margin, feed))
d = ImageDraw.Draw(paper)
for x in range(0, paper.width, 6):  # serrated torn edges
    d.polygon([(x, 0), (x + 3, 5), (x + 6, 0)], fill=200)
    d.polygon([(x, paper.height), (x + 3, paper.height - 5), (x + 6, paper.height)], fill=200)
bg = Image.new("L", (paper.width + 60, paper.height + 60), 120)
bg.paste(paper, (30, 30))

out_dir = os.path.abspath("previews")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, os.path.splitext(os.path.basename(src))[0] + "_preview.png")
bg.save(out)
print(f"preview ({card.width}x{card.height} dots) -> {out}")
if "--no-open" not in sys.argv:
    opener = {"darwin": ["open"], "win32": ["cmd", "/c", "start", ""]}.get(sys.platform, ["xdg-open"])
    try:
        subprocess.run(opener + [out], check=False)
    except FileNotFoundError:
        print("no image viewer found; open the file above")
