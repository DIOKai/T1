# How GTA V vehicle audio is put together

Source tags [Sx] → `sources.md`. (verified locally) = checked by dumping real packs with CodeWalker.Core; (inferred) = reasoning from data; (unverified) = single weak source.

Contents: §0 CodeWalker version gotcha · §1 record chain and data files · §1.4 field names (new ↔ old CodeWalker) · §2 AWC container

## 0. BIGGEST GOTCHA: CodeWalker XML field names differ by CodeWalker version

- CodeWalker master renamed almost all audio REL fields in 2024 (commits `f5a637588f` 2024-07-17 "PR #230 and #248 with extra audio editing improvements", `880f880c4d` 2024-07-18, `cdda7509a0` 2024-11-19, `35a8dfe7b0`/`ef877c82ad` 2025-04-04 rel fixes) [S1][S2]. Repo HEAD `485d56bec0` 2025-04-11 [S2].
- The widely used build `CodeWalker30_dev46` (DLL dated 2023-12-13, the one on this PC) still writes the OLD names: item types `Vehicle`, `VehicleEngine`, `VehicleEngineGranular`, many `UnkNN` fields (verified locally).
- Current master writes item `type=` from the enum name: `CarAudioSettings` (3), `VehicleEngineAudioSettings` (4), `GranularEngineAudioSettings` (88), `ElectricEngineAudioSettings` (108), `SportsCarRevsSettings` (118), `VehicleCollisionSettings` (1) [S1 RelFile.cs `enum Dat151RelType`, RelXml.GetXml].
- Consequence: XML exported by one CodeWalker version should be re-imported with the SAME version (inferred: tag names differ, so the other version's ReadXml will not find the fields). Tutorials written for old builds use old names (5mods wiki: `UnkVecData` = today's `GranularClock`) [S10].
- The 5mods wiki notes CodeWalker v29 from the public site cannot export .rel to XML; newer dev builds come from the CodeWalker Discord [S10]. KCMIR0 video says use dev44 or newer [S20 00:00:20–00:00:27].

---

## 1. How GTA V vehicle audio is structured

### 1.1 vehicles.meta → dat151
- `<audioNameHash>` in the car's vehicles.meta selects the audio game object; set it to the sound pack's name (e.g. `tamustanggt50`) [S11 TheAdmiester page; S21 00:01:44–00:02:00; S22 00:02:42–00:02:57; S23 00:05:30–00:06:26].
- That name must equal the `<Name>` of the dat151 car item (old CW `type="Vehicle"`, new `CarAudioSettings`) (verified locally: `tamustanggt50_game.dat151.rel` item Name `tamustanggt50`; clones `dominatorgrt` etc. keep only the top-level Name readable, all inner items are new hashes).
- The 204 sound vendor says their resource folder name always equals the audio hash, but warns to read the readme [S22 00:02:17–00:02:26]; a gta5-mods commenter notes the hash name can differ from the file name [S13]. Treat folder name ≠ guarantee; read the dat151 item Name.
- Runtime override for testing: native `ForceVehicleEngineAudio` (`FORCE_USE_AUDIO_GAME_OBJECT`, hash `0x4F0C413926060B38`) sets a vehicle's audio game object by string; it is not replicated and is lost when the vehicle leaves scope; Cfx staff suggested state bags + `AddStateBagChangeHandler` to sync [S16].

