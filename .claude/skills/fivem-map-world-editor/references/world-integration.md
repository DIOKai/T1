# World integration

## Placement and dependencies

Resolve YMAP entity -> YTYP archetype -> asset/dictionaries -> visual/collision files. Include base-game/DLC and minimum-build dependencies. Inspect duplicate names across resources; successful last-wins loading is not proof of compatibility.

Use tool calculations for extents/flags after edits. Review generated _manifest.ymf dependencies and keep stream/ and fxmanifest.lua consistent. Register custom YTYPs with the applicable data file type; do not create redundant archetypes for stock props.

## LOD and terrain

Asset mesh LODs and world entity LOD relationships are separate. Removing a close object can leave its distant representation; deleting/reordering entities can invalidate parent indices. Inspect both levels before changing draw distance.

Preserve an untouched area export with coordinates, filenames, build and hashes. Inspect terrain and collision seams along the complete boundary, especially road junctions, bridges, tunnels, water and interior entrances. Hidden visuals do not prove collision, distant objects, occluders or traffic data were removed.

## Conditional advanced checks

- Occlusion: inspect view-dependent disappearance from valid sides; do not delete all occluders.
- Distant lights: check ownership and day/night transition after exterior changes.
- Car generators/scenarios: compare positions/headings with the new geometry.
- Navigation: verify current tools and pedestrian/vehicle data separately. A road mesh does not create traffic lanes or navigation.
- Multiplayer: distinguish streamed static placements from scripted networked objects; overlapping spawns may mimic Z-fighting.

These are investigation targets. Do not claim the available toolchain can edit every layer; label unsupported work unresolved.

## Sources

Checked 2026-10-15:
- [Cfx placement guide](https://docs.fivem.net/docs/assets-manual/beginner-series/part-4/): placements, calculations, manifests and resource structure.
- [Cfx LOD guide](https://docs.fivem.net/docs/assets-manual/beginner-series/part-6/).
- [Cfx collision guide](https://docs.fivem.net/docs/assets-manual/beginner-series/part-5/).
- [CodeWalker](https://github.com/dexyfex/CodeWalker): verify installed-version advanced support.
- [Sollumz archetype format](https://docs.sollumz.org/documentation/archetype-definition.ytyp).
