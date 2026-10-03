# Timecycle modifiers

The timecycle is the game's per-weather, per-hour table of lighting and post-processing values (sky, fog, ambient light, bloom, colour correction, vignette, DOF…). Weather files hold the base keyframes; a **timecycle modifier** is a named set of overrides layered on top. A server-side graphics pack is a resource that ships modifiers and turns one on for each player.

## File format

FiveM's own TimeCycle Editor "Generate XML" button writes this format (`devtools-five/src/TimecycleEditor.cpp`), and vanilla `timecycle_mods_*.xml` use it too:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<timecycle_modifier_data version="1.000000">
  <modifier name="dio_gfx_warm" numMods="4" userFlags="0">
    <postfx_correct_col_r>1.050 0.000</postfx_correct_col_r>
    <postfx_correct_col_g>1.010 0.000</postfx_correct_col_g>
    <postfx_correct_col_b>0.920 0.000</postfx_correct_col_b>
    <postfx_desaturation>1.080 0.000</postfx_desaturation>
  </modifier>
</timecycle_modifier_data>
```

- Each child is a timecycle variable, text = two floats. **The first value is what applies**; keep the second at 0 (or copy what the editor generates).
- `numMods` must equal the number of child elements.
- Names must be unique across everything loaded — prefix them (`dio_gfx_…`). A modifier with a vanilla name overrides the vanilla one, which breaks every script that uses it.
- Variable names: `assets/timecycle_vars.txt` (423 names from vanilla `w_extrasunny.xml`). A misspelt variable is silently ignored.

Register it in `fxmanifest.lua`:

```lua
files { 'data/timecycle_mods_dio_gfx.xml' }
data_file 'TIMECYCLEMOD_FILE' 'data/timecycle_mods_dio_gfx.xml'
```

## Two slots — use the extra one for a pack

| Slot | Set | Clear | Strength |
|---|---|---|---|
| primary | `SetTimecycleModifier(name)` | `ClearTimecycleModifier()` | `SetTimecycleModifierStrength(0.0–1.0)` |
| extra | `SetExtraTimecycleModifier(name)` (`_SET_EXTRA_TIMECYCLE_MODIFIER`, 0x5096FD9CCB49056D) | `ClearExtraTimecycleModifier()` (0x92CCC17A7A2285DA) | none |

Gameplay scripts (security cameras, drugs, drunk effects, binoculars, some interiors and MLOs) use the primary slot. A pack that also uses it gets overwritten or overwrites them. Putting the pack in the **extra** slot lets both stack. The extra slot has no strength native — `_SET_EXTRA_TIMECYCLE_MODIFIER_STRENGTH` in older lists is really `ENABLE_MOON_CYCLE_OVERRIDE` — so strength is baked into the values (or offer `subtle` and `strong` modifiers).

There's also `SetTransitionTimecycleModifier(name, seconds)` for fades, and `PushTimecycleModifier`/`PopTimecycleModifier`.

## Building modifiers at runtime (CFX natives)

From `fivem/ext/native-decls`: `CREATE_TIMECYCLE_MODIFIER(name)`, `CLONE_TIMECYCLE_MODIFIER(source, newName)`, `SET_TIMECYCLE_MODIFIER_VAR(name, var, v1, v2)`, `REMOVE_TIMECYCLE_MODIFIER_VAR`, `GET_TIMECYCLE_MODIFIER_VAR`, `DOES_TIMECYCLE_MODIFIER_HAS_VAR`, `GET_TIMECYCLE_VAR_NAME_BY_INDEX` / `GET_TIMECYCLE_VAR_COUNT` / `GET_TIMECYCLE_VAR_DEFAULT_VALUE_BY_INDEX`, `REMOVE_TIMECYCLE_MODIFIER`. Useful for a live "graphics menu" with sliders: clone the pack's modifier per player, change vars, re-apply. The XML route is simpler for a fixed pack.

## Tuning in game: the TimeCycle Editor

FiveM ships an ImGui editor (`TimecycleEditor.cpp`). It only exists at **pure level 0** — on a pure server it never initialises. On a local dev server with `sv_pureLevel 0`: F8 console → `timecycleeditor true` (or the native `ACTIVATE_TIMECYCLE_EDITOR`). Pick or clone a modifier, change variables live, then **Generate XML** and paste the result into the pack's XML. Tune at several times (noon, sunset, night) and weathers (clear, rain, fog) — a look that's perfect at noon is often too dark at night.

## Variable cheat-sheet (for looks)

Names are from the vanilla list; effects are what the names and editor testing suggest — verify in game.

| Goal | Variables |
|---|---|
| colour tint / white balance | `postfx_correct_col_r`, `_g`, `_b` (1.0 = neutral), `postfx_correct_cutoff` |
| saturation | `postfx_desaturation` (1.0 in every vanilla keyframe; behaves like a saturation multiplier — <1 less colour; **unverified**, test) |
| contrast / exposure | `postfx_exposure`, `postfx_exposure_min`, `postfx_exposure_max`, `postfx_tonemap_filmic_*` (filmic curve, `_bright` / `_dark` variants) |
| bloom | `postfx_intensity_bloom`, `postfx_bright_pass_thresh`, `postfx_bright_pass_thresh_width` |
| vignette | `postfx_vignetting_intensity`, `postfx_vignetting_radius`, `postfx_vignetting_contrast` |
| grain / lens | `postfx_noise`, `postfx_noise_size`, `lens_artefacts_intensity`, `chrom_aberration_coeff` |
| fog / haze | `fog_start`, `fog_density`, `fog_falloff`, `fog_near_col_*`, `fog_col_*`, `fog_haze_density`, `fog_haze_start`, `fog_haze_col_*` |
| sky | `sky_zenith_col_*`, `sky_azimuth_east_col_*` / `_west_col_*`, `sky_sun_col_*`, `sky_hdr`, `sky_sun_hdr` |
| lights | `light_dir_col_*`, `light_dir_mult`, `light_natural_amb_up_*` / `_down_*`, `light_artificial_int_*` / `_ext_*` |
| performance | `shadow_distance_mult`, `lod_mult`, `dof_enable_hq`, `reflection_lod_range_*` |

Grep `assets/timecycle_vars.txt` for exact spellings before writing a variable.

Keep looks to **post-processing** variables when you want them consistent across weather and time: overriding sky or light values with fixed numbers flattens the day-night cycle (a "warm" sky at midnight looks wrong).

## Performance tiers

`make_timecycle_pack.py` adds optional tiers: `low` (`shadow_distance_mult 0.75`, `lod_mult 0.85`, `dof_enable_hq 0`), `medium` (`dof_enable_hq 0`), `high` (look only). These are rules of thumb; measure FPS before and after and say so to the user.

## Weather and time files

`WEATHER_FILE` and `TIME_FILE` exist as `data_file` types, and some packs use them to replace whole weather keyframe files (`w_*.xml`). No reliable success reports were found on Legacy, and they're broken on Enhanced (citizenfx/fivem issue #4240). Prefer modifiers. For changing which weathers run, use a weather sync resource (`qbx_weathersync`, `Renewed-Weathersync`, both GPL-3) or the CFX natives `SET_WEATHER_CYCLE_ENTRY` + `APPLY_WEATHER_CYCLES`.

## Interiors

MLO rooms carry their own timecycle (`SET_INTERIOR_ROOM_TIMECYCLE` / `GET_INTERIOR_ROOM_TIMECYCLE`), so a look applied outside can feel different indoors. Test inside at least one MLO.
