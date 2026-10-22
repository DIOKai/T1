# MapLibre GL JS for 3D maps

`maplibre-gl` 6.15.0, BSD-3-Clause (npm, 2026-10-22). Free, no key. Pin the exact version in the project.

## 3D buildings (fill-extrusion)

From the official example (uses OpenFreeMap): https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/

```js
const map = new maplibregl.Map({
  container: 'map',
  style: 'https://tiles.openfreemap.org/styles/bright',
  center: [13.3777, 52.5163], zoom: 15.5, pitch: 45, bearing: -17.6,
  canvasContextAttributes: { antialias: true },
});
map.on('load', () => {
  map.addSource('openfreemap', { type: 'vector', url: 'https://tiles.openfreemap.org/planet' });
  const labelLayer = map.getStyle().layers.find(l => l.type === 'symbol' && l.layout?.['text-field'])?.id;
  map.addLayer({
    id: '3d-buildings', source: 'openfreemap', 'source-layer': 'building',
    type: 'fill-extrusion', minzoom: 15,
    filter: ['!=', ['get', 'hide_3d'], true],
    paint: {
      'fill-extrusion-color': '#c9c3b8',
      'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 15, 0, 16, ['get', 'render_height']],
      'fill-extrusion-base':   ['interpolate', ['linear'], ['zoom'], 15, 0, 16, ['get', 'render_min_height']],
    },
  }, labelLayer);
});
```
- Property names depend on the tile schema: OpenMapTiles/OpenFreeMap use `render_height`/`render_min_height` in layer `building`; Protomaps uses `height`/`min_height` in layer `buildings`.
- Own data (output of `osm_to_geojson.py --out`): add a `geojson` source and use `['get','height']` / `['get','min_height']`. Fine for a district; for a whole country convert to vector tiles (tippecanoe/planetiler, not covered here) — a huge GeoJSON source is slow.
- Gameplay tinting: use `feature-state` (`map.setFeatureState({source, sourceLayer, id}, {owned: true})` + `['case', ['boolean', ['feature-state','owned'], false], '#e0a030', '#c9c3b8']`). Requires feature ids (`promoteId` for GeoJSON). Picking: `map.queryRenderedFeatures(e.point, {layers: ['3d-buildings']})`.

## Terrain

https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/

```js
sources: {
  terrainSource:   { type: 'raster-dem', url: 'https://tiles.mapterhorn.com/tilejson.json' },
  hillshadeSource: { type: 'raster-dem', url: 'https://tiles.mapterhorn.com/tilejson.json' },
},
layers: [ /* … */ { id: 'hills', type: 'hillshade', source: 'hillshadeSource' } ],
terrain: { source: 'terrainSource', exaggeration: 1 },
```
plus `map.addControl(new maplibregl.TerrainControl({ source: 'terrainSource', exaggeration: 1 }))`. Self-hosted Terrarium tiles: `{type:'raster-dem', tiles:[…], encoding:'terrarium', tileSize: 256|512}`. Check Mapterhorn's attribution page before shipping (未验证 terms). With terrain on, `map.queryTerrainElevation(lngLat)` gives ground height for placing your own objects.

## Self-hosted PMTiles

```bash
pmtiles extract https://<your-copy>/planet.pmtiles europe.pmtiles --bbox=-25,34,45,72 --maxzoom=15
```
Copy the daily build to your own storage first (Protomaps asks not to hotlink). In the browser:
```js
import { Protocol } from 'pmtiles';
maplibregl.addProtocol('pmtiles', new Protocol().tile);
// source: { type: 'vector', url: 'pmtiles://https://cdn.example.com/europe.pmtiles' }
```
Style: `@protomaps/basemaps` (5.7.2, BSD-3) generates layers for its schema. The `--bbox` / `addProtocol` usage is from memory of the pmtiles docs, not re-read today (未验证 exact flags for 4.5.0). Europe size at z15 not measured.

## three.js inside MapLibre

Two options:

1. **`maplibre-gl-three` 3.0.0** — used by the official examples since 2026-10-06 (`ThreeDManager`, `createLayer()`, `getEcefMatrix({ point:[lon,lat], height })`, `load3dTiles`). https://raw.githubusercontent.com/maplibre/maplibre-gl-js/main/test/examples/add-3d-tiles-3d-objects-and-models-using-threejs.html . Licence of that package not checked (未验证).
2. **Hand-written custom layer** — the earlier official example (commit f9140dc, 2025-06):
```js
const origin = [13.3777, 52.5163];
const mc = maplibregl.MercatorCoordinate.fromLngLat(origin, 0);
const s = mc.meterInMercatorCoordinateUnits();
const layer = {
  id: 'city-block', type: 'custom', renderingMode: '3d',
  onAdd(map, gl) {
    this.map = map;
    this.camera = new THREE.Camera();
    this.scene = new THREE.Scene();          // your meshes, in local metres (x east, y up, z south)
    this.renderer = new THREE.WebGLRenderer({ canvas: map.getCanvas(), context: gl, antialias: true });
    this.renderer.autoClear = false;
  },
  render(gl, args) {
    const m = new THREE.Matrix4().fromArray(args.defaultProjectionData.mainMatrix);
    const l = new THREE.Matrix4().makeTranslation(mc.x, mc.y, mc.z)
      .scale(new THREE.Vector3(s, -s, s))
      .multiply(new THREE.Matrix4().makeRotationX(Math.PI / 2));   // three's y-up -> map's z-up
    this.camera.projectionMatrix = m.multiply(l);
    this.renderer.resetState();
    this.renderer.render(this.scene, this.camera);
    this.map.triggerRepaint();   // only while animating; otherwise skip to save battery
  },
};
map.on('style.load', () => map.addLayer(layer));
```
The example notes `args.getMatrixForModel(origin, altitude)` works under any projection (e.g. globe). Not re-run on 6.15 (未验证). Source: https://github.com/maplibre/maplibre-gl-js/blob/f9140dc2c2ff2b77bdac4d882ce1f2452e2293e6/test/examples/add-a-3d-model-using-threejs.html

Rules: `renderingMode:'3d'` shares the depth buffer, blending is premultiplied alpha, render-to-texture belongs in `prerender` (https://maplibre.org/maplibre-gl-js/docs/API/interfaces/CustomLayerInterface/). Keep the custom layer to the active city block; let fill-extrusion draw everything else.

## deck.gl (alternative overlay)

`deck.gl` 9.4.0 (MIT). Use `@deck.gl/maplibre` (MapLibreOverlay) for MapLibre; in interleaved mode the pixel ratio comes from MapLibre's `pixelRatio`. Good for heatmaps of production, trade routes (ArcLayer), many instanced markers. https://deck.gl/docs/api-reference/mapbox/mapbox-overlay (MapLibreOverlay page not read, 未验证.)

## Zoom plan (rule of thumb, 未验证 numbers)

| Zoom | Show | Data |
|---|---|---|
| 3–6 | Europe, game regions as fills + borders | Natural Earth / simplified admin polygons (GeoJSON, a few MB) |
| 7–12 | Region detail, cities as points, resource fields | Vector tiles + game overlay |
| 13–14 | City districts, flat building footprints | Vector tiles |
| 15+ | 3D extrusions, ownership tint, picking | fill-extrusion |
| 16+ (selected block) | three.js factories, construction, animated props | custom layer |