### 1.2 FiveM data_file types and files
- Data file keys (Cfx docs table): `AUDIO_GAMEDATA` (example `x64:/audio/audio_rel/config/game.dat151.rel`), `AUDIO_SOUNDDATA` (`.../sounds.dat54.rel`), `AUDIO_SYNTHDATA`, `AUDIO_DYNAMIXDATA`, `AUDIO_CURVEDATA`, `AUDIO_SPEECHDATA` (`.dat4.rel`) — all `audMetadataDataFileMounter` except speech; `AUDIO_WAVEPACK` root = "Folder containing wave packs", mounter `audWavePackDataFileMounter` [S3].
- `data_file` supports globbing in general [S4], BUT for audio keys each file must be declared explicitly ("you have to data_file each item 10,54,151 individually and the dlc_ file") [S5]. Globs in `files {}` are fine (verified locally: TheAdmiester manifests use `'audioconfig/*.dat151.rel'`, `'sfx/**/*.awc'` in files, explicit data_file lines).
- The `.dat` convention: `files{}` lists the real file `xxx_game.dat151.rel`, while `data_file` points to `xxx_game.dat` (no `151.rel`) [S6 einsteinium 2017-06-14; S7 Department_of_Steel 2021-07-22; S8]. Rockstar's own DLC `content.xml` does the same: mptuner `dlc.rpf` content.xml lists `dlc_mpTuner:/%PLATFORM%/audio/dlcTuner_game.dat` (AUDIO_GAMEDATA), `dlcTuner_sounds.dat` (AUDIO_SOUNDDATA), `dlcTuner_amp.dat` (AUDIO_SYNTHDATA), `dlcTuner_mix.dat` (AUDIO_DYNAMIXDATA), `audio/sfx/dlc_Tuner` (AUDIO_WAVEPACK), while the archive holds `dlctuner_game.dat151.rel` + `dlctuner_game.dat151.nametable`, `dlctuner_amp.dat10.rel`, `dlctuner_mix.dat15.rel`, `dlctuner_sounds.dat54.rel` (verified locally, read-only from `G:\...\Grand Theft Auto V`). So the mounter appends the type number + `.rel` itself (inferred from that pattern).
- Mapping: `.dat151.rel` → AUDIO_GAMEDATA, `.dat54.rel` → AUDIO_SOUNDDATA [S7], `.dat10.rel` → AUDIO_SYNTHDATA (verified locally: Hellcat/bisontrx/dghmieng manifests `data_file 'AUDIO_SYNTHDATA' 'audioconfig/<name>_amp.dat'`; matches vanilla `dlcTuner_amp.dat`).
- `.nametable` files: vanilla ships them next to each .rel (verified locally); einsteinium's 2017 example lists one in `files` [S6]; none of the installed community FiveM packs ship one and they load (verified locally) — so optional for add-ons (inferred). Note: inside a dat54 the container (wave bank) paths are stored in the REL itself; CodeWalker XML shows them as `<ContainerPaths>` [S1 RelXml.GetXml] (verified locally: `DLC_tamustanggt50\tamustanggt50`, `DLC_tamustanggt50\tamustanggt50_npc`).
- A missing file referenced by data_file can crash the client on join (ma-T-o, 2023-08-19) [S8].

### 1.3 Record chain for one granular car (verified locally on tamustanggt50 + vanilla calico)
```
vehicles.meta audioNameHash = NAME
dat151  CarAudioSettings  NAME
          ├─ Engine         → VehicleEngineAudioSettings  NAME_engine   (loop-based layers, turbo, transmission, ignition, shutdown, pops)
          └─ GranularEngine → GranularEngineAudioSettings NAME_granular_engine
                                ├─ EngineAccel / ExhaustAccel        → dat54 GranularSound / EnvironmentSound
                                ├─ NPCEngineAccel / NPCExhaustAccel  → dat54 GranularSound using the _npc bank
                                ├─ EngineSynthPreset / ExhaustSynthPreset → dat10 SynthPreset (AUDIO_SYNTHDATA)
                                └─ RevLimiterPopSound / UpgradedRevLimiterPop → dat54 sounds
dat54   GranularSound NAME_engine_accel: 6 channels → container "dlc_NAME/NAME" files engine_accel, exhaust_accel, engine_decel, exhaust_decel, engine_idle, exhaust_idle
        EnvironmentSound NAME_exhaust_accel: ChannelID 1 (taps the exhaust output buffer of the granular sound)
        GranularSound (NPC): container dlc_NAME/NAME_npc, only accel + idle channels (Channel2/3 = "0"/empty), ParentSound = NAME_engine_accel
awc     sfx/dlc_NAME/NAME.awc (player bank) + NAME_npc.awc (NPC bank)
```
- `CarAudioSettings` also has `ElectricEngine` and `EngineType`; some cars use the electric engine line instead of granular [S9 commenter; S1]. (Local note: Dominator EV keeps vanilla `voltic` — `ElectricEngineAudioSettings` named `voltic_electric_engine` per CodeWalker enum comment [S1].)
- `AlternativeGranularEngines` + `AlternativeGranularEngineProbability` exist on CarAudioSettings [S1] (purpose unverified).

### 1.4 Real field names (CodeWalker master, RelFile.cs) and old dev46 names
Mapping old→new is by binary field order (both read the same bytes in the same order) (inferred, high confidence; old values checked against the dev46 dumps). Volumes look like 1/100 dB and pitches like cents (unverified — no source states units; consistent with local yukon62 clone where ExhaustVolume 800→300 was logged as "-5 dB", and MinPitch -1200 = -1 octave).

