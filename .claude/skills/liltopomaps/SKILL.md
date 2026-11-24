---
name: liltopomaps
description: Make and preview a miniature "playing card" terrain map of a real place from real elevation data — contours, cliffs, coastlines and lakes, survey-sheet style, with an inset cartouche carrying the place's native-script name and a local ornament. Use when the user names a place (mountain, volcano, island, caldera, canyon, lake, fjord...) and wants a map/card of it, or asks for "another card". Politely turn down places without beautiful terrain (cities, flat land) and explain why.
---

# Liltopomaps

A series of small (384 × ~475 dot, 1-bit) map cards, made to look like **little playing cards**. Every card shares
the same chassis; every card gets its own local soul. The output is always a **preview** image.

## Setup

- `$SKILL` = this skill's base directory (in this repo: `.claude/skills/liltopomaps`).
- `$PY` = a Python with `$SKILL/requirements.txt` installed (in this repo: `.venv/bin/python`).
- Shell variables don't persist between commands: write the paths out (or set them) in each command.
- Fonts: always name the macOS fonts (table under "Fonts"). Where one isn't installed (Linux, Windows), the
  renderer swaps in an open-licence lookalike, downloaded once to `~/.cache/liltopomaps/fonts`, and prints
  `font: X not installed, using Y`. Mention the stand-ins when showing the preview.

Name output files after the place (`moorea.png`) in the current directory.

## The goal: a *pretty* card — terrain only

Pretty = **beautiful organic lines and structure** that make the place recognisable at a glance. For this series
that means **terrain drawn from elevation data**: contours, cliffs, the silhouette of an island or coast, lakes.
These lines are continuous, flowing and evenly dense, and the data is consistent worldwide — every terrain card
has worked. Ask first: *what is the most beautiful relief structure of this place?*

| The place's beauty is… | Draw | Example |
|---|---|---|
| relief: peaks, cones, ridges, valleys | contour lines (+ stipple shading) | Fuji, Matterhorn, Kailash |
| cliffs, escarpments, canyons, calderas | dense contours on the drop; the cliff line is the hero | Santorini caldera rim |
| a silhouette: island, crescent, peninsula, coast | coastline + engraved water-lining (`--water lines`) | Santorini's crescent |
| lakes in relief: crater lakes, glacial/sacred lakes, fjords | hatched or water-lined water framed by contours | Kailash's lakes, Fuji Five Lakes |

**Out of scope: cities, streets, canals and other man-made structure.** A canal-ring city card (Amsterdam) was
tried: street data is irregular and fragmentary, line weights fight each other, density varies wildly, and the
result read as a wiry tangle, not a card. Don't offer or build city cards. (If someone insists on experimenting,
the idea to try next is a figure-ground plan from OSM building footprints — black blocks, white streets/canals —
not street lines.)

## Turn down places that won't make a pretty card

Before rendering anything, judge honestly. If the place won't make a pretty terrain card, **say so before spending
any effort, explain why in a sentence or two, and suggest a nearby or similar place that would work.**
Reasons to decline:

- **It's a city / man-made place** (Amsterdam, Paris, Tokyo, a landmark): its beauty is streets and buildings,
  which this style can't capture. Suggest real terrain nearby or in the same spirit (Paris → no relief worth a card;
  Rio → yes, Sugarloaf and Corcovado are superb terrain; Hong Kong → Victoria Peak and the harbour coast).
- **Flat:** the Netherlands, Kansas, most deltas and plains — contours have nothing to draw. Offer the nearest relief
  or a dramatic coast instead.
- **Featureless or uniform:** open ocean, uniform desert or ice sheet, gentle rolling hills that render as a few
  wobbly rings.
- **Wrong scale:** a single rock or building is a point; a whole country or range collapses to noise at 384 dots.
  Offer the characterful piece (one massif, one island, one caldera).
- **Bad data:** satellite DEM voids on sheer giants (Everest, K2, big walls) with no national survey to patch; polar
  regions. Warn and offer a neighbour with clean data (e.g. Ama Dablam is also voided — check first).

Say it plainly, e.g. "Amsterdam is flat — its beauty is its canals and streets, which this terrain style can't draw
well. The Netherlands has no relief worth a card. Want a mountain, island or dramatic coast instead?"
Then let the user choose.

