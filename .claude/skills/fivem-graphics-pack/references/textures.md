# Texture packs (2K / 4K / "UHD")

## How replacement works

The game finds textures by **dictionary name** (`.ytd` file name) and **texture name** inside it. Streaming a `.ytd` with the same name as a vanilla one from a resource's `stream/` folder replaces the whole dictionary. So:

1. Export the vanilla `.ytd` from **the user's own game** (CodeWalker RPF Explorer or OpenIV, both free).
2. Keep **every** texture in it, and swap only the ones you upgrade, keeping their names. A missing texture shows up as missing or default on every model that used it.
3. Save with the same file name and put it in `stream/` (no `data_file` needed for textures).

Vanilla dictionaries often come in pairs: `name.ytd` and `name+hi.ytd`. The `+hi` one holds the higher-resolution versions and is **only loaded when the player's texture quality is Very High** (FiveM source, `PatchExtendedBudgeting.cpp`: "very high … allow +hi TXDs"). Players on High or below never see a `+hi` upgrade, so upgrade the base dictionary too if that matters.

Vehicle textures live in the vehicle's own `.ytd` (and `vehshare.ytd` for shared ones) — see `fivem-vehicle-mod`.

## Memory maths — do it before building

Per texture, including the mip chain (≈ +33 %):

| Size | DXT1 / BC1 (0.5 B/px) | DXT5 / BC3 / BC7 (1 B/px) | A8R8G8B8 (4 B/px) |
|---|---|---|---|
| 1024² | 0.7 MiB | 1.3 MiB | 5.3 MiB |
| 2048² | 2.7 MiB | 5.3 MiB | 21.3 MiB |
| 4096² | 10.7 MiB | 21.3 MiB | 85.3 MiB |

FXServer warns when one streamed asset uses **> 16 MiB** of virtual or physical memory, and above **48 MiB** says oversized assets "can and WILL lead to streaming issues (such as models not loading/rendering)" (`ResourceStreamComponent.cpp`). It decodes the size from the RSC7 header, **not the file size on disk** — files are compressed, so a 15 MB `.ytd` can be a 30 MiB asset. `check_graphics_pack.py` decodes it the same way.

So a single 4096² DXT5 texture already breaks the 16 MiB line on its own. Rules of thumb:
- Use DXT1/BC1 for textures without alpha, DXT5/BC3 (or BC7) only where alpha or quality needs it. Never ship uncompressed A8R8G8B8 for big textures.
- 2K for most surfaces; 4K only where the camera gets close (roads under the player, hero props), and split such dictionaries so each stays under the warning.
- Always generate mipmaps — without them distant surfaces shimmer and the game can't drop resolution under memory pressure.
- Add up the whole pack: every player downloads it on join and it all competes for VRAM with vehicles, clothing and MLOs.

## Client-side limits players control

- **Vehicle textures are capped at 1024 px by default.** Client convar `str_maxVehicleTextureRes` (default 1024) limits textures in vehicle dictionaries; `str_maxVehicleTextureResRgba` (default 512) does the same for uncompressed A8R8G8B8/A8B8G8R8 textures (`TextureStreamingLimits.cpp`). The game simply drops mip levels until the texture fits. A "4K car" shows at 1024 unless the player raises it (F8: `str_maxVehicleTextureRes 2048`). Tell players this rather than shipping 4K vehicle textures nobody sees.
- **Extended texture budget**: client convar `vid_budgetScale` (FiveM's graphics settings) multiplies the streaming texture budget by `value / 12 + 1` (`PatchExtendedBudgeting.cpp`). Players with plenty of VRAM can raise it so texture packs don't blur under load.
- Texture quality: `+hi` dictionaries need Very High (above).

## Free tools

| Tool | Use | Licence |
|---|---|---|
| CodeWalker | open/extract/edit `.ytd`, import DDS, compile XML | free (open source) |
| OpenIV | browse/extract game archives | free (closed source) |
| texconv (Microsoft DirectXTex) | PNG/TGA → DDS with BC1/BC3/BC7 and mips, batch | MIT |
| Real-ESRGAN / Real-ESRGAN-ncnn-vulkan | AI upscaling 2×/4× on the user's own GPU, offline | BSD-3 / MIT |
| Upscayl | GUI for Real-ESRGAN-style models | AGPL-3 (fine to use) |
| chaiNNer | node-based batch image pipelines incl. upscaling | GPL-3 (fine to use) |
| GIMP / Krita | manual edits, tileable fixes | GPL |

Local upscalers install software and need a GPU — ask the user before setting one up. Paid upscalers (Topaz, Magnific, cloud APIs) are out.

Upscaling tips: work from the original DDS converted to PNG; upscale colour (diffuse) maps with a photo/texture model; for normal maps either upscale gently and renormalise or regenerate; keep tileable textures tileable (check seams); re-compress with mips at the end.

## Licences

AI-upscaled vanilla textures are still Rockstar's textures; texture packs for FiveM are common, but don't sell them. Never repackage someone else's pack (NVE, QuantV, or free packs without a licence) — "no licence" means no permission to redistribute.
