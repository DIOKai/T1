# Lighting and sky (Blender 5.x, Cycles first)

## Sky Texture — names changed in 5.0
| Sky Type (5.x) | bpy enum | Status |
|---|---|---|
| **Multiple Scattering** | `'MULTIPLE_SCATTERING'` | new in 5.0, "most accurate" — use for archviz |
| Single Scattering | `'SINGLE_SCATTERING'` | this is the old **Nishita**; legacy, may be removed |
| Preetham, Hosek/Wilkie | `'PREETHAM'`, `'HOSEK_WILKIE'` | legacy, will be removed |

Old scripts with `sky_type = 'NISHITA'` raise an error in 5.x. Version attribution comes from comparing the 4.5 and 5.0 manuals.

Parameters: Sun Disc (**Cycles only**), Sun Size, Sun Intensity, **Sun Elevation**, **Sun Rotation**, **Altitude** (beach = 0), **Air** (1 ≈ city air), **Aerosols** (was Dust), **Ozone** (bluer sky). The manual warns these skies "are very bright by default (hence accurate)" — lower **Color Management ▸ Exposure** instead of the sky strength.

```python
# NOT RUN in Blender: built from the ShaderNodeTexSky API page.
import bpy, math
world = bpy.context.scene.world
nt = world.node_tree
sky = nt.nodes.get("Sky Texture") or nt.nodes.new("ShaderNodeTexSky")
sky.sky_type = 'MULTIPLE_SCATTERING'
sky.sun_elevation = math.radians(4)     # golden hour
sky.sun_rotation = math.radians(230)
bg = nt.nodes.get("Background")
nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
bpy.context.scene.view_settings.exposure = -3.0   # starting guess; check with False Color
```

**Real place and time**: the free official **Sun Position** extension (GPL, Blender 4.2+) drives a sun lamp and the sky from latitude/longitude/date/time and can sync HDRI rotation (e.g. a Saint-Tropez villa at its real coordinates).

## Times of day
- Golden hour ≈ sun −4° to +6°; blue hour ≈ −6° to −4° (photography convention, no official definition).
- Golden: Sun Elevation 2–6°, long shadows, warm. Blue hour: sky light plus interior lights and lit windows carry the image (Multiple Scattering below the horizon: test-render it, unverified).
- White balance: Color Management ▸ White Balance (Temperature/Tint, default D65) warms/cools the whole image.
- Night: lit windows need a **real interior with lights** behind real glass (user's LESSONS rule), not emissive planes with a printed room. Weakly glowing meshes: turn their MIS off to reduce noise; bright emitters that act as lights: keep MIS on.

## Light strengths (manual reference table)
- Sun lamp (W/m²): clear 1000, overcast 500–200, moonlight 0.001.
- Radiant watts, not electrical: candle 0.05 W; 800 lm LED bulb 2.1 W; 1000 lm bulb 2.9 W; 1500 lm PAR38 4 W (Area Disk); 2500 lm fluorescent tube 4.5 W (Area Rectangle).
- Use lamp **Temperature** (Kelvin), **Normalize** (power stays the same when resizing), Point/Spot **Radius** and **Soft Falloff**; Area **Spread** mimics a softbox grid (Cycles).
- Renders look brighter/darker than the eye expects (no auto-adaptation) → compensate with Exposure.

## Exposure workflow
1. Set the sky/sun physically. 2. Adjust **Color Management ▸ Exposure** (stops, before the view transform) or Film ▸ Exposure (Cycles, on data). 3. Check with the **False Color** view: blue = under, grey (≈ 16–22 % middle grey) = good, red/white = clipped. 4. Interior vs exterior balance: **Light Groups** (Cycles: one pass per group — sun, sky/world, interior) and rebalance in the compositor; or an Exposure node with a mask on the window area (the manual's own example).

## HDRI
World ▸ Settings ▸ Sampling Auto/Manual (MIS) must be on when the HDRI has a small bright sun; higher Map Resolution = more accurate. Use a Light Path "Is Camera Ray" mix to show a high-res HDRI in the background and light with a low-res one (or the reverse). 5.2 adds a World **Cast Shadows** option. Free HDRIs: Poly Haven (CC0, no attribution needed).

## Interiors: portals, path guiding, light tree
- **Light Portal**: Area light with Portal on, same shape as the window/door opening, placed in it. "Significantly reduce noise in interior scenes"; each sample is slower but converges with fewer samples. **Useless for exteriors.** 5.0 adds a Portal Depth light path output.
- **Path Guiding** (CPU only): for rooms lit through a small opening; Training Samples 128–256 are usually enough.
- **Light Tree**: samples many lights efficiently (lots of downlights), ignores custom falloff and textured lights.

## IES and artificial light
IES Texture node (Internal/External) → Emission Strength of the lamp's node tree. **Cycles only**: "EEVEE ... ignores light shader node trees". Free IES files: ieslibrary.com (reported in 2020 as 90 000+ free, commercial use allowed — current status unverified). Light Falloff node "Smooth" reduces hot spots close to walls. Clamp **Indirect** rather than direct light to keep highlights.

## Sources
- Sky Texture (5.x manual): https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/sky.html
- Sky API: https://docs.blender.org/api/current/bpy.types.ShaderNodeTexSky.html
- 4.5 vs 5.0 Sky manual: https://docs.blender.org/manual/en/4.5/render/shader_nodes/textures/sky.html , https://docs.blender.org/manual/en/5.0/render/shader_nodes/textures/sky.html
- Sun Position extension: https://extensions.blender.org/add-ons/sun-position/
- Golden/blue hour: https://sunrisesunset.io/golden-hour-blue-hour/ , https://www.home-assistant.io/conditions/sun.is_golden_hour/
- Light objects (strength table): https://docs.blender.org/manual/en/latest/render/lights/light_object.html
- Cycles light settings (portals, node trees): https://docs.blender.org/manual/en/latest/render/cycles/light_settings.html
- Reducing noise: https://docs.blender.org/manual/en/latest/render/cycles/optimizations/reducing_noise.html
- Sampling (path guiding, light tree): https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html
- World settings (MIS): https://docs.blender.org/manual/en/latest/render/cycles/world_settings.html
- Color management (Exposure, False Color, White Balance): https://docs.blender.org/manual/en/latest/render/color_management/displays_views.html
- Film exposure: https://docs.blender.org/manual/en/latest/render/cycles/render_settings/film.html
- Exposure node (window mask example): https://docs.blender.org/manual/en/latest/compositing/types/color/adjust/exposure.html
- Passes / Light Groups: https://docs.blender.org/manual/en/latest/render/layers/passes.html
- IES: https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/ies.html ; EEVEE limits: https://docs.blender.org/manual/en/latest/render/eevee/limitations/limitations.html
- 5.0 Cycles notes (Portal Depth): https://developer.blender.org/docs/release_notes/5.0/cycles/ ; 5.2 Cycles notes: https://developer.blender.org/docs/release_notes/5.2/cycles/
- Poly Haven license: https://polyhaven.com/license ; IES library report (2020): https://www.cgchannel.com/2020/06/download-over-90000-free-ies-lighting-files-from-ies-library/
