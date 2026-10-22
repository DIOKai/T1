# Data sources and licences

All pages read on 2026-10-22. **未验证** marks inference, rules of thumb, or details the page did not state. This is not legal advice.

## OpenStreetMap data (ODbL 1.0)

| Duty | What it means for a game | Source |
|---|---|---|
| Attribution | Name "OpenStreetMap" and say the data is ODbL; "© OpenStreetMap contributors" linked to openstreetmap.org/copyright is fine. For games: splash screen, in the game view, during play, credits or menu are all acceptable, but detailed licence info must be findable. On interactive maps put it in a corner; it may fade after interaction or 5 s if an "(i)"/About keeps it reachable. | https://osmfoundation.org/wiki/Licence/Attribution_Guidelines |
| Produced Work | Output not intended for extracting the original data (rendered images, a game's map view) is a Produced Work and can be under your own terms. Games are not listed as an example → "the game view is a Produced Work" is inference (未验证). | https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline |
| Derivative database | Data you adapt, modify, correct or extend (your cleaned building extract, corrected heights) is a derivative database. When a Produced Work made from it is publicly used, the derivative database must be offered under ODbL (on request). Practical approach: keep the processed OSM extract + scripts publishable. | same + https://osmfoundation.org/wiki/Licence/Licence_and_Legal_FAQ |
| Share-alike scope | Judged per Feature Type. A type whose data is **entirely** non-OSM (e.g. your game factories) does not trigger share-alike; mixing OSM and non-OSM data of the **same** type, or "filling gaps" by comparison with OSM, does. | https://osmfoundation.org/wiki/Licence/Community_Guidelines/Horizontal_Map_Layers_-_Guideline |
| Your code | ODbL covers data, not software; the FAQ does not require game code to be opened (未验证 inference). | FAQ above |

## Getting OSM data

| Service | Policy | Use in a game | Source |
|---|---|---|---|
| Overpass API (overpass-api.de) | Light use: < 10,000 queries/day, < 1 GB/day, < 10 min processing/day — **shared by all users of an app**; regular use ÷100. Identify with User-Agent/Referer; no parallel scripts; cache; on 429/406 wait 30 s; **commercial → own or paid server**. Default timeout 180 s. | Build time only, small bboxes. Never from the client. | https://wiki.openstreetmap.org/wiki/Overpass_API |
| Other Overpass instances | private.coffee (no rate limit, notify for big projects), VK Maps, overpass.ch (free 10k req/month, 30/min), Geofabrik/Tracestrack (paid). | Same rules apply. | same |
| `.osm.pbf` regional extracts (e.g. Geofabrik downloads) | Whole countries/continents as files; process locally (osmium, tilemaker, planetiler). Download-site terms not checked (未验证). | Best for country/Europe scale. | — |
| Nominatim geocoding | Max 1 request/s for the whole app, custom User-Agent, cache, **no autocomplete**, no systematic queries. | Don't put a city-search box on the public Nominatim; self-host or precompute. | https://operations.osmfoundation.org/policies/nominatim/ |
| tile.openstreetmap.org raster tiles | HTTPS, real User-Agent/Referer, visible attribution, honour cache (≥ 7 days); **no bulk download, prefetch, offline, headless bots**; no SLA; heavy use is blocked. | **Not** for a game basemap. | https://operations.osmfoundation.org/policies/tiles/ |

## Vector tiles

| Option | Cost / limits | Licence & attribution | Source |
|---|---|---|---|
| **Protomaps PMTiles, self-hosted** (recommended for production) | Free. Daily planet builds ≈ 120 GB (z0–15); cut a region with `pmtiles extract … --maxzoom N` (each zoom ≈ doubles size). Don't hotlink build URLs — copy to your storage. Serve as one static file with HTTP Range. | Data ODbL (OSM attribution). `pmtiles` 4.5.0 and `@protomaps/basemaps` 5.7.2 are BSD-3-Clause. Buildings layer `buildings` with `height`, `min_height`; individual buildings from z15. | https://docs.protomaps.com/basemaps/downloads ; https://docs.protomaps.com/basemaps/layers |
| **OpenFreeMap** (recommended for prototypes) | Free, no key, no registration, no view limits, commercial use allowed; donation-funded, no SLA stated (未验证). Offline downloads ≤ 3000 tiles / 50 MB, ≤ 4 parallel. | MIT software; attribution "OpenFreeMap © OpenMapTiles Data from OpenStreetMap". Styles `https://tiles.openfreemap.org/styles/liberty` (also `bright`, `positron`); source `https://tiles.openfreemap.org/planet`, OpenMapTiles schema, `building` layer with `render_height`/`render_min_height`. | https://openfreemap.org/ ; https://openfreemap.org/quick_start/ |
| MapTiler Cloud Free (**treat as 付费 for a commercial game**) | 5,000 map sessions/month, 100,000 API requests, 2,000 3D sessions; pauses until next month when exceeded; MapTiler logo shown; page targets testing/personal/non-commercial use. | — | https://www.maptiler.com/cloud/pricing/ |

## Regions (admin boundaries)

- **OSM** `boundary=administrative` relations: `admin_level=2` is the country; lower levels differ per country. Germany 4 state / 6 district / 8 municipality; France 4 région / 6 département / 8 commune; Italy 4 regione / 6 provincia / 8 comune. Check the country table before choosing a level. https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative (Poland/UK/Spain rows not read, 未验证.)
- **Natural Earth** admin-0/admin-1: **public domain**, commercial use, no attribution needed ("Made with Natural Earth" optional). Coarser, good for the continent view and simple game regions. https://www.naturalearthdata.com/about/terms-of-use/ . Disputed borders are a design decision (the page doesn't address them).

## Terrain (DEM)

| Source | Notes | Source URL |
|---|---|---|
| Copernicus DEM GLO-30 / GLO-90 | Free licence worldwide, ~30 m / ~90 m; public can download (Copernicus Data Space account). Modified products must say "produced using Copernicus WorldDEM-30" + DLR/Airbus copyright lines. Full ESA licence not read (未验证). | https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM |
| Terrarium tiles (AWS Terrain Tiles / Tilezen) | Decode `h = (R*256 + G + B/256) - 32768`. S3 `elevation-tiles-prod` (+ EU copy `elevation-tiles-prod-eu`), no account. Attribution per source, e.g. EU-DEM line. URL template `…/terrarium/{z}/{x}/{y}.png` 未验证. | https://github.com/tilezen/joerd/blob/master/docs/formats.md ; https://registry.opendata.aws/terrain-tiles/ ; https://github.com/tilezen/joerd/blob/master/docs/attribution.md |
| Mapterhorn | Terrarium-encoded 512 px WebP, TileJSON `https://tiles.mapterhorn.com/tilejson.json`; downloadable `planet.pmtiles` (z0–12) + z13+ areas for self-hosting; code BSD-3. Usage limits and data licence not stated on the pages read → read https://mapterhorn.com/attribution before shipping (未验证). | https://mapterhorn.com/data-access/ |

## Paid / limited 3D services (付费 — ask before using)

- **Google Photorealistic 3D Tiles**: 1,000 free events/month, then from USD 6.00 per 1,000. Policies forbid pre-fetching, storing, caching (limited exceptions), extracting geometry, offline use; single-line attribution at the bottom. You can't turn them into game assets. https://developers.google.com/maps/billing-and-pricing/pricing ; https://developers.google.com/maps/documentation/tile/policies
- **Cesium ion Community**: 10 GB storage, 15 GB/month streaming, personal/non-commercial; paid once revenue or funding > USD 50K, government work, or over quota. https://cesium.com/platform/cesium-ion/pricing/

## Attribution block to ship (adapt to the stack actually used)

```
© OpenStreetMap contributors (ODbL) — openstreetmap.org/copyright
OpenFreeMap © OpenMapTiles                       ← only if using OpenFreeMap
Terrain: Mapterhorn / Copernicus WorldDEM-30 …   ← per terrain source's own wording
Natural Earth (public domain)                    ← optional
```
