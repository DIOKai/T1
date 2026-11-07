# Tools, workflows A–C (install, clone, new sounds)

Source tags [Sx] → `sources.md`. The skill's own scripts (`sound_pack.ps1`, `revoice_wav.py`, `check_sound_resource.py`) automate workflow B and the checks; see SKILL.md.

## 3. Tools (free vs paid)

- **CodeWalker** (dexyfex) — free; source on GitHub, no LICENSE file in repo (GitHub reports none); bundled Notice.txt: "Copyright(c) 2017-2019 dexyfex" plus MIT notices for third-party code [S2; local Notice.txt]. RPF Explorer: Edit mode, Export XML / Import XML (Ctrl+Ins) for .rel and .awc [S10]; can open .dat151.rel directly in edit mode and search fields (KCMIR0) [S20]. `CodeWalker.Core.dll` is scriptable from PowerShell: `RelFile.Load`, `RelXml.GetXml`, `XmlRel.GetRel`, `AwcFile.Load`, `AwcXml.GetXml(awc, wavFolder)`, `XmlAwc.GetAwc(XmlDocument, inputFolder)` [S1; local siren memory: pass `XmlDocument` via `.PSObject.BaseObject`]. Dev builds come from the CodeWalker Discord [S10].
- **OpenIV** — free download with donations/Patreon; v4.1 (2022-01-18); tagline "ultimate modding tool for GTA V, GTA IV and Max Payne 3" [S17]. Has a GTA V .awc editor (OpenIV Team video "How to edit GTA V audio files in OpenIV (.awc)", 2015-06-20, no narration) [S18]. Used for singleplayer OIV installs and dlclist.xml [S23 02:05–05:00]. Granular grain-table editing in OpenIV: not documented (unverified — assume no).
- **GSTools** (Legacy_DMC) — credited for granular porting in many packs (TheAdmiester, Aquaphobic) [S11][S12]. No public download, documentation or licence found; Legacy_DMC's Gumroad says he made "the first script that allowed custom granular sounds to be ported" [S24]. Treat as NOT available / private (unverified). Legacy_DMC's "Dynamic" docs describe an antilag/gearshift audiobank tool that outputs CodeWalker XML [S25] (product licence/price unknown).
- **AWCMaster** (qyful) — GPL-3.0, Python GUI, makes AWC + XML for CodeWalker to import; last push 2024-09-02; no granular support mentioned [S14].
- **native-audio-tool** (JoeSzymkowiczFiveM) — GPL-3.0, converts audio to .awc + REL XML for script sounds (not granular) [S15].
- **Monkys-Audio-Research** (Monkeypolice188) — dat54/dat151 field research + nametables, no licence shown, updated 2026-09 [S26]. CamxxCore RageAudioTool — C#, ~2017, inactive [S27].
- **FiveM-EngineSound-Simulator** (MushroomFleet) — web parser/simulator; its README's channel mapping ("idle uses channel 0 …") contradicts real data (Channel0 = engine_accel), and its licence is inconsistent (MIT vs Apache) → low reliability [S28].
- Beware `Sachincr2222/GTA-V-Enhanced-AWC-Toolkit`: promotional, invented-looking, not audio ("Advanced Weapon Component") — do not download (search result S29).
- Generic free audio: Audacity is credited for sample work (InfamousSabre "Audacity guidance") [S12]; ffmpeg/Python are fine for EQ/gain on exported WAVs — this skill's `scripts/revoice_wav.py` does it without changing rate or length.
- **Paid**: Legacy_DMC MTPO script (paid, forum) [S24 search]; commercial sound vendors (204 sells via Cfx portal) [S22]; KCMIR0 has a Tebex store [search result]. Not needed for any workflow here.
- **Not free in effect**: there is NO public, documented free tool that turns raw recordings into a GTA granular bank (grain table + loops). See §6.

---

## 4. Workflow A — install an existing community pack as a FiveM resource