GranularEngineAudioSettings (master) [S1 class Dat151GranularEngineAudioSettings] — `old dev46 name` in brackets, Mustang value:
- Flags, MasterVolume [MasterVolume, 1500], EngineAccel, ExhaustAccel
- EngineVolume_PreSubmix, ExhaustVolume_PreSubmix, AccelVolume_PreSubmix, DecelVolume_PreSubmix, IdleVolume_PreSubmix, EngineRevsVolume_PreSubmix, ExhaustRevsVolume_PreSubmix, EngineThrottleVolume_PreSubmix, ExhaustThrottleVolume_PreSubmix [Unk04–Unk12, all 0]
- EngineVolume_PostSubmix [EngineVolume 400], ExhaustVolume_PostSubmix [ExhaustVolume 800]
- EngineMaxConeAttenuation [**EngineIdleVolume** -100 — misnamed in old builds!], ExhaustMaxConeAttenuation [**ExhaustIdleVolume** -100]
- EngineRevsVolume_PostSubmix [Unk17 300], ExhaustRevsVolume_PostSubmix [Unk18 100], EngineThrottleVolume_PostSubmix [EngineAccelVolume 0], ExhaustThrottleVolume_PostSubmix [ExhaustAccelVolume 100]
- GearChangeWobbleLength [Unk21 30], GearChangeWobbleLengthVariance, GearChangeWobbleSpeed, …SpeedVariance, …Pitch, …PitchVariance, …Volume, …VolumeVariance [Unk22–Unk28 floats]
- EngineClutchAttenuation_PostSubmix, ExhaustClutchAttenuation_PostSubmix [Unk29, Unk30]
- EngineSynthDef, EngineSynthPreset, ExhaustSynthDef, ExhaustSynthPreset [EngineSubmix, EngineSubmixPreset, ExhaustSubmix, ExhaustSubmixPreset] — Hellcat's `EngineSubmixPreset hash_C7406224` is the Name of the SynthPreset in its `_amp.dat10.rel` (verified locally) → this is why some packs need AUDIO_SYNTHDATA.
- NPCEngineAccel, NPCExhaustAccel [EngineAccelNPC, ExhaustAccelNPC], RevLimiterPopSound [LimiterPops]
- MinRPMOverride, MaxRPMOverride [Unk38, Unk39 = 0]
- EngineSubmixVoice, ExhaustSubmixVoice [Unk40, Unk41], ExhaustProximityVolume_PostSubmix [Unk42 600]
- RevLimiterGrainsToPlay [Unk43 4; Hellcat 3], RevLimiterGrainsToSkip [Unk44 2]
- SynchronisedSynth [IdleSub], UpgradedEngineVolumeBoost_PostSubmix, UpgradedEngineSynthDef/Preset, UpgradedExhaustVolumeBoost_PostSubmix, UpgradedExhaustSynthDef/Preset [Unk46–Unk51], DamageSynthHashList [EngineDamage], UpgradedRevLimiterPop [LimiterPopsUpgraded]
- EngineIdleVolume_PostSubmix, ExhaustIdleVolume_PostSubmix [Unk54, Unk55 — these are the REAL idle volumes]
- StartupRevsVolumeBoostEngine_PostSubmix, StartupRevsVolumeBoostExhaust_PostSubmix [Unk56, Unk57 = 500]
- RevLimiterApplyType [Unk58: Mustang 1, calico 2], RevLimiterVolumeCut [Unk59 0.2] — optional trailing 8 bytes (read only if present) [S1]

