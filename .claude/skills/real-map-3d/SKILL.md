---
name: real-map-3d
description: Build browser 3D maps and map-based strategy or tycoon games from REAL, free map data — OpenStreetMap buildings and land use, regions from OSM admin_level or public-domain Natural Earth, free terrain (Copernicus DEM, Terrarium) — rendered with MapLibre GL JS fill-extrusion and terrain or three.js in a MapLibre custom layer, zooming from a continent down to real city blocks. Covers ODbL attribution and share-alike for a game, Overpass and OSM tile policies, free vector tiles (self-hosted Protomaps PMTiles, OpenFreeMap), building heights, lon/lat to local metres, tiling and LOD, plus an offline Overpass-JSON to GeoJSON converter. Use whenever the user wants a real city or country in 3D in the browser, a game on a real map of Europe, OSM buildings in three.js, ownable map regions, or asks which map data is free — even if they only say "真实地图3D", "OSM建筑", "网页地图游戏", "把城市做成3D", "地图经营游戏", "真实城市建模", "欧洲地图分区", "放大到街区", "地图数据免费吗".
---

# Real map → 3D in the browser

The repo's 40 `threejs-*` skills generate fictional cities. This skill is for **real places**: the data is free, but it comes with licence duties and usage policies that can get a game blocked or put in breach if ignored. Most of the work is choosing the right free source for each zoom level, converting it once at build time, and keeping attribution on screen. The rendering itself is ordinary MapLibre or three.js.

Before using it, follow T1 rules: say which skill you are using and what it does (reads files, prints queries, writes GeoJSON; only touches the network with `--fetch` after the user agrees). Paid services (Google Photorealistic 3D Tiles, Cesium ion commercial, MapTiler beyond free) are documented as 付费 — never use them without asking.

## Workflow

### 1. Pin down the map game (ask in one go)
Which area (one city, a country, all of Europe), the smallest unit a player interacts with (region, district, city block, single building), 2D map with 3D city view or full 3D throughout, expected players and whether it is commercial (decides hosting and which "free" tiers are allowed), and the tech already in the project (plain MapLibre, three.js, React). Gameplay economy (rent, production, prices) → offer `game-balance-economy` and `game-design-core`; ask before using them.

### 2. Pick data sources per zoom level
Read `references/data-sources-and-licences.md`. Default free stack:
- Continent and regions: Natural Earth admin-1 (public domain) or OSM `boundary=administrative` at a chosen `admin_level` (ODbL).
- Base map: OpenFreeMap styles for prototypes; self-hosted Protomaps PMTiles extract for production. **Never** `tile.openstreetmap.org` as a game basemap.
- City blocks and buildings: the vector tiles' `building` layer, or your own extract from Overpass / `.osm.pbf` converted with `scripts/osm_to_geojson.py`.
- Terrain: Mapterhorn or AWS Terrarium tiles; Copernicus GLO-30 for your own processing.
Tell the user which attribution lines each choice adds.

### 3. Get the data politely (build time, never from the game client)
```bash
python scripts/overpass_query.py --center 52.5163,13.3777 --radius 400      # prints QL + curl, no network
python scripts/overpass_query.py ... --fetch --user-agent "Game-dev/0.1 (mail@...)" --save area.json   # only after the user agreed
python scripts/osm_to_geojson.py area.json --out buildings.geojson --local buildings_local.json --origin auto
```
`overpass_query.py` refuses boxes over 4 km² (split them or use a `.osm.pbf` extract). `osm_to_geojson.py` (offline, stdlib) reads both `out geom` and node-reference output, joins multipolygon rings with courtyards, orients rings for RFC 7946, takes `height` → `building:levels` × 3 m (+ roof) → default 9 m, and writes `footprint_m2` and `floor_area_m2` for gameplay. It reports how many heights are guesses — pass that on to the user.

### 4. Render
- **MapLibre only** (fastest path, millions of buildings): `fill-extrusion` from vector tiles + `raster-dem` terrain. See `references/maplibre-3d.md`.
- **three.js for the interactive city block** (factories, construction animation, picking): a MapLibre custom layer or `maplibre-gl-three`, meshes built from the local-metre GeoJSON. See `references/threejs-from-osm.md`. General three.js work → the repo's `threejs-geometry`, `threejs-performance`, `threejs-interaction`, `threejs-procedural-buildings-and-cities` (facade detail on OSM boxes); ask first.

### 5. Design the map game layer
Read `references/game-map-design.md`: regions from admin boundaries, building IDs and snapshots, local coordinates per city chunk, server authority, what player data stays outside ODbL share-alike, and where the attribution goes in the game UI.

### 6. Verify
- Attribution visible on every map view ("© OpenStreetMap contributors" plus tile/terrain provider lines) and in credits.
- Spot-check 5 buildings against reality: footprint, height source, courtyard holes.
- Area numbers: compare `footprint_m2` of a known building with a reference (cadastre, Wikipedia). Lon/lat degrees are never used as metres.
- Network tab: no requests to `tile.openstreetmap.org`, Overpass or Nominatim from the client.
- Frame rate at the densest zoom on a mid-range laptop and a phone (`threejs-performance` for method).

## Limits (say them, don't hide them)
- OSM coverage is uneven: many buildings have no height tag, so heights are estimates; roof shapes are not built by the script (flat extrusions only). Simple 3D Buildings roofs need extra work.
- Licence notes summarise official OSMF guidance read on 2026-10-22; they are not legal advice. Whether specific player data counts as a derivative database is a judgement for a lawyer — the skill marks those spots 未验证.
- `osm_to_geojson.py` and `overpass_query.py` were tested offline with hand-made Overpass JSON (16 unit tests). The `--fetch` path was not run against the live Overpass server. The MapLibre / three.js snippets were written from the official examples and docs but not run in a browser while writing this skill.
- Paid or limited services (Google Photorealistic 3D Tiles, Cesium ion, MapTiler Cloud commercial use) are documented only; ask before using any of them.
- Self-hosting a Europe-wide PMTiles extract means tens of GB of storage and a CDN with HTTP Range support; exact size depends on the max zoom (not measured here).

## References
- `references/data-sources-and-licences.md` — every source, licence, usage limit, attribution line, with URLs.
- `references/maplibre-3d.md` — MapLibre 3D buildings, terrain, PMTiles, custom layers, deck.gl.
- `references/threejs-from-osm.md` — local-metre GeoJSON to merged three.js meshes, picking, chunk origins, LOD.
- `references/game-map-design.md` — regions, parcels, IDs, coordinates, ODbL-safe data split, attribution in game UI, performance budget.
- Research notes: `docs/skill-batches/archviz-batch2-2026-10-22-research/real-map-3d.md` in the T1 repo.
