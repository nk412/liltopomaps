"""Open-licence stand-ins for the macOS system fonts the cards are designed with.

resolve(path, index) returns the font unchanged when it exists. Otherwise (Linux, Windows) it returns a close
open-licence lookalike, downloaded once to ~/.cache/liltopomaps/fonts; variable fonts are cut to the matching
weight with fontTools.
"""
import os
import urllib.request

CACHE = os.path.expanduser("~/.cache/liltopomaps/fonts")
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
URW = "https://raw.githubusercontent.com/ArtifexSoftware/urw-base35-fonts/master/fonts/"
CTAN = "https://mirrors.ctan.org/fonts/tex-gyre/opentype/"

# (macOS font file, face index): (stand-in name, download URL, variable-font axes or None)
STAND_INS = {
    ("Futura.ttc", 0): ("Jost-Medium.ttf", GF + "jost/Jost%5Bwght%5D.ttf", {"wght": 500}),
    ("Futura.ttc", 1): ("Jost-MediumItalic.ttf", GF + "jost/Jost-Italic%5Bwght%5D.ttf", {"wght": 500}),
    ("Futura.ttc", 2): ("Jost-Bold.ttf", GF + "jost/Jost%5Bwght%5D.ttf", {"wght": 700}),
    ("Songti.ttc", 2): ("NotoSerifTC-Bold.ttf", GF + "notoseriftc/NotoSerifTC%5Bwght%5D.ttf", {"wght": 700}),
    ("Helvetica.ttc", 1): ("NimbusSans-Bold.ttf", URW + "NimbusSans-Bold.ttf", None),
    ("Didot.ttc", 2): ("GFSDidot-Regular.ttf", GF + "gfsdidot/GFSDidot-Regular.ttf", None),
    ("Avenir Next.ttc", 2): ("NotoSans-SemiBold.ttf", GF + "notosans/NotoSans%5Bwdth,wght%5D.ttf",
                             {"wght": 600, "wdth": 100}),
    ("Avenir Next.ttc", 3): ("NotoSans-SemiBoldItalic.ttf", GF + "notosans/NotoSans-Italic%5Bwdth,wght%5D.ttf",
                             {"wght": 600, "wdth": 100}),
    ("Avenir Next.ttc", 6): ("NotoSans-MediumItalic.ttf", GF + "notosans/NotoSans-Italic%5Bwdth,wght%5D.ttf",
                             {"wght": 500, "wdth": 100}),
    ("Kokonor.ttf", 0): ("Jomolhari-Regular.ttf", GF + "jomolhari/Jomolhari-Regular.ttf", None),
    ("Kailasa.ttc", 1): ("NotoSerifTibetan-Bold.ttf", GF + "notoseriftibetan/NotoSerifTibetan%5Bwght%5D.ttf",
                         {"wght": 700}),
    ("DevanagariMT.ttc", 1): ("NotoSerifDevanagari-Bold.ttf",
                              GF + "notoserifdevanagari/NotoSerifDevanagari%5Bwdth,wght%5D.ttf",
                              {"wght": 700, "wdth": 100}),
    ("PTSans.ttc", 1): ("PT_Sans-Web-Italic.ttf", GF + "ptsans/PT_Sans-Web-Italic.ttf", None),
    ("PTSans.ttc", 2): ("PT_Sans-Narrow-Web-Bold.ttf", GF + "ptsansnarrow/PT_Sans-Narrow-Web-Bold.ttf", None),
    ("PTSans.ttc", 6): ("PT_Sans-Web-BoldItalic.ttf", GF + "ptsans/PT_Sans-Web-BoldItalic.ttf", None),
    ("PTSans.ttc", 7): ("PT_Sans-Web-Bold.ttf", GF + "ptsans/PT_Sans-Web-Bold.ttf", None),
    ("Mshtakan.ttc", 2): ("NotoSerifArmenian-Bold.ttf", GF + "notoserifarmenian/NotoSerifArmenian%5Bwdth,wght%5D.ttf",
                          {"wght": 700, "wdth": 100}),
    ("SFArmenian.ttf", 0): ("NotoSansArmenian-Regular.ttf", GF + "notosansarmenian/NotoSansArmenian%5Bwdth,wght%5D.ttf",
                            {"wght": 400, "wdth": 100}),
    ("Palatino.ttc", 2): ("texgyrepagella-bold.otf", CTAN + "texgyrepagella-bold.otf", None),
    ("Baskerville.ttc", 4): ("LibreBaskerville-Bold.ttf", GF + "librebaskerville/LibreBaskerville%5Bwght%5D.ttf",
                             {"wght": 700}),
    ("Baskerville.ttc", 5): ("LibreBaskerville-Italic.ttf",
                             GF + "librebaskerville/LibreBaskerville-Italic%5Bwght%5D.ttf", {"wght": 400}),
    ("SFGeorgian.ttf", 0): ("NotoSerifGeorgian-Regular.ttf", GF + "notoserifgeorgian/NotoSerifGeorgian%5Bwdth,wght%5D.ttf",
                            {"wght": 400, "wdth": 100}),
    ("Diwan Thuluth.ttf", 0): ("Amiri-Regular.ttf", GF + "amiri/Amiri-Regular.ttf", None),
    ("AppleMyungjo.ttf", 0): ("NotoSerifKR-Regular.ttf", GF + "notoserifkr/NotoSerifKR%5Bwght%5D.ttf", {"wght": 400}),
    ("KefaIII.ttf", 0): ("NotoSerifEthiopic-Regular.ttf", GF + "notoserifethiopic/NotoSerifEthiopic%5Bwdth,wght%5D.ttf",
                         {"wght": 400, "wdth": 100}),
}
_done = {}


def _download(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "liltopomaps"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path + ".part", "wb") as f:
            f.write(r.read())
        os.rename(path + ".part", path)
    return path


def resolve(path, index=0):
    """(path, index) of the font to load: the font itself if installed, else its open-licence stand-in."""
    if os.path.exists(path):
        return path, index
    key = (os.path.basename(path), index)
    if key in _done:
        return _done[key], 0
    if key not in STAND_INS:
        raise SystemExit(f"font not found: {path} (index {index}), and no open stand-in is known for it; "
                         "pass an installed font file instead")
    name, url, axes = STAND_INS[key]
    out = os.path.join(CACHE, name)
    if not os.path.exists(out):
        src = _download(url, os.path.join(CACHE, "src", url.rsplit("/", 1)[1].replace("%5B", "[").replace("%5D", "]")))
        if axes:
            from fontTools.ttLib import TTFont
            from fontTools.varLib.instancer import instantiateVariableFont
            instantiateVariableFont(TTFont(src), axes, inplace=False, updateFontNames=False).save(out + ".part")
            os.rename(out + ".part", out)
        else:
            os.replace(src, out)
    print(f"font: {key[0]} #{index} not installed, using {name}")
    _done[key] = out
    return out, 0