1. Download the "FiveM" version; a valid resource has `audioconfig/`, `sfx/`, `fxmanifest.lua` [S21 00:00:44–00:00:54]. Layout (verified locally, all installed packs):
   ```
   <name>/fxmanifest.lua
   <name>/audioconfig/<name>_game.dat151.rel
   <name>/audioconfig/<name>_sounds.dat54.rel
   <name>/audioconfig/<name>_amp.dat10.rel        (only some packs)
   <name>/sfx/dlc_<name>/<name>.awc
   <name>/sfx/dlc_<name>/<name>_npc.awc
   ```
2. Manifest pattern (verified locally, TheAdmiester style):
   ```lua
   fx_version 'cerulean'   -- older packs use 'adamant'; both work
   game 'gta5'
   files { 'audioconfig/*.dat151.rel', 'audioconfig/*.dat54.rel', 'audioconfig/*.dat10.rel', 'sfx/**/*.awc' }
   data_file 'AUDIO_SYNTHDATA' 'audioconfig/<name>_amp.dat'   -- only if the .dat10.rel exists
   data_file 'AUDIO_GAMEDATA'  'audioconfig/<name>_game.dat'
   data_file 'AUDIO_SOUNDDATA' 'audioconfig/<name>_sounds.dat'
   data_file 'AUDIO_WAVEPACK'  'sfx/dlc_<name>'
   ```
   One resource may carry several engines (tamustanggt50 also declares tascmustanggt50) (verified locally). ma-T-o's generic version adds `config/*.dat.rel` to files [S8].
3. Converting a singleplayer pack: copy `config/*.rel` and the `dlc_<name>` folder; file names may differ from the car name (e.g. car1 vs car11) — use the real names [S8].
4. Set `<audioNameHash>` in the car's vehicles.meta to the pack's dat151 car Name [S21][S22].
5. `ensure` the sound resource in server.cfg; 204 says start audio BEFORE the car resources or "your vehicles won't have sound" [S22 00:01:24–00:01:49] (vendor claim, unverified elsewhere).
6. Packs ported from DLC content may need a game build: Aquaphobic's M177 requires "A FiveM server build that supports the Los Santos Tuners assets" [S12] → `sv_enforceGameBuild 2372` (tuner) or later [S30].

Common mistakes:
- Wildcards in `data_file` for audio → silent cars [S5].
- Using `.dat151.rel` in data_file instead of `.dat` (convention in S6/S7, Rockstar content.xml verified locally).
- Wrong/outdated audioNameHash → silent car (Carrera GT pack changed its hash between versions) [search: S31]; folder name not always the hash [S13].
- Missing file referenced in data_file → crash on join [S8].
- Too many add-on audio packs: Cfx issue #2515 (open since 2024-05-11): around 190 sounds/banks the last ones go silent, no errors; `increase_pool_size "AudioHeap"` did not help; contributor gottfriedleibniz notes the game indexes wave packs by only the first eight characters of the name [S32]. FiveM's `PatchAudioWavePackOverlay.cpp` keeps a ref-count per wave-pack name and overlays several resource paths under one `awc:/<name>/` mount, with a comment about the 8-character limit [S33] → keep every `.awc` file name globally unique (e.g. `<audioNameHash>.awc`) because packs whose names share a prefix may be merged into one virtual folder (inferred from S32+S33; the local clones dominatorgrt/hkxx/bs share the prefix "dlc_domi" and use unique awc names — in-game confirmation still pending).
- Restart vs reconnect: forum guides only say restart the resource [S8][S7 `/refresh` + `/start`]; Legacy_DMC's Dynamic docs advise restarting both server and client after new audio banks [S25]; local siren notes say clients must reconnect for audio data. Recommend: after any audio change, restart the resource AND reconnect the client (unverified as strict requirement; safe).

---

## 5. Workflow B — clone/rename a pack into per-car variants

What must be unique per variant (verified locally by diffing tamustanggt50 → dominatorgrt):
- Resource folder, file names: `<new>_game.dat151.rel`, `<new>_sounds.dat54.rel`, (`<new>_amp.dat10.rel`), `sfx/dlc_<new>/<new>.awc`, `<new>_npc.awc`, and the 4 data_file lines.
- dat54 `ContainerPaths` and every `ContainerName` → `dlc_<new>/<new>` and `dlc_<new>/<new>_npc` (e.g. `DLC_dominatorgrt\dominatorgrt`).
- dat151 car item Name = new audioNameHash; its `Engine`/`GranularEngine` references and every other record name that the original pack defined (engine, granular engine, granular sounds, door/ignition/shutdown/startup/pops/dump-valve sounds …) — the earlier clone gave all of them new hashes so two variants can be loaded at the same time without name collisions. Vanilla references (`null_sound`, vanilla horns, collision, scanner hashes that are not defined in the pack) stay unchanged (verified locally: Horns hash unchanged, DoorOpen changed because the pack defines it).
- vehicles.meta `<audioNameHash>` of the target car.
- AWC stream names (`engine_accel` …) stay the same — they are local to the container (verified locally: same names in every pack and vanilla).