VehicleEngineAudioSettings (master) [S1 class Dat151VehicleEngineAudioSettings] — old names in brackets:
MasterVolume, MaxConeAttenuation [EngineLowVolume], FXCompensation [EngineHighVolume], NonPlayerFXComp [EngineNPCVolume], LowEngineLoop/HighEngineLoop/LowExhaustLoop/HighExhaustLoop [EngineLow/EngineHigh/ExhaustLow/ExhaustHigh], RevsOffLoop, MinPitch/MaxPitch [Unk09 -1200 / Unk10 1400], IdleEngineSimpleLoop/IdleExhaustSimpleLoop, IdleMinPitch/IdleMaxPitch [Unk13/Unk14], InductionLoop [AirIntake] + InductionMinPitch/MaxPitch, TurboWhine [Turbo] + TurboMinPitch/TurboMaxPitch [**EngineLowPitch/EngineHighPitch** — misnamed in old builds], DumpValve, DumpValveProb, TurboSpinupSpeed, GearTransLoop [Transmission] + GearTransMinPitch/MaxPitch, GTThrottleVol, Ignition, EngineShutdown [ShutDown], CoolingFan, ExhaustPops, StartLoop [DistantStart], MasterTurboVolume [Unk33], MasterTransmissionVolume [GearStickVolume], EngineStartUp [StartupMaster], Engine/ExhaustSynthDef/Preset, Engine/ExhaustSubmixVoice, UpgradedTransmissionVolumeBoost [Unk42], UpgradedGearChangeInt/Ext, Upgraded* boosts, UpgradedDumpValve, UpgradedTurboVolumeBoost [DumpValveUpgradedVolume 3000], UpgradedGearTransLoop, UpgradedTurboWhine [TurboUpgraded], UpgradedInductionLoop, UpgradedExhaustPops.
- Turbo behaviour (verified locally): Mustang has `Turbo null_sound` but `TurboUpgraded` set → whine only with the turbo mod upgrade (matches TheAdmiester "turbo sounds … when a turbo upgrade is added" [S11]). A gta5-mods commenter complained an NA pack still spooled [S13] → check both TurboWhine and UpgradedTurboWhine.

CarAudioSettings (master) fields [S1]: Flags, Engine, GranularEngine, HornSounds, Door/Boot sounds, … VehicleCollisions, ScannerVehicleSettings, …, StartupRevs, …, SirenSounds, AlternativeGranularEngines, AlternativeGranularEngineProbability, …, EngineType, ElectricEngine, Openness, …, CarSpecificShutdownSound, AdditionalRevsIncreaseSmoothing, AdditionalRevsDecreaseSmoothing, AdditionalGearChangeSmoothing, AdditionalGearChangeSmoothingTime, CabinToneLoop, InteriorViewEngineOpenness, … (old dev46: `EngineGranular`, `Horns`, `TrunkOpen`, `Collision`, `PoliceScannerParams`, `StartupSequence`, `InteriorTones`, many Unk).

dat54 GranularSound (master) [S1 class Dat54GranularSound, Dat54GranularSoundFile, Dat54GranularSoundData]:
- `WaveSlotIndex`, `Channel0..5` each {`ContainerName`, `FileName`}, `ChannelSettings0..5` each {`OutputBuffer`, `GranularClockIndex`, `StretchToMinPitch`, `StretchToMaxPitch`, `MaxLoopProportion`} (old dev46: `UnkFlags0`, `UnkFlags1`, `UnkByte0`, `UnkByte1`, `UnkFloat`), `LoopRandomisationChangeRate`, `LoopRandomisationPitchFraction` (old `UnkFloat0` 0.01, `UnkFloat1` 0.05), `ChannelVolume0..5`, `ParentSound`, `GranularClock` (Vector2 list; old 5mods name `UnkVecData`).
- Mustang values (verified locally): channels 0..5 = engine_accel, exhaust_accel, engine_decel, exhaust_decel, engine_idle, exhaust_idle; OutputBuffer 0/1/0/1/0/1 (engine/exhaust); GranularClockIndex 0/0/0/0/1/1 (idle uses clock 1); MaxLoopProportion 0.5 for accel, 1 otherwise; ChannelVolume -250/100/-600/700/-1250/1900; GranularClock `11.8, 55.7` and `22.7, 22.7`. Vanilla calico: `8.62, 50` / `6.5, 6.5`.
- 5mods wiki: first pair = min (left) / max (right) pitch for engine+exhaust, second pair = idle pitch; edit both player and NPC GranularSound [S10]. Locally the first pair equals the min/max of the per-grain rate in the accel bank (11.9…55.1 Hz vs clock 11.8/55.7) and the idle pair equals the idle grains (≈22.66) (verified locally). Conversion of this number to RPM is NOT documented (unverified; it is grains per second, see §2).
- Pitch per dat54 header: `Pitch`, `LPFCutoff`, `VolumeCurveScale` … (verified locally in XML).

---

## 2. The AWC wave container

