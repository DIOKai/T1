# Making the model game-ready for GTA V / FiveM

- **Polycount** (modding-forum "LOD models" guide). GTA counts **triangles**.
  - Original Rockstar cars: L0 60k-120k, L1 20k-30k, L2 10k-15k, L3 5k-10k, L4 500-1000.
  - A detailed custom L0: 100k-150k; L1 about 30k-40k.
  - Default LOD distances in `vehicles.meta`: L1 15 m, L2 30 m, L3 60-70 m, L4 120-140 m.
  - The T1 rule of keeping LOD0 under about 50k triangles is stricter than this. Use it as the working target.
- **Subdivision:** don't ship the render-level Subdivision. Apply level 1 at most on the body, or model the support loops by hand and stop. KG says high-poly isn't for engines and that the detail should be **baked** to the low-poly (KG9 0:50).
- **Tire tread:** KG's arrayed tread is "not recommended for game engines"; use a texture or normal map on simple extruded circles (KG19 12:23, 15:23). The same goes for the 7×2×Subdivision wheel spokes: keep the spoke cage low.
- **Panel gaps:** fine in geometry for L0. For L1+, merge the panels and use a normal or decal line.
- **Not usable in-game:** Shrinkwrap and Solidify decals, text objects and curves must be **applied and converted to mesh** before Sollumz export. Badges and logos in GTA are usually **texture or decal geometry**.
- **Lights:** the KG lens-over-emitter method matches GTA. The emitter gets the vehicle light shader and light IDs via vertex colours; the lens gets a glass material. This is done in Sollumz, not with Cycles emission.
- **Hidden parts:** KG's "void black plane" and "underside plane" match GTA practice for hidden interiors. GTA renders **back faces culled**, so these planes and inner walls must face the camera, or be doubled (see T1 LESSONS on engine-bay holes).
- **Naming and rigging:** the `vehicle-artist` names (`SM_Vehicle_*`) don't apply. Use GTA bone names (`chassis`, `wheel_lf`, `door_dside_f`, `bonnet`, `boot`, …) via muto-atlas. Wheels must be separate objects pivoted at the hub centre, which matches KG's separate wheel objects. For a helicopter, check rotor bone names in muto-atlas too.
- **Materials:** procedural Cycles node setups (KG20 car paint) don't export. Use the GTA vehicle shaders (paint slots and so on) in Sollumz with image textures.

---


## Hand-off checks (T1 lessons)

- Export with Sollumz as a fragment (.yft + _hi.yft + .ytd); start from a vanilla car of the same class for the bone list and fragment setup (Sollumz "Creating vehicles").
- Engine bay and underbody must be real 3D models in every LOD, not a photo on a plane; check holes with back-face culling on and a red ground render from player eye points (see `fivem-vehicle-mod`).
- Body panels keep at least ~40 % of their faces in Medium/Low LODs; interiors can drop more.
- Real brands become GTA brands on every badge and texture before release.
- **Collision:** GTA collision is Sollumz bounds on the fragment (copied from the vanilla donor and reshaped: a few convex hulls / boxes for the body, separate bounds for doors, bonnet, boot and wheels on their bones), not UCX_ meshes and never the visual mesh. Glass gets its own collision with the *Car Glass* material. Details: `fivem-vehicle-mod` → `references/modeling-sollumz.md`.
- **UVs:** every game mesh needs a UV map; keep UVs near 0-1 (GTA stores them as half floats, so values far outside lose precision and textures swim). Paint panels share the paint shader's UV layout; lights and badges use their own atlas.
- **Glass:** windows use the `vehicle_vehglass` shader (inner pane `vehicle_vehglass_inner`), skinned to the window/door bone with a shattermap mode; don't use a generic glass material.
- **Interior:** a real dashboard, seats, steering wheel and door cards are needed in L0 (first-person and through the glass); they can drop out at L2+. The steering wheel is its own object on the steering-wheel bone (`steeringwheel` in vanilla cars; confirm with muto-atlas `/vehicle`).
