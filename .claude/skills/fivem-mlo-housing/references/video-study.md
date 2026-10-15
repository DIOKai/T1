# MLO video study

Primary visual workflow sources:

- [Desertos — Creating custom MLO interior in Blender/Sollumz](https://www.youtube.com/watch?v=NN-fjCbPO1Q), 1:38:38. Its published chapters cover exterior export, interior modeling, coordinate recording, room division, collision, portals, MLO metadata, export, CodeWalker placement, visual fixes, vertex color, texture dictionary, exterior collision, props, FiveM streaming, occlusion, and in-game testing.
- [Creating your own MLO with Blender/Sollumz for FiveM (2026)](https://www.youtube.com/watch?v=ul-obDJ3e1U), a newer complementary demonstration.

No exportable transcript was available for either video during review. Therefore, use the videos to find visual demonstrations while deriving technical requirements from the current Sollumz and Cfx sources cited in `mlo-authoring.md`.

## Workflow lessons reinforced by the chapter structure

- Record world coordinates/orientation before moving editable geometry to a convenient local origin. Placement errors otherwise masquerade as missing assets.
- Visible geometry, collision, room/limbo bounds, portals, MLO archetype data, and YMAP placement are distinct deliverables. Check each one separately.
- Fixing an entrance may require modifying every relevant exterior collision asset, not only cutting a visible doorway in the rendered building.
- Vertex color, texture dictionaries, props, lighting/occlusion, and visual cleanup come after the basic room/portal/collision round trip works.
- The final gate is streaming the packaged resource into FiveM and walking every transition. A CodeWalker preview is not gameplay acceptance.

## Acceptance evidence

Retain screenshots or notes for: recorded placement transform; room and limbo bounds; each portal's direction and four corners; interior and exterior collision tests; archetype/YMAP name match; calculated flags/extents; generated manifest; resource restart/reconnect; daylight, night, rain, and audio behavior.
