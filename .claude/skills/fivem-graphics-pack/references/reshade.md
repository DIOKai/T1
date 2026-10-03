# ReShade in FiveM (client-side)

ReShade is a post-processing injector each player installs on their own PC. It can do things the timecycle can't (sharpening, LUT colour grading, ambient occlusion, better DOF), but nobody else sees it, and servers can block it. Offer it as an optional extra next to a server-side look, not instead of one.

## Where it works

- **FiveM Legacy (DX11) only.** FiveM Enhanced always runs pure, so no ReShade or client graphics mods load there.
- The server must allow plugins. `sv_pureLevel 1` blocks modified client files "except audio files and known graphics mods"; `sv_pureLevel 2` blocks all modified client files (fivem-docs, server-commands). Servers can also disallow plugins outright.

## Installing for FiveM

1. Install ReShade (free, reshade.me) for DirectX 10/11/12, pointing it at any folder, and choose the effect packages to download.
2. Copy `dxgi.dll` (renamed from ReShade64.dll by the installer), `ReShade.ini`, and the `reshade-shaders` folder into **`%localappdata%\FiveM\FiveM.app\plugins`** (create `plugins` if missing). FiveM loads plugins from there (fivem-docs, client manual).
3. **ReShade 5.0 or newer is blocked by default** (`rage-graphics-five/src/ReShadeFixups.cpp`). On first launch FiveM prints, in the F8 console, the exact line to add to `FiveM.app\CitizenFX.ini`:
   ```ini
   [Addons]
   ReShade5=ID:xxxxxxxx acknowledged that ReShade 5.x has a bug that will lead to game crashes
   ```
   The `ID` is a hash of the PC's computer name, so it differs per PC. Copy it from the console, don't reuse someone else's.
4. **ReShade 5.9.0 is hard-blocked** (heap corruption); use 5.9.1 or newer. Versions below 3.1 are refused.
5. Versions before 5.9 also conflict with the NUI setting `nui_useInProcessGpu`, so keep ReShade up to date.
6. Press Home in game to open the ReShade overlay; enable effects and save a preset `.ini`.

## Presets

A preset is an `.ini` listing `Techniques=` (enabled effects) and per-effect sections with their values. Ship a preset plus a short list of the shader packages it needs; players load it from the overlay. Keep the effect count low — each costs FPS, and ambient occlusion/DOF are the most expensive.

## LUT colour grading

`LUT.fx` (crosire/reshade-shaders) reads a horizontal strip of `tiles` tiles, each `tiles × tiles` px (default 32 → 1024×32). Inside a tile x = red, y = green; the tile index = blue. Make one with:

```
python .claude/skills/fivem-graphics-pack/scripts/make_lut.py --preset warm -o lut.png
python .claude/skills/fivem-graphics-pack/scripts/make_lut.py --neutral -o lut_neutral.png
```

The neutral strip matches ReShade's own `lut.png` (max difference 1/255). To grade by hand: take an in-game screenshot, paste the neutral LUT into a corner, colour-grade the whole image in GIMP/Krita, then crop the LUT back out — the LUT now carries the grade. Put it in `reshade-shaders/Textures/` and select it in LUT.fx (`fLUT_TextureName`). For a 64-tile LUT also set `fLUT_TileSizeXY=64` and `fLUT_TileAmount=64` in PreprocessorDefinitions (the script prints this).

## Shader packages and licences

| Package | Licence | Bundle in a pack? |
|---|---|---|
| crosire/reshade-shaders (standard) | mixed, per file | link to it |
| SweetFX (CeeJayDK) | MIT | yes, with the licence |
| prod80 ReShade Repository (colour, LUT, film looks) | MIT | yes, with the licence |
| qUINT (martymcmodding) | "all rights reserved" | no — link to it |
| iMMERSE (martymcmodding) | "all rights reserved", no redistribution | no — link to it |
| iMMERSE Pro / RTGI | paid (Patreon) | don't recommend |

Paid "graphics packs" (NaturalVision Evolved, QuantV) are out. Free, licence-compatible look: timecycle modifiers server-side + an optional ReShade preset using SweetFX/prod80 + a LUT from `make_lut.py`.