Safe audio edits (keep grain tables valid):
- Export each AWC to XML with WAV folder (CodeWalker `AwcXml.GetXml(awc, folder)`), process the mono 16-bit WAVs, re-import with `XmlAwc`. Keep sample rate, sample count and channel count identical (grain offsets are sample positions; CodeWalker does not update `Samples`) [S1; inferred]. No time-stretch, no trim, no resample. Avoid processing that shifts phase/timing heavily (long linear-phase filters introduce delay; prefer minimum-phase EQ or compensate) (inferred).
- Edits used successfully on the user's server variants (see sources.md, installed packs): EQ shelves/peaks (e.g. +3 dB at 110 Hz, +1.5 dB at 450 Hz), tanh saturation for rasp, gain ±1–5 dB per layer, blending a filtered looped real recording into the idle streams, synthesised supercharger whine following the rpm curve (their CREDITS.txt files). Prefer REL volume fields for pure loudness changes (KCMIR0 changes MasterVolume of the granular item [S20 01:13–01:52]) and only touch WAVs for tone.
- After edits watch for clipping: the WAV must stay within full scale (inferred; Headroom field exists in format chunk [S1]).
- Removing pops: set `RevLimiterPopSound` (old `LimiterPops`) and `UpgradedExhaustPops` to `null_sound` (verified locally in yukon62 clone).

---

## 6. Workflow C — new engine sound from recordings (honest limits)

- What Rockstar records (S19 23:54–24:19): one in-gear run idle → top revs, lift off, coast back to idle; ~7 s; separate engine and exhaust mics (exterior suction-cup omni). Cut into idle / accel / decel. Player bank needs 6 streams: engine_accel, exhaust_accel, engine_decel, exhaust_decel, engine_idle, exhaust_idle (verified locally); NPC bank 4 streams (accel + idle) made from loop regions [S19 27:03–27:22].
- Local data confirms accel = rising sweep (grain rate 11.9 → 55.1 /s), decel = falling sweep (52.4 → 12.7 /s), idle = steady (~22.6 /s, 39 grains) (verified locally, Mustang). Streams last ~10–14 s at 30 kHz (299 984 samples) (verified locally).
- Grain cutting: Rockstar uses guided fundamental tracking with known cylinder count, then autocorrelation with zero-crossing bias [S19 24:46–25:09]; loops are designer-marked stable regions [S19 25:14–25:51]. The open-source Unity project Jonas-Hack/Granular-Synthesis-for-Engine-Audio describes the same idea (single idle→max-RPM recording, grains selected by RPM) [S34] but does not output GTA files.
- Free toolchain reality: CodeWalker can WRITE granulargrains/granularloops from XML [S1], so a custom script could in principle generate the grain list (offset, rate, two ushorts) and loops. But the meaning of `UnkUshort1/2` and grains-chunk `UnkFloat1` is undocumented [S1 comments], the rate→RPM mapping and how `GranularClock`/`MinRPMOverride` drive it are undocumented, and the only known working porter (GSTools) is private. → Fully new granular banks from scratch: NOT achievable with documented free tools (as of 2026-11). Realistic free path = re-voice an existing pack whose engine character is close: replace/blend WAV content per stream while keeping grain timing (EQ-match to real recordings, replace idle with a looped real idle of the same length, add whine/rasp), as done on the user's server for yukon62/bisontrx/conqogla1000 (`sources.md`, installed packs). Mark any "from scratch" attempt as experimental.
- Source licensing for recordings: use CC0/CC BY Freesound recordings and credit them (local CREDITS.txt pattern) — see §8.

---

