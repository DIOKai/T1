# three.js from OSM footprints

Input: the `--local` output of `scripts/osm_to_geojson.py` — features with rings in **metres** (`x` east, `y` north) around `origin {lat, lon}`, plus `height`, `min_height`, `height_source`, `footprint_m2`, `floor_area_m2`, `osm_id`. three 0.186.1 (MIT) is current on npm (2026-10-22). General three.js practice lives in the repo's `threejs-*` skills; this file only covers what is specific to real map data.

## Why local metres, not degrees or Web Mercator

- Degrees are not lengths: 0.001° of longitude is ~68 m at 52.5°N but ~111 m at the equator.
- Web Mercator inflates lengths by 1/cos(lat) — about ×1.6 at 50°N, ×2 at 60°N — so areas, rents and truck distances computed in Mercator units are wrong. MapLibre's `meterInMercatorCoordinateUnits()` exists exactly to undo this per location.
- The script uses exact WGS84 → ECEF → ENU (East-North-Up) at the origin; on a city-sized chunk this is metre-accurate (tested against the meridian arc to 1 cm). Far from the origin the ground curves away (ENU is a tangent plane), so use one origin per city chunk, a few km across (rule of thumb, 未验证 threshold).
- three.js geometry is float32: keep vertex coordinates small (local metres around a nearby origin), never raw Mercator or ECEF metres.

## Footprint → extruded mesh

```js
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

function featureToGeometry(f) {
  const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
  const out = [];
  for (const poly of polys) {
    const ring = poly[0].slice(0, -1);                    // drop closing point
    const shape = new THREE.Shape(ring.map(([x, y]) => new THREE.Vector2(x, y)));
    for (const hole of poly.slice(1)) shape.holes.push(new THREE.Path(hole.slice(0, -1).map(([x, y]) => new THREE.Vector2(x, y))));
    const depth = Math.max(0.1, f.properties.height - f.properties.min_height);
    const g = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false });
    g.rotateX(-Math.PI / 2);                              // shape XY (east,north) -> XZ ground, extrude up +Y
    g.translate(0, f.properties.min_height, 0);           // now x=east, y=up, z=-north (south)
    out.push(g);
  }
  return out;
}
```
After `rotateX(-π/2)` a point (east, north) lands at (x=east, z=-north): three's default camera looks down −Z, so north is "into the screen". Keep one convention across client and server and document it.

Per chunk, merge everything into one geometry (one draw call) and keep a lookup from triangle range → `osm_id`:
```js
const geos = [], ranges = [];
let tri = 0;
for (const f of fc.features) for (const g of featureToGeometry(f)) {
  const n = (g.index ? g.index.count : g.attributes.position.count) / 3;
  ranges.push({ start: tri, end: tri + n, id: f.id }); tri += n; geos.push(g.toNonIndexed());
}
const merged = mergeGeometries(geos);   // all non-indexed so attributes match
const mesh = new THREE.Mesh(merged, new THREE.MeshStandardMaterial({ color: 0xcfc8bc }));
```
Picking: `raycaster.intersectObject(mesh)` → `hit.faceIndex` → binary-search `ranges` → building id. Ownership colours: a per-vertex `color` attribute you rewrite for that range (cheap) rather than one material per building.

## Instancing, LOD, chunks

- **Instancing** (`THREE.InstancedMesh`) for repeated game props on real sites: factory modules, trucks, trees, cranes — not for OSM buildings, which are all different.
- **Chunks**: split by slippy-map tile at z14 or z15 (one tile ≈ 1–2 km in Europe at z14). Load the chunk under the camera + neighbours, dispose the rest (`geometry.dispose()`, materials, textures). Each chunk has its own origin; position the chunk group by the offset between origins (or one custom layer per chunk).
- **LOD**: far → let MapLibre fill-extrusion draw; near → three.js mesh with roofs/facades. Facade detail on plain boxes → `threejs-procedural-buildings-and-cities` / `threejs-procedural-materials` (ask first).
- **Budget starting points (rule of thumb, 未验证)**: a dense European district of ~5,000 buildings extrudes to roughly 100k–300k triangles; one merged mesh per chunk keeps draw calls in the tens. Measure with the method in `threejs-performance`.

## Terrain under buildings

With MapLibre terrain on, query `map.queryTerrainElevation([lon, lat])` at each building centroid and lift the building base to it (OSM heights are above local ground). Pure three.js: decode Terrarium tiles (`h = R*256 + G + B/256 - 32768`) into a heightfield. Sloped sites: extend the base below ground by the slope difference so no building floats (same rule as elsewhere in T1: nothing floating).

## Placing your own glTF factories

Store each placed object as `{ chunk, x, y (metres east/north), heading_deg, model_id }` in game data, not as world matrices. With `maplibre-gl-three`, `getEcefMatrix({ point:[lon,lat], height })` places a group at a geographic point and children use metre offsets (east=+x, south=+z in that example).
