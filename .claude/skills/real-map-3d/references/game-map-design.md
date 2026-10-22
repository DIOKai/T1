# Designing a game on a real map

For games like "Capital Rift": real Europe split into regions, zoom to real city blocks, build factories, process resources, rent buildings to other players. Numbers below are design starting points (未验证 rules of thumb) unless a source is given. Economy maths (rent levels, production rates, price curves, sinks/faucets) → `game-balance-economy`; core loop, multiplayer interaction → `game-design-core`. Ask before using either.

## 1. Regions

- **Simple and stable**: Natural Earth admin-1 (public domain, no attribution needed). Few hundred polygons for Europe; good for the continent view and region ownership.
- **Realistic**: OSM `admin_level` per country (DE 4/6, FR 4/6, IT 4/6 …). Levels mean different things in different countries, so pick per country and store your own mapping table. Borders change and get edited — freeze a snapshot.
- **Balanced**: real regions differ wildly in size and population. Either accept it (prestige regions) or overlay a game grid (H3-style hexes or tile squares) for fairness. Decide with `game-design-core`.
- Simplify boundaries for the overview (Douglas-Peucker to a few hundred metres) and keep full detail only when zoomed in.

## 2. Buildings as game objects

- **Snapshot, don't live-link.** OSM ids change (ways get split, deleted, re-drawn). Import a dated extract, give every building your own stable `building_id`, keep `osm_id` + snapshot date as provenance, and store the footprint geometry you used.
- Gameplay values from data: `footprint_m2` (plot), `floor_area_m2` (= footprint × levels; rentable space), `building` tag (residential/industrial/commercial → which uses are allowed), `height_source` (show "estimated" in UI when not `height`).
- Mining & industry hints from OSM `landuse=quarry|industrial|farmland`, `man_made=works`, `power=plant` — query with `overpass_query.py --what landuse`. Actual resource amounts should be game-designed (seeded per region), not presented as real geology.
- Updating to a newer OSM snapshot: diff by geometry overlap, migrate player ownership to the best-matching new building, and give players a fallback (refund) when a building vanished in reality.

## 3. Coordinates the server and client agree on

- Store **lon/lat (WGS84, 7 decimals ≈ 1 cm)** as truth; derive local metres per chunk (`osm_to_geojson.py --local` uses exact ENU).
- Distances for trucks/logistics: geodesic (haversine is fine for gameplay) or road network distance from OSM `highway` ways — never Mercator units.
- Chunk key = slippy tile `z/x/y` at z14 (or similar) so map tiles, game state and three.js chunks line up.

## 4. Multiplayer & server authority

- Ownership, rent, production, trade: server-decided and server-timed; the client only renders. Same principle as T1's FiveM rule (economy rewards are always server-side).
- Rent between players: contracts are records `{building_id, landlord, tenant, price, period}`; settle on the server tick; rate-limit actions.

## 5. Keeping player data out of share-alike (未验证, ask a lawyer)

Per the OSMF Horizontal Map Layers guideline, share-alike is judged per Feature Type:
- Factories, warehouses, ownership, rents, resources are **your own feature types** with no OSM data of the same type → they can stay proprietary.
- Your cleaned/corrected **building table** is derived from OSM → treat it as an ODbL derivative database: be ready to publish it (or the extract + scripts) on request.
- Do **not** let players "fix" building heights/outlines into your building table and then claim it is not OSM-derived; consider pointing players to edit OSM itself instead.
- Keep the two in separate tables joined by `building_id`.

## 6. Attribution in the game UI

- Map view corner: "© OpenStreetMap contributors" (link to openstreetmap.org/copyright) + tile/terrain provider lines. MapLibre's AttributionControl does this when sources declare `attribution`.
- Credits/About screen: full list with licences (ODbL, Copernicus wording, Natural Earth optional).
- Splash or loading screen is allowed for games, but keep the in-map corner credit too (OSMF guidance allows fading only if it stays reachable).
- Source: https://osmfoundation.org/wiki/Licence/Attribution_Guidelines

## 7. Performance budget (starting points, 未验证)

| Layer | Budget | How |
|---|---|---|
| Continent | < 5 MB GeoJSON or vector tiles | simplified regions, no buildings |
| City overview | vector tiles only | fill-extrusion, no three.js |
| Active block | ≤ 300k triangles, ≤ 50 draw calls | merged chunk meshes + InstancedMesh props |
| Mobile | half of the above, no shadows by default | `threejs-performance`, `threejs-compatibility-fallbacks` |

Never ship a client that calls Overpass, Nominatim or tile.openstreetmap.org; serve everything from your own static storage/CDN.
