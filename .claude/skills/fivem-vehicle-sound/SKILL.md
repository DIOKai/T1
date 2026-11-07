---
name: fivem-vehicle-sound
description: Use when a GTA V / FiveM car needs its own engine sound — installing a downloaded engine-sound pack as an add-on resource, giving several cars distinct variants of one pack (clone, rename, deeper/raspier/quieter exhaust), re-voicing a pack with real recordings, tuning volume, idle, rev limiter, pops or turbo whine, or when a car is silent, plays the stock sound, crackles, has the wrong pitch, or clients crash after adding a sound. Also for 声浪, 引擎声, 换声浪, 排气声, 回火, 涡轮声, 车没声音, audioNameHash, dat151, dat54, awc, granular.
---

# FiveM vehicle engine sound

A car's sound is a chain: `vehicles.meta <audioNameHash>` → a dat151 **car** record of that name → engine + **granular engine** records → dat54 sounds → two wave banks (`<name>.awc` for the player, `<name>_npc.awc` for NPCs). GTA V uses **granular** synthesis: each bank stream (`engine_accel`, `exhaust_accel`, `engine_decel`, `exhaust_decel`, `engine_idle`, `exhaust_idle`) carries a grain table of sample positions. Everything below follows from that.

## Pick the route

| Goal | Route | Effort |
|---|---|---|
| "Sounds like some GTA car" | set `audioNameHash` to that vanilla car | minutes |
| Use a downloaded pack | **A** install it as its own resource (`references/workflows.md` §4) | minutes |
| Several cars, one pack, each slightly different | **B** clone + rename with `scripts/sound_pack.ps1 clone` | ~15 min per variant |
| Change the tone (deeper, raspier, quieter, real idle) | **B** + `scripts/revoice_wav.py` on the exported WAVs | ~30 min |
| Brand-new sound from your own recordings | **C** — not possible with documented free tools; re-voice the closest pack instead (`workflows.md` §6) | — |

Prefer REL volume fields for pure loudness changes; touch WAVs only for tone.

## Workflow B (clone, optionally re-voice)

Needs only CodeWalker (free; the folder with `CodeWalker.Core.dll`) and Python. Ask before running anything on the user's PC, work on copies, never edit the installed pack. `scripts/…` below means this skill's folder (installed at `~/.claude/skills/fivem-vehicle-sound/scripts/`, Codex `~/.codex/skills/…`) — pass the full path.

1. **Look at the pack:** `powershell -ExecutionPolicy Bypass -File scripts/sound_pack.ps1 dump -CodeWalker <CW folder> -Res <pack> -Out <work>\dump -Wav`. `streams.txt` in each WAV folder lists every stream with rate, length and whether it is **GRANULAR** (6 player + 4 NPC streams).
2. **Re-voice (optional):** `py -3 scripts/revoice_wav.py <work>\dump\<pack> <work>\edited\<pack> --only "exhaust_*" --preset deeper` (presets `deeper`, `raspier`, `straight-pipe`, `muffled`, or `--low-shelf/--peak/--high-shelf/--drive/--gain`). It keeps the sample rate and every sample, and lowers gain instead of clipping. Never trim, time-stretch, resample or use long linear-phase filters on granular streams.
3. **Clone:** `... sound_pack.ps1 clone -CodeWalker <CW> -Res <pack> -NewName <newname> -Out <work>\out [-WavDir <work>\edited]`. It renames the car record, every record the pack defines (including references held in attributes, e.g. RandomizedSound variations), the wave-bank container names and the files, rebuilds edited banks, writes `fxmanifest.lua` + `CREDITS.txt`, and verifies no source name is left. Use `-Engine` for packs with several engines (e.g. `tascmustanggt50` inside `tamustanggt50`).
4. Fill in `CREDITS.txt` (original author, link, licence text), put the resource next to the cars, set `<audioNameHash><newname></audioNameHash>`, `ensure` the sound **before** the car.
5. **Check:** `py -3 scripts/check_sound_resource.py <resources folder>` (read-only; point it at all sound **and** car resources so it can match them).
6. **Test on the local test server only:** restart the resource and **reconnect** the client (audio data is loaded on join). For quick A/B without editing meta, `ForceVehicleEngineAudio(veh, '<name>')` from a local test command (not synced to other players).