Existing cards (re-render with `$SKILL/scripts/presets.sh NAME [out.png]`): `fuji`, `matterhorn`, `santorini`,
`kailash`, `pyramiden`, `ararat`, `halong`, `ilulissat`, `teide`, `damavand`, `kotor`, `moorea`, `cuillin`. Study a
preset before making a new card — it's the best reference for flag combinations.

## The chassis — never change

- 384 dots wide, aspect ~1.25 (map ~366 × ~458 dots), double-rule sheet frame, full-bleed map.
- Title lives in an **inset cartouche over the map** (white box, double rule). Never a header above the map.
- Cartouche stack, top to bottom: optional ornament band → **native-script name (the hero)** →
  optional second native script → letter-spaced English title (Futura Bold) → rule with centre dot →
  subtitle (`height · region, country`) → scale bar → `contours N m · lat lon`.
- Black-and-white only. No greys except via dots/lines (cards are 1-bit).

## The soul — different every card

Pick, for this place specifically:

1. **Hero typeface for the native name.** It must be the place's own script in a classical face.
   Check the font actually has the glyphs (see "Fonts" below). Tracking 0 for complex scripts
   (Tibetan, Devanagari, Arabic, Thai…) so they shape correctly; letter-space alphabets (Greek, Latin, Cyrillic).
