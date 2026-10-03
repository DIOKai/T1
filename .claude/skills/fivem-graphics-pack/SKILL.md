---
name: fivem-graphics-pack
description: Build and tune GTA V / FiveM graphics packs — server-side "looks" every player gets (warm, cool, cinematic, realistic colour grading via timecycle modifiers), visualsettings tweaks, 2K/4K/UHD texture replacements (roads, buildings, vehicles), and client-side ReShade presets and LUTs — and keep them within FiveM's memory, streaming and pure-mode limits. Use whenever the user wants a graphics pack, better graphics, colour grading, warm or cinematic tones, sharper or higher-resolution textures, NVE/QuantV-style visuals without paying, a ReShade preset or LUT, timecycle or visualsettings edits, or asks why a graphics mod doesn't show or crashes — even if they only say "画质包", "画质", "暖色", "滤镜", "4K 贴图", "UHD", "timecycle", "reshade".
---

# FiveM graphics packs

"Graphics pack" means three different things, and the first job is to work out which one the user wants, because they're built, shipped and limited differently:

| Kind | What it changes | Who installs it | Works on |
|---|---|---|---|
| **Server-side look** (timecycle modifiers, visualsettings) | colour, contrast, vignette, bloom, fog, light intensity | the server — every player gets it automatically | Legacy and Enhanced, any pure level |
| **Texture pack** (streamed `.ytd`) | sharper / 2K / 4K roads, buildings, vehicles | the server | Legacy and Enhanced; costs VRAM and download size |
| **Client-side ReShade** (+ LUT) | any post effect: sharpening, LUT grading, AO, DOF | each player on their own PC | Legacy only, and only where the server allows plugins |

"2K / 4K / UHD" in a pack name almost always means **texture resolution** (2048² / 4096² textures), not screen resolution — screen resolution is each player's own game setting. "暖色 / 冷色 / 电影感" is colour grading: do it server-side with timecycle modifiers (everyone sees it, nothing to install) or client-side with a LUT.

Read the reference you need:
- `references/timecycle.md` — modifier XML, the two slots and their natives, the in-game TimeCycle Editor, weather/time files, variable cheat-sheet.
- `references/visualsettings.md` — `SET_VISUAL_SETTING_FLOAT`, what it can change, how to ship it.
- `references/textures.md` — replacing vanilla textures, `+hi` dictionaries, memory maths, 16/48 MiB, texture-budget convars, free upscaling and DDS tools, licences.
- `references/reshade.md` — installing ReShade for FiveM (plugins folder, ReShade 5 acknowledgement line, blocked versions), presets, LUTs, shader licences.
- `references/troubleshooting.md` — symptom → cause → fix.

Related skills: `fivem-script` and `fivem-pro` (client scripts, resmon), `fivem-vehicle-mod` (vehicle texture limits), `muto-atlas` (vanilla timecycle/weather data, ask before `/asset-setup`), `document-skills` / image tools for screenshots.

## Workflow

### 1. Pin down the goal
Ask, or infer from the request: which kind (table above), which looks (warm / cool / cinematic / realistic / custom), whether players should be able to switch or turn it off, Legacy or Enhanced, and the players' typical hardware (VRAM decides how far textures can go).

### 2. Server-side look (the default answer to "画质包 / 暖色")
Generate a ready resource:

```
python .claude/skills/fivem-graphics-pack/scripts/make_timecycle_pack.py --name <prefix> -o <resources>/<prefix>
```

It writes `fxmanifest.lua` (`data_file 'TIMECYCLEMOD_FILE'`), `data/timecycle_mods_<prefix>.xml` with one modifier per look × performance tier (`--no-tiers` for looks only), a `client.lua` with `/graphics <look|off> [low|medium|high]` that saves each player's choice (KVP), and a README. It applies the look in the **extra** timecycle slot, so other scripts' `SetTimecycleModifier` effects (cameras, drugs, interiors) keep working. Options: `--looks warm,cinematic`, `--default warm`.

The generated values are **starting points, not measured standards**. Tune them in game: dev server with `sv_pureLevel 0` → FiveM's TimeCycle Editor → adjust → "Generate XML" → paste back, keeping `numMods` equal to the number of variables. Variables and their effects: `references/timecycle.md`. Light, bloom and reflection strength that timecycle can't reach: `references/visualsettings.md`.

### 3. Texture pack (2K / 4K)
Replace a vanilla texture dictionary by streaming a `.ytd` with the **same name** containing textures with the **same names**. Budget it before building — 4096² DXT5 ≈ 21 MiB per texture with mips, and one oversized `.ytd` triggers FXServer's 16 MiB warning. Prefer 2K for most things and 4K only where the camera gets close (roads, hero props). `+hi` dictionaries only load when the player's texture setting is Very High. Details, tools and licences: `references/textures.md`.

### 4. ReShade (client-side, optional)
Only when the user wants effects timecycle can't do (sharpening, LUT grading, AO) and accepts that each player installs it. For a LUT look:

```
python .claude/skills/fivem-graphics-pack/scripts/make_lut.py --preset warm -o lut.png
python .claude/skills/fivem-graphics-pack/scripts/make_lut.py --temperature 0.3 --saturation 1.1 -o mylook.png
python .claude/skills/fivem-graphics-pack/scripts/make_lut.py --neutral -o lut_neutral.png   # grade by hand in GIMP/Krita
```

Presets: neutral, warm, cool, cinematic, realistic, vivid, noir; `--strength 0..1` blends. Output is the 1024×32 strip ReShade's `LUT.fx` reads. Install steps, the ReShade 5 acknowledgement line, and which shaders may be bundled: `references/reshade.md`.

### 5. Check
Run `python .claude/skills/fivem-graphics-pack/scripts/check_graphics_pack.py <resource-or-folder>` (local, read-only, Python only). It catches: `numMods` ≠ variable count, misspelled timecycle variables (checked against the 423 vanilla names in `assets/timecycle_vars.txt`), non-numeric values, duplicate or generic modifier names, timecycle XML not registered as `TIMECYCLEMOD_FILE`, `data_file` paths that match nothing or aren't in `files{}`, `WEATHER_FILE`/`TIME_FILE` use, a `visualsettings.dat` no script applies, `.ytd` over 16/48 MiB or without an RSC7 header, ReShade presets without `Techniques=`, and LUT images with the wrong shape.

Then test in game: day and night, clear and rain, inside an interior, and on a low-VRAM PC if textures were added. Compare FPS and `resmon` before and after.

## Ground rules
- Free only. NaturalVision Evolved and QuantV are paid; iMMERSE Pro is paid; AI image services (Topaz, Magnific, fal, inference.sh) are paid or credit-based — don't recommend them. Free tools are listed in the references, with licences.
- Don't redistribute other people's packs or shaders without permission: qUINT and iMMERSE forbid redistribution; SweetFX and prod80 are MIT. "Inspired by NVE" is fine; copying NVE files is not.
- Don't present tuning numbers as facts. Vanilla values come from the game files; everything the skill suggests beyond that is a rule of thumb to check in game.
- Enhanced always runs pure — ReShade and client graphics mods don't load there; server-side looks and textures do.
