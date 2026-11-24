# liltopomaps

Little "playing card" terrain maps of real places, made by a [Claude Code](https://claude.com/claude-code) skill.

Each card is 384 dots wide and 1-bit: a contour map drawn from open elevation data, framed like an old survey
sheet, with an inset cartouche carrying the place's name in its own script and a local ornament: Greek key friezes
for Santorini, prayer flags for Kailash, a Swiss cross and km grid for the Matterhorn.

## The `liltopcard` skill

`.claude/skills/liltopcard/` makes a new card end to end: it judges whether a place has terrain worth a card,
verifies coordinates against the elevation data, picks a local typeface and ornament, places the cartouche over the
least interesting ground, self-checks the render, and opens a preview:

```
/liltopcard moorea
/liltopcard stromboli
```

It is deliberately terrain-only. Cities and flat places get politely turned down, with the reason and a terrain
alternative.

To use it in another project, copy the `.claude/skills/liltopcard/` folder into that project's `.claude/skills/`
or into `~/.claude/skills/`.

## Setup (macOS)

```sh
python3 -m venv .venv
.venv/bin/pip install -r .claude/skills/liltopcard/requirements.txt
```

Fonts are taken from the macOS system font library (`/System/Library/Fonts`).

## Rendering without Claude

The renderer and its helpers live in `.claude/skills/liltopcard/scripts/`:

```sh
S=.claude/skills/liltopcard/scripts
$S/presets.sh santorini santorini.png               # re-render a saved card
.venv/bin/python $S/preview.py santorini.png        # previews/santorini_preview.png, opened in your viewer
.venv/bin/python $S/realtopo.py --help              # every option
```

Presets: `fuji`, `matterhorn`, `santorini`, `kailash`, `pyramiden`, `ararat`, `halong`, `ilulissat`.

- `realtopo.py`: the card renderer (placement, contour intervals, cartouche text/fonts/ornaments, water styles,
  labels, routes, data source).
- `check_points.py`: checks label coordinates against the elevation data before they go on a card.
- `zoom.py`: dot-level enlargement of parts of a card.
- `preview.py`: dot-exact enlargement on a paper mock-up.

## Data and attribution

- [Copernicus DEM GLO-30 / GLO-90](https://registry.opendata.aws/copernicus-dem/): © DLR e.V. 2010–2014 and
  © Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the European Union and ESA.
- [Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) (Mapzen / AWS Open Data).
- [swissALTI3D](https://www.swisstopo.admin.ch/en/height-model-swissalti3d), © swisstopo, used to patch
  satellite voids on Swiss peaks.

Downloads are cached under `~/.cache/liltopomaps`.
