# liltopomaps

Little "playing card" terrain maps of real places, made by a [Claude Code](https://claude.com/claude-code) skill.

Each card is 384 dots wide and 1-bit: a contour map drawn from open elevation data, framed like an old survey
sheet, with an inset cartouche carrying the place's name in its own script and a local ornament: Greek key friezes
for Santorini, prayer flags for Kailash, a Swiss cross and km grid for the Matterhorn.

<table>
  <tr>
    <td align="center" width="33%"><img src="examples/santorini.png" width="260" alt="Santorini map card"><br>
      <sub><b>Santorini</b>: the caldera rim, Greek key friezes, engraved water-lining</sub></td>
    <td align="center" width="33%"><img src="examples/fuji.png" width="260" alt="Mount Fuji map card"><br>
      <sub><b>Mount Fuji</b>: 富士山 in a mincho serif, the near-perfect cone</sub></td>
    <td align="center" width="33%"><img src="examples/kailash.png" width="260" alt="Mount Kailash map card"><br>
      <sub><b>Mount Kailash</b>: Tibetan and Devanagari names, prayer flags, the sacred lakes</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="examples/matterhorn.png" width="260" alt="Matterhorn map card"><br>
      <sub><b>Matterhorn</b>: swisstopo survey data, Swiss cross, km grid, the Hörnli route</sub></td>
    <td align="center"><img src="examples/halong.png" width="260" alt="Ha Long Bay map card"><br>
      <sub><b>Ha Long Bay</b>: white karst islands on a hatched sea, Dong Son drum bands</sub></td>
    <td align="center"><img src="examples/ilulissat.png" width="260" alt="Ilulissat Icefjord map card"><br>
      <sub><b>Ilulissat Icefjord</b>: iceberg symbols fanning out of the fjord, Greenland flag</sub></td>
  </tr>
</table>

## The `liltopomaps` skill

`.claude/skills/liltopomaps/` makes a new card end to end: it judges whether a place has terrain worth a card,
verifies coordinates against the elevation data, picks a local typeface and ornament, places the cartouche over the
least interesting ground, self-checks the render, and opens a preview:

```
/liltopomaps moorea
/liltopomaps stromboli
```

It is deliberately terrain-only. Cities and flat places get politely turned down, with the reason and a terrain
alternative.

To use it in another project, copy the `.claude/skills/liltopomaps/` folder into that project's `.claude/skills/`
or into `~/.claude/skills/`.

## Setup (macOS)

```sh
python3 -m venv .venv
.venv/bin/pip install -r .claude/skills/liltopomaps/requirements.txt
```

Fonts are taken from the macOS system font library (`/System/Library/Fonts`).

## Rendering without Claude

The renderer and its helpers live in `.claude/skills/liltopomaps/scripts/`:

```sh
S=.claude/skills/liltopomaps/scripts
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
