# Tuning, testing and troubleshooting

Source tags [Sx] → `sources.md`.

## 7. Tuning and testing

Parameters people tweak (field names = master; old name in brackets):
- Loudness: GranularEngine `MasterVolume` (KCMIR0: higher = louder) [S20 01:13–01:52]; `EngineVolume_PostSubmix`/`ExhaustVolume_PostSubmix` [EngineVolume/ExhaustVolume]; `EngineIdleVolume_PostSubmix`/`ExhaustIdleVolume_PostSubmix` [Unk54/Unk55]; dat54 `ChannelVolume0..5` per layer (verified locally). Units presumably 0.01 dB (unverified).
- Directionality ("audio occlusion" in gta5-mods titles = exhaust faint from the front, engine faint from the rear [S13]): `EngineMaxConeAttenuation`/`ExhaustMaxConeAttenuation` (inferred link; S19 26:21–26:29 describes the cone design).
- Pitch range: dat54 `GranularClock` pairs (player AND NPC GranularSound) [S10]; VehicleEngine `MinPitch/MaxPitch`, `IdleMinPitch/IdleMaxPitch` for the loop layers (old Unk09/10, Unk13/14).
- Rev limiter: `RevLimiterGrainsToPlay/ToSkip` [Unk43/44], `RevLimiterApplyType` [Unk58], `RevLimiterVolumeCut` [Unk59], `RevLimiterPopSound` (verified locally values differ per pack). Effect of each value: unverified.
- Turbo/whine: `TurboWhine`, `UpgradedTurboWhine`, `DumpValve`, `MasterTurboVolume`; NA car → set both whine fields to `null_sound` (inferred from local data + S13 complaint).
- Gear change feel: `GearChangeWobble*` [Unk21–28]; CarAudioSettings `AdditionalRevsIncrease/DecreaseSmoothing`, `AdditionalGearChangeSmoothing(Time)` [S1] (effects unverified).
- Startup: `StartupRevsVolumeBoostEngine/Exhaust_PostSubmix` [Unk56/57], CarAudioSettings `StartupRevs`.

A/B testing in game:
- Local dev server only. Edit XML → import with the same CodeWalker version → copy into resource → `refresh` + `ensure <res>` (or restart) → reconnect client (see `workflows.md` §4). Switch quickly between candidates without editing vehicles.meta with `ForceVehicleEngineAudio(veh, 'name')` from a client test command [S16] (local only).
- Load several candidate packs side by side (each with unique names) and compare on the same car.
- Check the F8 console / client log for mount errors (inferred standard practice).

Symptoms → likely causes:
- Silent engine: data_file glob or wrong path [S5]; audioNameHash doesn't match dat151 Name or outdated [S31][S13]; >~190 audio packs [S32]; mixing ContainerName lines from different vehicles in one GranularSound [S9]; audio resource started after the cars (vendor claim) [S22]; dat151 references a SynthPreset but the `_amp.dat10.rel` is not mounted (inferred).
- Car plays the default/stock sound: audioNameHash not changed in the vehicles.meta that the server actually loads [S23 05:02–05:09]; car uses the electric engine line [S9 commenter].
- Crash on join: data_file points to a missing file [S8]; badly packed REL (issue #2496 was the reporter's own REL packing, not FiveM) [S35].
- Crackle/clicks: WAV clipped after gain/saturation; sample count/even-length mismatch after edits (CodeWalker requires even PCM sample counts) [S1]; grain timing destroyed by trim/resample/time-shifting filters (inferred).
- Sound cuts/stutters at high RPM: rev limiter grains settings or limiter pops (inferred); `MaxRPMOverride` (inferred); wave pack name collision (8-char) if awc names are reused (inferred from S32/S33).
- Wrong pitch (too high/low, chipmunk): GranularClock min/max don't match the grain rates in the bank (verified relation locally), sample rate in WAV changed on re-import (CodeWalker takes rate from WAV header [S1]); NPC GranularSound clock not edited [S10].
- Turbo whine on an NA car: TurboWhine/UpgradedTurboWhine set [S13, local data].

---

## 8. Licensing

- gta5-mods pages often have no licence at all (TheAdmiester Mustang page: none) [S11]; others forbid reuploads: Aquaphobic "I do NOT tolerate reuploads without my explicit permission", REL code unencrypted "for personal use" [S12]; Fadilj "I do not allow reuploading of my sound without permission" [S13].
- Most community packs contain audio ripped from commercial games: Mustang 5.0 = Codemasters DIRT Rally 2.0 + Ghost Games NFS Heat + Polyphony GT Sport [S11]; LT1 = Criterion / NFS Unbound (local CREDITS); M177 = Playground Games Forza Horizon 5 [S12]; NSX = Grid 2 [S13]. The pack author cannot grant rights to that audio → do not sell, do not reupload, do not put in a paid/escrowed resource; personal server use only, keep credits (inferred legal reading; not legal advice).
- Freesound recordings: CC0 (no attribution needed) or CC BY 3.0 (attribution required, state changes) — local CREDITS.txt examples (Ears68 CC BY 3.0, jodybruchon / Walking.With.Microphones / itinerantmonk108 / overmedium CC0).
- Tools: CodeWalker no explicit licence for the app (copyright dexyfex) [S2]; AWCMaster and native-audio-tool GPL-3.0 [S14][S15].

---

## 10. Biggest gaps / uncertainties

1. Units of volume (assumed 0.01 dB) and pitch (assumed cents) — no source.
2. Meaning of grain fields `UnkUshort1/2`, grains-chunk `UnkFloat1`, loop `UnkUint1`; how grain rate maps to RPM; what `MinRPMOverride/MaxRPMOverride` do.
3. No public free tool to build granular banks from recordings (GSTools private).
4. Restart vs reconnect for audio changes — no authoritative Cfx doc.
5. The 8-character wave-pack name behaviour — only a contributor comment + a code comment; not tested in game here.
6. Whether add-on audio works the same on FiveM for GTA V Enhanced — not researched.
7. YouTube coverage is install-level only; no tutorial found that explains granular bank creation (searches for "granular engine GTA V tutorial" returned none).

---

