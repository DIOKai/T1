# site-plan.json schema (`site-plan/1`)

One file, read by every agent, written only by the lead. `scripts/check_site_plan.py` enforces the rules marked **(checked)**. Full example: `assets/example-site-plan.json`.

## Coordinates (decide once, never per agent)
- Units: metres (`"units": "m"`, **checked**).
- Plan points are `[x, z]`: x east, z south, y up — the three.js convention, so plan values go straight into `position.set(x, y, z)`. North is −z (top of the SVG).
- Blender: `bx = x`, `by = -z`, `bz = y` (Blender is Z-up). Write the mapping into the plan's `axes` string so no agent guesses.
- Origin: the site centre unless there is a reason (a survey grid, a real coordinate). Ground level `site.ground_y` (default 0).
- Rotations: `rotation_deg` about the vertical axis, counter-clockwise seen from above in plan coordinates. State it in `axes` if you use anything else.

## Top level
| key | type | meaning |
|---|---|---|
| `schema` | `"site-plan/1"` | version |
| `name` | string | shown on the SVG |
| `units` | `"m"` | **checked** |
| `axes` | string | the coordinate convention, in words |
| `site` | object | `bounds [xmin, zmin, xmax, zmax]` (**checked**), `ground_y`, `grid` (m, > 0, **checked**; off-grid centres get a WARN), `north`, `notes` |
| `style` | object | era, palette (hex), rules — the hidden decisions every agent must share (Cognition's "actions carry implicit decisions") |
| `shared_files` | list | `{path, owner: "lead", note}` — read-only for zone agents; **checked** that no zone also owns them |
| `zones` | list | see below |
| `water` | list | see below |
| `paths` | list | see below |
| `interfaces` | list | see below |
| `elements` | list | see below |
| `shots` | list | optional, see `shot-plan.md` |

## zones
```json
{"id": "pond", "owner": "agent-pond", "bbox": [-40, -10, -4, 10],
 "files": ["src/zones/pond.js"], "description": "Pond, red arched bridge, lantern on a rock"}
```
- `bbox` axis-aligned `[xmin, zmin, xmax, zmax]`, inside the site (**checked**). Zones may touch but not overlap (> 0.05 m², **checked**). Uncovered ground gets a WARN — fine if it stays empty.
- `owner` required (**checked**). One agent may own several zones; a zone has exactly one owner.
- `files` — the only files that agent may create or edit. A file listed under two different owners is an ERROR (**checked**): two agents writing one file overwrite each other (Claude Code agent-teams docs).
- Cut zones along natural seams (a path, a wall, the pond edge), not through a building. A thing that crosses a seam (a long path, a wall) is split into one piece per zone plus an interface point.

## elements
```json
{"id": "pagoda", "zone": "pagoda", "type": "pagoda", "landmark": true,
 "footprint": {"rect": {"center": [22, 0], "size": [6.4, 6.4], "rotation_deg": 0}},
 "height": 31.3, "anchor": "on:pagoda_kidan", "base_y": 1.2,
 "clearance": 1.5, "allow_overlap": [], "proportions": {...}, "notes": "..."}
```
- `id` unique (**checked**). `zone` must exist and the whole footprint must lie in its bbox (**checked**) and in the site (**checked**).
- `footprint`: one of `rect {center, size [w, d], rotation_deg}`, `circle {center, radius}`, `polygon [[x, z], ...]` (≥ 3 points, non-zero area, **checked**). For a building it is the outer line of walls/pillars at the base; eaves overhang is part of the building's own job and must stay inside its zone.
- `height` > 0 from `base_y` to the highest point incl. finial (**checked**).
- `anchor` (**checked**):
  - `ground` — `base_y` must equal `site.ground_y`. Standing in water is an ERROR unless `over_water: true`.
  - `on:<id>` — sits on another element: `base_y` must equal support `base_y + height` (± 0.02 m) and the footprint must lie within the support's footprint (no overhang without support). Support must exist; loops are errors. Different-zone support gives a WARN (one agent should own both).
  - `water_bed` — footprint fully inside a water body, `base_y` = `surface_y − depth` (stepping stones, a rock carrying a lantern).
  - `terrain` — sampled from a height field the checker can't see (WARN); the zone agent must sample it.
- `over_water: true` — bridges. At least two footprint corners must be on land (abutments on both banks, **checked**).
- `passable: true` — gates and arches a path goes through (silences the path WARN).
- `clearance` (m) — WARN when another element is closer.
- `allow_overlap: [ids]` — deliberate overlaps (a fence through a hedge). Use rarely; stacking (`on:`) is usually the right answer.
- `type` — free text for agents and the SVG (`ground_cover` is drawn faint and doesn't block paths; `tree` is skipped by the camera check because canopies are see-through enough).
- `proportions`, `notes`, `refs` — free; this is where the cited numbers and the reference-photo paths go.

## water
```json
{"id": "pond_water", "zone": "pond", "surface_y": -0.3, "depth": 0.8,
 "polygon": [[-34, -6], [-20, -8], [-8, -5], [-7, 4], [-18, 7], [-32, 5]]}
```
Inside its zone (**checked**), `depth` > 0 (**checked**), `surface_y` not above ground (**checked**), water bodies don't overlap (**checked**).

## paths
```json
{"id": "path_axis", "zone": "axis", "width": 3, "material": "stone slabs", "polyline": [[0, 10], [0, -10]]}
```
Inside its zone (**checked**), `width` > 0 (**checked**). Running into water without an `over_water` element covering that spot is an ERROR; running into a non-passable element is a WARN.

## interfaces
```json
{"id": "if_pond_axis", "between": ["pond", "axis"], "point": [-4, 0],
 "note": "1.6 m gravel path from the bridge joins the axis path at its west edge"}
```
The point must lie on the edge of both zones (**checked**). The note says what meets there (width, level, material) — both agents build to it.

## No-overlap rules in one place
1. Zones don't overlap; each square metre has one owner.
2. Elements don't overlap in plan **and** height unless stacked (`on:`) or listed in `allow_overlap`.
3. Nothing stands in water except bridges (with two banks) and water-bed items.
4. Everything is grounded: on the ground, on a support, on the water bed or on terrain. Nothing floats, nothing sinks, nothing overhangs its support.
5. Each file has one owner.

## Example: cited Japanese temple numbers (use as starting points)
| item | number / rule | source |
|---|---|---|
| Hōryūji five-storey pagoda plan | 3×3 bays, 6.42 m square; top (5th) storey 2×2 bays; mokoshi 10.85 m square | JAANUS "tō" https://projects.mcah.columbia.edu/jaanus/node/575 |
| Other pagodas | Haguro 3×3 bays 5.02 m, "each story slightly smaller"; Murōji only 2.44 m | same |
| Hōryūji pagoda height | ≈ 32.45 m incl. finial (another engineering paper: 32.55 m) | https://en.wikipedia.org/wiki/Japanese_pagoda, Structurae |
| Roof diminution | 10:9:8:7:6 bottom to top — **unverified** (secondary caption) | MLIT tagengo-db (search summary) |
| Upper tiers | Only the ground storey is a usable room; the upper four are bracket complexes and eaves | MLIT tagengo-db 001545932 |
| Sōrin (finial), bottom→top | roban, fukubachi, 9 rings (kurin), suien, ryūsha, hōju | JAANUS https://projects.mcah.columbia.edu/jaanus/record/sorin |
| Bracket set (kumimono = tokyō) | bracket arms (hijiki) + large bearing block (daito) + small blocks (makito) on the pillar; brackets get smaller tier by tier | JAANUS sonae/tokyō; JAABE 2024 (abstract) |
| Myōjin torii | 2 inward-leaning pillars; kasagi with up-turned ends over shimaki; nuki about one pillar diameter lower, projecting ~1/5 of its length past the pillars, wedged; central strut/plaque; stone bases | JAANUS torii / myōjin torii |
| Taikobashi | arched bridge of stone or wood (also called soribashi) | JAANUS https://projects.mcah.columbia.edu/jaanus/record/taikobashi |
| Karesansui | stones, sand/gravel, few plants; raked patterns stand for water; viewed from one seated point; Zen temples | JAANUS karesansui |

Torii belong mainly to shrines; ask before putting one in a "temple". Stone-lantern proportions weren't found in a reliable source — take them from the user's reference photos.
