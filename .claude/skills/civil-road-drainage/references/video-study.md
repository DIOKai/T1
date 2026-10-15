# FreeCAD road and drainage video study

Visual sources:

- [FreeCAD Trails Horizontal Alignment Design Tool Update](https://www.youtube.com/watch?v=QRTd7056yy8)
- [Create Drainage Piping System in FreeCAD BIM](https://www.youtube.com/watch?v=sQhC8w8SeN8)

No exportable transcript was available during review. The drainage tutorial's community description explicitly frames it as a simple system made with limited FreeCAD MEP tools. Treat both videos as geometry demonstrations, not evidence of standards compliance, hydraulic sizing, or construction readiness.

## Alignment checks

- Confirm the imported terrain/controls, station origin and direction, curve definitions, units, and design-standard source.
- Inspect tangency and station continuity and compare key coordinates/radii with an independent schedule or calculation.
- Do not infer minimum radius, transition length, superelevation, sight distance, or widening from tool defaults.

## Drainage checks

- Record pipe/channel nodes, invert levels, lengths, gradients, diameters, materials, fittings, and outlet boundary conditions.
- Verify positive drainage and connectivity using a tabulated node-to-node check; a connected-looking 3D model may still contain inverted or disconnected runs.
- Mark the model `geometry only` until catchments, rainfall, runoff, capacity, surcharge, tailwater, velocity/erosion, cover, and maintenance access are checked using the supplied governing method.
- A BIM pipe object is not proof of hydraulic performance.