- Chunk types (last byte of a name hash) [S1 AwcFile.cs `enum AwcChunkType`]: `data`, `format`, `animation`, `peak`, `mid`, `gesture`, `granulargrains` (0xE787895A), `granularloops` (0x252C20D9), `markers` (0xD4CB98BD), `streamformat`, `seektable`.
- Stream id = `JenkHash(name) & 0x1FFFFFFF` (29 bits), top 3 bits = chunk count [S1 AwcStreamInfo.Read/Write]. Matches siren work notes (joaat & 0x1FFFFFFF) [local memory police-siren-tones.md]. Example: `engine_accel` → 0x1F7402AA (computed with CodeWalker JenkHash, verified locally).
- Codecs: `PCM = 0`, `ADPCM = 4` [S1 enum AwcCodecType]. All installed packs and vanilla calico: PCM only (verified locally).
- format chunk XML: `Codec`, `Samples`, `SampleRate`, `Headroom`, `PlayBegin`, `PlayEnd`, `LoopBegin`, `LoopEnd`, `LoopPoint`, `Peak` [S1 AwcFormatChunk.WriteXml; verified locally]. Granular streams have LoopPoint -1 (verified locally).
- granulargrains chunk: `UnkFloat1` + list of grains, each `UnkUint1` (sample offset), `UnkFloat1`, `UnkUshort1`, `UnkUshort2` — CodeWalker itself labels them "sample offset? / duration..? rpm..? / peak low? / peak high?" [S1 AwcGranularGrainsChunk]. Locally: offset delta 2521 samples at 30 kHz ↔ float 11.9 → float = sampleRate / grain length = grains per second (verified arithmetic, meaning inferred). UnkUshort1 rises monotonically with the rate (170 → 16679) (meaning unknown).
- granularloops chunk: list of loops, each `UnkUint1` (=2, CodeWalker comment `style="walk"?`), `GrainCount`, `Identifier` (default 0x4c633d07 "loop"), `Grains[]` (grain indices) [S1 AwcGranularLoopsChunk]. Mustang engine_accel: 331 grains, 6 loops of 55 consecutive grains; engine_idle: 39 grains, 1 loop (verified locally).
- Per pack, each granular stream has chunks `peak data granulargrains granularloops format` (verified locally). Main bank also holds ~8–24 one-shot PCM streams (startup, shutdown, pops, etc.) at mixed rates 30k/32k/44.1k/48k (verified locally: Mustang 26 streams, Hellcat 25, Redeye 28, calico 30). NPC bank holds 4 granular streams (engine/exhaust accel + idle) (verified locally).
- Rockstar design (GDC 2014, Alastair MacGregor) [S19]: record in-gear run idle → top revs, lift off, coast to idle, cut into idle / acceleration / deceleration, aim ~7 s, 2nd gear usually (1st for diesel) [23:54–24:19]; pipeline: guided fundamental-frequency/RPM detection (designer picks the fundamental, tells the tool the cylinder count) → autocorrelation with bias to zero crossings to cut grains → designer marks up "loop" regions with no cam change/pops for steady-state RPM; runtime pitch-corrects, randomises, blends the two adjacent loops with pure granular data [24:43–25:51]; optional discard of a % of grains to shrink assets [25:51–26:09]; separate engine and exhaust granular synths (cone engine front, exhaust back; mix-and-match engines/exhausts) [26:11–26:46]; NPC engines use only the loop data in a separate bank (subset of player data → seamless switch) [27:03–27:22]; oscillators synced to multiples of the granular clock for sub-harmonic sweeteners, then real-time DSP post-processing for upgrades [27:24–27:54]; single accel and single decel asset per car, wish for throttle layers [49:31–49:57]; one player slot + ~6–7 NPC slots streamed [50:34–50:45]. GTA IV was loop-based, V granular [23:15–23:23].
- Sample rates seen: Mustang 5.0 granular 30000 Hz (all 6); LT1 accel/decel 30000 Hz but idle 48000 Hz; Hellcat, Redeye, vanilla calico 32000 Hz (verified locally). Rates can differ per stream inside one pack (verified locally).
- WAV import (CodeWalker master `AwcStream.ParseWavFile`) [S1]: only PCM (`"Only PCM format .wav files supported!"`) and only mono (`"Only mono .wav files supported!"`), 16-bit assumed; sample rate is taken from the WAV header; `Samples` is NOT updated from the WAV (assignment commented out) → keep the XML sample count = WAV length; PCM data chunks must have an even number of samples (ADPCM: multiple of 8) or encryption throws [S1 around "Unable to encrypt data chunk"]. Peak chunk is read from XML, not recomputed (inferred from code: AwcPeakChunk reads its data from XML).
- Grain offsets are in samples, so resampling or trimming a granular WAV invalidates the grain/loop tables (inferred). Keep rate and length identical when editing.

---

