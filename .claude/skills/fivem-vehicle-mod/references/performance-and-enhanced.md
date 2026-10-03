# Performance, limits and GTA V Enhanced

## Size warnings — what FiveM actually checks
- FXServer measures each streamed asset's **physical and virtual memory** use (not the file size). Over **16 MiB** it prints `Asset <resource>/<file> uses <n> MiB of <physical|virtual> memory.` (colour escalates at 32 and 64 MiB). Only above **48 MiB** does it add "Oversized assets can and WILL lead to streaming issues (such as models not loading/rendering)." The resource start line then shows `Started resource X (N warnings)`. (FiveM source: ResourceStreamComponent.cpp ValidateSize)
- So "16 MB" is a warning threshold per asset per memory type, not a hard block — but treat it as the budget, because many heavy cars together cause texture loss.
- Memory use is at least the file size; a file under 16 MB can still trigger the warning. The server console after `ensure` is the authoritative check — read it.

## Texture loss ("city bug")
Cfx describes it as streaming issues "caused by loading larger amounts of custom addon player vehicles". Mitigations: smaller and compressed textures, split HD textures into `+hi.ytd` (base ytd keeps a half-res copy), fewer/lighter vehicles in the same area.

### Client texture caps
`str_maxVehicleTextureRes` (default 1024) and `str_maxVehicleTextureResRgba` (default 512, for uncompressed A8R8G8B8/A8B8G8R8) are **client** archived ConVars — each player sets them in F8; they are not server convars and no evidence shows a server can force them. They mip-skip textures of vehicle archetypes. (FiveM source: TextureStreamingLimits.cpp; Cfx docs console-commands lists the first)

## Texture formats
- Legacy supports DXT1, DXT3, DXT5, ATI1 (BC4), ATI2 (BC5), BC7, A8R8G8B8 and others (CodeWalker Texture.cs).
- Vanilla vehicles (measured by muto-atlas): normals mostly DXT1 (ATI2 rare), spec DXT1, diffuse DXT1 without alpha / DXT5 with alpha.
- Always: power-of-two sides, full mip chain. DXT1 has no alpha (cut-outs close up). Avoid uncompressed textures — they get the stricter 512 cap and use the most memory. BC5/ATI2 for high-quality normals is community consensus, not official.
- Sollumz embeds textures from the DDS files on disk; edits made only inside Blender aren't exported (muto-atlas).

## LODs and geometry
- Sollumz LOD levels: Very High, High, Medium, Low, Very Low. In a vehicle, High/Medium/Low/Very Low → L0–L3 in `<model>.yft`; Very High → `<model>_hi.yft`.
- Polygon budget: there is no official number. This project uses LOD0 under ~50k triangles (CLAUDE.md); `lod-pipeline` and `retopology` skills help build the lower levels.
- Vehicles have a 128-bone limit (SSLA README). Sollumz splits geometry at 65,535 indices.
- `lodDistances` (6 floats in vehicles.meta): copy from a similar vanilla car; if the car pops or vanishes at distance, check that all LOD levels exist and compare distances with vanilla.

## Pre-release budget checklist
- [ ] Server console after `ensure`: no `uses … MiB` warnings, or only a few just over 16 MiB
- [ ] Every texture compressed, power-of-two, mipmapped; large ones split into `+hi.ytd`
- [ ] L0–L3 present; LOD0 within budget
- [ ] `check_vehicle_resource.py` and `fivem-vehicle-validator` clean
- [ ] Tested with several custom vehicles in view, not just one

## GTA V Enhanced (Gen9) client — status October 2026
- FiveM for GTA V Enhanced is in **early access** (launched July 2026; patch notes continue at github.com/citizenfx/rfc/discussions). Official migration page: Cfx docs `developers/legacy-vs-enhanced`.
- Facts from that page: asset escrow not implemented yet; pure mode always on (no client graphics mods, so client ASIs like SSLA can't be used); only the latest game build.
- Folder: put Gen9 assets in **`stream_enhanced/`**; with both folders present, Enhanced loads only `stream_enhanced` (patch notes 2026-09-22). Keep Gen8 assets in `stream/` for Legacy players.
- **Alchemist** (official converter; download from portal.cfx.re; Windows 11): converts YDR, YTD, YFT, YPT, YDD. Meta files are not converted and stay the same. GUI: pick Asset Conversion or Asset Refinement, input and output folders, Convert. CLI: `AlchemistCli.exe <in> <out> [--refine] [--relaxed] [-f] [-jN] [--fail-on-error]`. The GUI aborts on escrowed assets; the CLI skips and lists them. Run refinement before conversion if conversion output misbehaves (community advice: always `--refine` first).
- **Sollumz ≥ 2.8.0** can export native binaries for Gen8 and/or Gen9 into separate `gen8/` and `gen9/` folders — an alternative to Alchemist when you have the .blend.
- Vehicle-related notes from patch notes: vehicle data validation now also runs on Enhanced (invalid vehicle data is caught before it crashes the client, 2026-09-30); vehicle stream request pool overflow fixed for servers with many vehicles (2026-09-30); open report #567 (2026-10-01): FXServer b157 `data_file` mounts freeze the Enhanced client — if seen, try the previous server build.
- Community report: some DLC engine sound banks play no sound on Enhanced while base-game banks work; remap `audioNameHash` to a base-game car of the same class (awesome-fivem-vehicles; unverified).