2. **A local ornament or convention** in or around the cartouche. Done so far:
   - Fuji: kanji 富士山 in Songti (mincho-style serif), lake hatching.
   - Matterhorn: Helvetica (Swiss) + Swiss-cross emblem, dotted 1 km grid (Swiss national map), glacier names in
     spaced italics, relief stipple shading lit from NW (Swiss/Imhof), Hörnli route dashed on the ridge.
   - Santorini: ΣΑΝΤΟΡΙΝΗ in Didot (Greek printing tradition) between **Greek key friezes**, engraved
     **water-lining** for the sea, nautical **compass rose**, Greek place names, island names set in the water.
   - Kailash: Tibetan གངས་རིན་པོ་ཆེ in Kokonor (scriptural calligraphy) + Devanagari कैलाश पर्वत,
     **prayer flags** string (5 colours → 5 patterns), lakes named in Tibetan + English.
   - Pyramiden (Svalbard): ПИРАМИДА in PT Sans Narrow Bold (ParaType, Moscow) with crossed **miner's hammers**
     (`--emblem mining`, it was a coal town), Norwegian name as title, fjord with only 3 water-lining rings, glacier
     named in italics.
   - Ararat: Armenian Մասիս in Mshtakan flanked by a mirrored pair of **eternity signs** (`--emblem eternity`, as
     carved on khachkars), Little Ararat marked as a secondary summit.
   - Ha Long Bay: Vietnamese in Palatino + 下龍灣 in Songti, **Dong Son bronze-drum bands** (`--ornament dongson`),
     hatched sea so the karst islands stand out white.
   - Ilulissat: Baskerville + Greenlandic Kangerlua, **Greenland flag** emblem, chart-style **iceberg symbols**
     (`--ice`) over the ice-choked fjord.
   - Teide: El Teide in Ibarra Real Nova (Joaquín Ibarra's 1780 Madrid types) + the Guanche name Echeyde,
     **Canarian pintadera** stamp bands (`--ornament pintadera`), the volcano set above its caldera rim.
   - Damavand: دماوند in Nastaliq (the Persian calligraphic hand), **Persian girih** star bands (`--ornament girih`),
     200 m contours with heavy lines so the lone cone stands out of the Alborz.
   - Bay of Kotor: Бока которска in Monomakh (early Cyrillic, after the Crnojević press at Cetinje, 1494) under a
     **winged lion of St Mark** crest (`--ornament lion`, Kotor was Venetian), towns named in Cyrillic, hatched bay.
   - Moorea: Mo’orea in Didot (French Polynesia), **Tahitian tatau** shark-teeth bands (`--ornament tatau`; tatau
     is where "tattoo" comes from), water-lined island silhouette, compass rose, bay names in the sea.
   - The Cuillin: An Cuiltheann in Uncial Antiqua (insular uncial, as in the Iona manuscripts), **Celtic knotwork**
     bands (`--ornament knotwork`), 50 m contours left dark on purpose: these are the Black Cuillin.
   Don't repeat an ornament unless it is genuinely the local convention. If a new ornament is needed, add it to
   `$SKILL/scripts/realtopo.py` as another `--ornament` choice (see `meander()` / `prayer_flags()` for the pattern).
3. **Water style** to suit: `--water hatch` (lakes; Fuji/Kailash) or `--water lines` (seas/coasts; Santorini).
   In fjords/narrow seas framed by dense contours use `--water-rings 3`: deep water-lining looks like more contours
   and land/water stop reading apart. If even 3 rings read as contours (Kotor's narrow bay under limestone walls),
   hatch the water instead.
4. **North:** `--north arrow` default; `--north rose` for coastal/nautical places.

## Composition rules (learned the hard way)

1. **Frame the hero first, tight.** The headline feature must be big on the card. Kailash v1 at 72 km made the
   mountain a speck — redone at 38 km. Rough guide: a single peak 7–12 km wide sheet; volcano/island 16–30 km;
   peak + lakes ~40 km. Shift `--lat/--lon` so the hero sits in the upper or central part of the card.
2. **Then put the cartouche over the least interesting ground** — open sea, flat plain, glacier plateau — never
   over the hero, named places, or labels. Use `--corner` or, if no corner is empty, `--cartouche-at LAT,LON`.
   Variety of corner is only a tie-breaker: never move the cartouche just to vary it.
   So far: Fuji bl, Matterhorn br, Santorini tr, Kailash centred on the Barkha plain, Teide br over the south
   flank, Kotor tr over the karst plateau, Moorea centred in the open sea below the island, Cuillin bl over the sea.
3. **Every label coordinate must be verified against the DEM** (`check_points.py`). If a coordinate doesn't check
   out, fix it or drop the feature. Never draw a wrong route/place (the Kailash kora was dropped because the
   waypoints were 450–650 m off in elevation).
4. Small islands/features: put their names **in the water beside them**, not over dense contours.
5. Thin labels over dense contours disappear — use ≥10–11 px, demi/bold weights, halos (built in).
6. Keep the card light: if contours turn mountains into black masses, double the interval (e.g. 100→200 m).
7. **Carry the card in bold lines.** Single-dot lines in sparse areas look faint at card size (Pyramiden's glacier
   side, Kailash v1's lower edge), and `--shade` stipple is subtle. Don't rely on 1-dot detail or stipple to carry
   a card — the hero must read in bold lines (cliff bands, coastlines, major contours, solid water rims).
   Remedy (Pyramiden v2): `--minor-width 0.75 --major-width 1.6 --coast-width 1.5`, no `--shade`. Consider these
   heavier weights the default for sparse terrain (glaciers, plateaus, gentle slopes).

## Data

- `--source terrarium` (default): quick global tiles, fine for broad, smooth terrain (Fuji). Coarse in high mountains.
- `--source copernicus`: Copernicus GLO-30 (30 m), use for almost everything. Auto-finer grid on small sheets.
- `--source copernicus90`: GLO-90, for tiles GLO-30 doesn't publish (e.g. N39E044 around Ararat).
- Satellite DEMs have **voids on near-vertical faces** (smooth blobs; summits read low). Signs: summit far below the
  true height, smooth hillshade on a famous peak. Check with `--hillshade hs.png` (saves shaded relief of the data).
- Switzerland: `--swiss-patch KM` blends swisstopo swissALTI3D (2 m) — fixes the Matterhorn completely.
  Other national surveys could be added similarly if a card needs it.
- Only pass `--peak` when the true height is known for sure; `--peak 0` labels the measured DEM height at the
  marked summit (Pyramiden: 881 m measured vs an unverified remembered 935 m — don't draw unverified numbers).
- Pass the true summit height via `--peak` when known, and `--summit LAT,LON` when the map max isn't the hero.
  `--summit` searches 1 km around the point; narrow it with `--summit-radius KM` when a neighbour reads higher in
  the DEM (Cuillin: Sgùrr Dearg reads above Sgùrr Alasdair, which is the true high point).
  Secondary summits: `--label "summit|Name 7,694|lat|lon"` snaps to the local max within 3 km — so a subsidiary peak
  close to a higher one (Pico Viejo, 2 km from Teide) must use `peak` (no snapping) at its verified local maximum.
- Find coordinates from the DEM itself (local maxima for peaks; a distance transform of the water mask for the
  widest open water to put a bay name in) instead of guessing again.
- Coordinate pairs that start with a minus go with `=` (`--summit=-17.55,-149.82`, `--cartouche-at=-17.66,-149.8`):
  argparse reads a bare `-17.55,...` as a flag. Single numbers (`--lat -17.5`) are fine.
- Caches: `~/.cache/liltopomaps/tiles`, `~/.cache/liltopomaps/dem` (Copernicus tiles are ~40 MB each).

## Fonts

Verify glyph coverage before designing (fontTools `getBestCmap()`; off macOS, check the stand-in file the renderer
reports), and render a quick test strip for complex scripts — Pillow's raqm shaping handles them. Paths are relative
to `/System/Library/Fonts/`. Known-good:

| Script | Hero face (macOS) | Stand-in elsewhere | Notes |
|---|---|---|---|
| Latin titles, labels | `Supplemental/Futura.ttc` 0 Medium, 1 Medium Italic, 2 Bold | Jost | the default face of every card |
| Japanese/Chinese | `Supplemental/Songti.ttc` idx 2 (TC Bold) | Noto Serif TC Bold | mincho feel; Hiragino Mincho not installed |
| Tibetan | `Supplemental/Kokonor.ttf` (calligraphic), `Kailasa.ttc` idx 1 (clean, for labels) | Jomolhari; Noto Serif Tibetan Bold | tracking 0 |
| Devanagari | `Supplemental/DevanagariMT.ttc` idx 1 | Noto Serif Devanagari Bold | conjuncts shape fine; also `ITFDevanagari.ttc` (macOS only) |
| Greek | `Supplemental/Didot.ttc` idx 2 + `--local-bold 0.5` | GFS Didot | Didot hairlines vanish otherwise. Avenir Next (`Avenir Next.ttc`) for Greek labels: 2 Demi Bold, 3 Demi Bold Italic, 6 Medium Italic (stand-in: Noto Sans) |
| Latin (Swiss etc.) | `Helvetica.ttc` idx 1 | Nimbus Sans Bold | |
| Latin with diacritics (Vietnamese) | `Supplemental/Palatino.ttc` idx 2 | TeX Gyre Pagella Bold | Ha Long |
| Latin, classical (Greenlandic) | `Supplemental/Baskerville.ttc` idx 4 (hero), 5 (second line) | Libre Baskerville Bold / Italic | Ilulissat |
| Cyrillic | `Supplemental/PTSans.ttc` idx 2 (Narrow Bold), 7 (Bold), 1 (Italic for water/glacier labels) | PT Sans (the same family) | PT = ParaType, Moscow. Also in Futura Bold, Helvetica; `PTSerif.ttc`, Rockwell, Didot Bold, DIN Condensed (macOS only) |
| Armenian | `Supplemental/Mshtakan.ttc` idx 2; `SFArmenian.ttf` | Noto Serif Armenian Bold; Noto Sans Armenian | Ararat; SF Armenian untested |
| Georgian | `SFGeorgian.ttf` | Noto Serif Georgian | untested |
| Arabic | `Supplemental/Diwan Thuluth.ttf` (calligraphic) | Amiri | tracking 0; untested; also `Baghdad.ttc`, `GeezaPro.ttc` (macOS only) |
| Korean | `Supplemental/AppleMyungjo.ttf` | Noto Serif KR | untested |
| Ge'ez (Ethiopia) | `Supplemental/KefaIII.ttf` | Noto Serif Ethiopic | untested |
| Thai/Khmer/Lao/Myanmar/Sinhala | `* Sangam MN` / `* MN` families | none: pass an installed Noto Serif file | untested |

Open faces with no macOS counterpart, named by file name alone (e.g. `--local-font UncialAntiqua-Regular.ttf`) and
downloaded on every system:

| Use | File name | Notes |
|---|---|---|
| Spanish, classical | `IbarraRealNova-Bold.ttf`, `IbarraRealNova-Italic.ttf` | Ibarra's Real types (Madrid, 1780); Teide |
| Persian / Urdu calligraphic | `NotoNastaliqUrdu-Bold.ttf` | very tall line metrics: add `--local-dy` (about −0.9 × size); Damavand |
| Arabic-script labels | `NotoNaskhArabic-SemiBold.ttf` | covers Persian letters (پ چ ژ گ) |
| Early Cyrillic | `Monomakh-Regular.ttf` | after early printed Church Slavonic; Kotor |
| Gaelic / insular | `UncialAntiqua-Regular.ttf` | insular uncial; Cuillin |

Faces marked macOS only, and any font in neither table, must be given as a file that exists on this machine.

Futura has no ū/ō macrons — write "Honshu". **Never use Snell Roundhand** or other frilly Latin scripts: they
fight the engraved survey-sheet style.

## Workflow

0. **Decide whether the place has beautiful terrain** (table above). If not — city, flat, featureless, bad data —
   decline before rendering anything, with the reason and a terrain alternative.
1. Research the place: true heights, native names (exact spelling in script), a local visual tradition.
2. `check_points.py` every coordinate you intend to label (expected elevation after the colon; lakes show std≈0):
   ```
   $PY $SKILL/scripts/check_points.py "Hörnlihütte=45.98236,7.67736:3260" "Summit=31.0675,81.3119"
   ```
3. First render with `--hillshade hs.png` to sanity-check the terrain and framing; look at both PNGs (Read them).
   Use the hillshade to *find* features whose coordinates you're unsure of (peaks: local maxima search on the DEM;
   glaciers: smooth, steadily sloping surfaces) instead of guessing coordinates again.
   ```
   $PY $SKILL/scripts/realtopo.py moorea.png --lat ... --lon ... --km ... --source copernicus --hillshade hs.png ...
   ```
4. Iterate: framing → cartouche spot → labels. After each render, Read the PNG and zoom dense areas
   (labels, ornament, summit tag) to check them dot by dot:
   ```
   $PY $SKILL/scripts/zoom.py moorea.png zoom.png 0,0,200,160 180,300,384,475
   ```
   Fix overlaps, clipped labels, unreadable text.
5. **Preview** (see below) — every card ends here.
6. Once the card is settled, add the final command as a new case in `$SKILL/scripts/presets.sh` so it can be
   re-rendered by name.

## Preview

```
$PY $SKILL/scripts/preview.py moorea.png                    # saves previews/moorea_preview.png and opens it
$PY $SKILL/scripts/preview.py moorea.png --no-open --scale 4
```

It saves `previews/<card>_preview.png` under the current directory (kept, so it can be found later) and opens it
in the default image viewer: a dot-exact 3× enlargement on a little paper mock-up. Read the preview and zoom-check
the card first, so obvious defects are never shown. Then give the user the path, briefly describe what's on the
card and any trade-offs, and invite feedback. On feedback, re-render and re-preview (same filename overwrites).

## realtopo.py flag reference

```
placement   --lat --lon --km --aspect
data        --source {terrarium,copernicus,copernicus90} --swiss-patch KM --hillshade PNG
contours    --interval M --major M
summit      --summit LAT,LON --summit-radius KM --peak M | --no-summit
cartouche   --local TEXT --local-font F --local-index I --local-size PX --local-tracking PX --local-bold PX --local-dy PX
            --local2 TEXT --local2-font F --local2-index I --local2-size PX
            --title TEXT --title-size PX --title-font F --title-index I --sub TEXT
            --corner {bl,br,tl,tr} | --cartouche-at LAT,LON
            --ornament {none,meander,prayerflags,dongson,tatau,knotwork,girih,pintadera,lion}
            --emblem {none,swiss,mining,eternity,greenland}
lines       --minor-width PT --major-width PT --coast-width PT   (defaults 0.45 / 1.35 / 1.0)
map extras  --water {hatch,lines} --water-rings N --north {arrow,rose,none} --north-corner C --grid KM --shade
            --ice "LAT0,LON0,LAT1,LON1[,SPACING[,FADE]]"   (iceberg symbols over water in the box; repeatable)
labels      --label "KIND|TEXT|LAT|LON[|font=PATH:INDEX:SIZE]"
            KIND: place (dot+text right), text (centred, halo), italic/glacier (spaced italic),
                  hut (hut symbol), peak (triangle), summit (snap to local max, label below)
            "place||lat|lon" + a separate "text" label = dot on land, name placed in the water
routes      --route "LAT,LON;LAT,LON" --route-snap {ridge,none} --route-style {dash,dot}
```
