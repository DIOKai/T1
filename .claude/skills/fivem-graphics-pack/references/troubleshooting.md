# Troubleshooting: symptom → cause → fix

Start with `check_graphics_pack.py <resource>`, then the server console after `ensure` (size warnings), then F8 in game.

| Symptom | Likely cause | Fix |
|---|---|---|
| Look doesn't apply at all | XML not registered (`data_file 'TIMECYCLEMOD_FILE'`) or not in `files{}`; modifier name typo in the script; resource not started | run the checker; `ensure` the resource; print the name you pass to `SetExtraTimecycleModifier` |
| Some values change, others don't | `numMods` lower than the variable count; misspelt variable (silently ignored) | checker `NUMMODS_MISMATCH` / `VAR_UNKNOWN`; copy names from `assets/timecycle_vars.txt` |
| Look disappears when using a camera, drug or interior script | pack and script both use the primary slot | move the pack to the extra slot (`SetExtraTimecycleModifier`) — the generator already does |
| Look fights another graphics resource | two packs on the same slot, or same modifier names | keep one pack; unique prefixed names |
| Great at noon, too dark/orange at night | fixed sky/light values in the modifier | keep looks to `postfx_*` variables; tune at several hours and weathers |
| TimeCycle Editor missing | server pure level > 0 (editor is compiled out of pure mode) | local dev server with `sv_pureLevel 0`, F8 `timecycleeditor true` |
| visualsettings changes do nothing | shipped `visualsettings.dat` without a script, or wrong key name | apply with `SetVisualSettingFloat` from a client script; copy names from the vanilla file |
| visualsettings revert | the resource that set them stopped or restarted | expected — values are tied to the setting resource |
| `Asset … uses N MiB of physical memory` in console | 4K/uncompressed textures in one `.ytd` | DXT1/DXT5 with mips, 2K where possible, split dictionaries |
| Textures blurry / low-res in game | player's texture quality below Very High (no `+hi`); vehicle texture cap 1024; streaming budget full | tell players: Very High textures, `str_maxVehicleTextureRes 2048`, raise Extended Texture Budget (`vid_budgetScale`) |
| Missing/white/purple textures after a texture pack | replacement `.ytd` lacks some original texture names | rebuild from the full vanilla dictionary, only swapping upgraded textures |
| Long join times, crashes on low-end PCs | pack too heavy | total the pack size; offer the `low` tier; cut 4K |
| ReShade doesn't load | Enhanced client; server pure level / plugins blocked; ReShade ≥ 5 without the `CitizenFX.ini` acknowledgement line; 5.9.0 | Legacy only; copy the exact line from F8 into `[Addons]`; update to ≥ 5.9.1 |
| ReShade loads but LUT looks wrong | wrong LUT size or tile settings; LUT saved with colour management / resized | 1024×32 for defaults; match `fLUT_TileSizeXY`/`fLUT_TileAmount`; save as plain PNG without scaling |
| FPS dropped | heavy ReShade effects (AO, DOF), high shadow/LOD settings in the look | fewer effects; `low`/`medium` tier; measure with and without |