## Rules that bite

- **Same CodeWalker build for every XML round trip.** CodeWalker renamed almost every audio field in 2024 (`Vehicle` → `CarAudioSettings`, `VehicleEngineGranular` → `GranularEngineAudioSettings`, many `UnkNN`); old and new XML don't mix. Some old names are wrong (old `EngineIdleVolume` is really cone attenuation). Table: `references/audio-structure.md` §1.4.
- **`data_file` for audio: one explicit line per file, no globs** (globs → silent car); point it at `xxx_game.dat` while the file is `xxx_game.dat151.rel` (Rockstar's content.xml does the same); globs are fine inside `files {}`.
- A `data_file` pointing at a missing file can crash clients on join.
- Keep every `.awc` name unique server-wide; FiveM indexes wave packs by their first 8 characters, and around 190 add-on banks the last ones go silent (cfx issue #2515).
- CodeWalker imports only mono 16-bit PCM WAV and does not update the sample count — a changed length silently breaks the grain table (`sound_pack.ps1` refuses it).
- Units of volume (≈ 0.01 dB) and pitch (≈ cents) are inferred, not documented — change in small steps and listen.

## Checks before calling it done

- `check_sound_resource.py` shows no errors; `PACK_UNUSED` means a pack was made for a car whose meta still points elsewhere.
- In game: idle, full-throttle pull through the gears, lift-off, rev limiter, reverse, NPC traffic with the same car, two players at once, after a reconnect.
- Credits kept; nothing re-uploaded or sold.

## Common mistakes

| Symptom | Cause → fix |
|---|---|
| Car silent | glob in audio `data_file`; `audioNameHash` ≠ dat151 car name; sound resource started after the car; `_amp.dat10.rel` referenced but not mounted |
| Stock/default sound | edited a `vehicles.meta` the server doesn't load; electric-engine car |
| Clone plays the original pack (or nothing) | container names not renamed — clone with `sound_pack.ps1`, not by hand-renaming files |
| Crackles/clicks | clipped after gain/saturation; odd sample count; grain timing destroyed |
| Chipmunk / wrong pitch | `GranularClock` (player **and** NPC sound) doesn't match the grain rates; WAV resampled |
| Turbo whine on an NA engine | `TurboWhine` / `UpgradedTurboWhine` set → `null_sound` |
| Crash on join | `data_file` points at a missing file |

More: `references/tuning-and-troubleshooting.md`.

## Licensing

Most community packs contain audio ripped from commercial games (DIRT Rally, NFS, Forza, Gran Turismo); the pack author cannot license it. Own server only, keep credits, never re-upload, sell or escrow. Freesound CC0/CC BY recordings are fine with attribution. Paid sound packs and paid porting tools are not needed for any route here.

## References

- `references/audio-structure.md` — record chain, data-file types, field names new ↔ old CodeWalker, AWC format and grains.
- `references/workflows.md` — free/paid tools, workflow A install, B clone/rename, C recordings (honest limits).
- `references/tuning-and-troubleshooting.md` — what each parameter changes, A/B testing, symptom → cause, open questions.
- `references/sources.md` — CodeWalker source, Cfx docs/issues/forum, Rockstar GDC talk, pack pages, videos; what the user's installed packs showed.
- `scripts/sound_pack.ps1` (dump/clone, CodeWalker.Core), `scripts/revoice_wav.py` (EQ/saturation/gain, length-safe), `scripts/check_sound_resource.py` (read-only checker), `scripts/test_scripts.py`.

Related: `fivem-vehicle-mod` (the car resource, `audioNameHash`), `fivem-audio-package-check` (generic audio packaging), `audio-loop-editing` and `audio-quality-check` (preparing real recordings), `ffmpeg-skill`.
