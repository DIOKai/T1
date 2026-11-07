# Helicopter workflow: AH-6 Little Bird (KS mkaLvAeoprg, all from frames)

KS models the **mechanical core before the skin**. Times are video timestamps.

1. **0:40-1:30 Reference.** Side, front and top photo planes are placed in 3D around the origin, not blueprint lines.
2. **2:40-4:40 Fuselage egg.** The cockpit shell starts as a mirrored half shell with a curved quad grid built along the side profile. The N panel shows the **Auto Mirror** add-on (Cut and Mirror, Use Clip) and **LoopTools**. By 4:00 the grid follows the egg silhouette over the photo. The tail boom is added at 4:40-5:20.
3. **5:20-7:20 Tail boom and tail parts.** The tail boom, the tail-rotor gearbox and the T-tail start as blocked-out cylinders.
4. **8:00-20:00 Turbine and drivetrain.** The engine is built from lathe-like stacked cylinders: inset and extrude rings, then bevels. After it come the drive shafts, couplings, hydraulic lines and clamps, as many small separate objects.
5. **22:00-40:00 Rotor head.** The mast, hub and blade grips start as primitives with a radial pattern (repeated around the hub, likely an array). Then the swashplate, pitch links and scissor links.
6. **40:00-50:00 Skids and frame.** The cross tubes, landing skids and fuselage floor structure are built at this stage.
7. **50:00-58:00 Weapons.** The minigun is built from cylinders around an axis with an end plate full of holes, and a rocket pod is added. A small **asset library of reusable bolts, caps and cylinders** appears in the Asset Browser at the bottom of the screen from about 1:10 on.
8. **1:00:20-1:04:00 Canopy and door openings.** **Bool Tool** (Auto Boolean: Difference/Union/Slice) is used on a semi-transparent fuselage to cut doors and window openings.
9. **1:04-1:30 Cockpit interior.** Seats with subdivided cushions, cyclic and collective sticks, instrument panel and armour plates.
10. **1:36-1:50 Exterior skin.** Panel lines and hatches are cut into the shell; a hatch is outlined with a support border at 1:41. At 1:44 the reference photo is shown on the shell (likely projected) to trace panel lines. **Rivets** are added as small objects snapped onto the surface, with "Project Individual Elements" visible in the snap options at 1:48.
11. **1:52-2:12 Small parts.** Steps, antennas, the FLIR ball turret (sphere with window cut, 2:04-2:11), lights and the tail fin.
12. **2:13-2:24 Materials.** Shader node work, then image textures for instrument gauges (2:23).
13. **2:24-2:30 Render.** Final turntables with high subdivision; dense rivets and panel lines are visible in the wireframe.

Takeaways for a GTA helicopter:
- Lock the fuselage silhouette first and keep the **rotor mast, tail rotor and doors as separate objects** so they can rotate. Each needs a correct pivot at its rotation centre.
- The KS level of mechanical detail (turbine, swashplate, rivets as geometry) is far beyond a game budget. Keep the main rotor head and skids. Bake rivets and panel lines into a normal map. Drop the hidden turbine unless the cowling opens.

---
