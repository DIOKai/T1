# Sources


- [S1] CodeWalker source, master: `CodeWalker.Core/GameFiles/FileTypes/RelFile.cs` (enum Dat151RelType; classes Dat151CarAudioSettings, Dat151VehicleEngineAudioSettings, Dat151GranularEngineAudioSettings, Dat54GranularSound, Dat54GranularSoundFile, Dat54GranularSoundData; RelXml.GetXml) and `AwcFile.cs` (AwcChunkType, AwcCodecType, AwcStreamInfo, AwcFormatChunk, AwcGranularGrainsChunk, AwcGranularLoopsChunk, AwcMarkersChunk, AwcStream.ParseWavFile, AwcXml/XmlAwc). https://github.com/dexyfex/CodeWalker/tree/master/CodeWalker.Core/GameFiles/FileTypes (fetched 2026-11-08, HEAD 485d56bec0)
- [S2] GitHub API: commit history of RelFile.cs and repo info, https://api.github.com/repos/dexyfex/CodeWalker/commits?path=CodeWalker.Core/GameFiles/FileTypes/RelFile.cs ; README https://github.com/dexyfex/CodeWalker
- [S3] Cfx docs, Data files: https://docs.fivem.net/docs/game-references/data-files/
- [S4] Cfx docs, Resource manifest (data_file, globbing): https://docs.fivem.net/docs/scripting-reference/resource-manifest/
- [S5] Cfx forum "Audio file globbing does not seem to work" (BrianTU, 2022-05-03): https://forum.cfx.re/t/audio-file-globbing-does-not-seem-to-work/4844752
- [S6] Cfx forum "Ability to stream more than model and meta files" #6 (einsteinium, 2017-06-14): https://forum.cfx.re/t/ability-to-stream-more-than-model-and-meta-files/25137/6
- [S7] Cfx forum "[HOW-TO] [QUICK TUTORIAL] How to use custom sounds?" (Department_of_Steel, 2021-07-22): https://forum.cfx.re/t/how-to-quick-tutorial-how-to-use-custom-sounds/4059006
- [S8] Cfx forum "How do i pack singleplayer custom car sounds…" (ma-T-o, 2023-08-19): https://forum.cfx.re/t/how-do-i-pack-singleplayer-custom-car-sounds-in-a-way-i-can-use-them-on-the-server/5155150
- [S9] 5mods wiki "How to increase/decrease the volume of vehicle engines (without editing the .awc)" (actually swapping; ContainerName mixing → silent; electric engine line): https://github.com/5mods/tutorials/wiki/How-to-increase-decrease-the-volume-of-vehicle-engines-(without-editing-the-'.awc'-audio-files)
- [S10] 5mods wiki "How to change the pitch frequency of a vehicle's engine (min, max & idle)" (edited 2024-01-15): https://github.com/5mods/tutorials/wiki/How-to-change-the-pitch-frequency-of-a-vehicle's-engine-(min,-max-&-idle)
- [S11] gta5-mods, TheAdmiester "Ford Mustang GT 5.0 Engine Sound Pack [OIV Add-On | FiveM]" v1.01 (2022-02-13): https://www.gta5-mods.com/vehicles/ford-mustang-gt-5-0-engine-sound-pack-oiv-add-on-fivem
- [S12] gta5-mods, Aquaphobic "Mercedes AMG 63 M177 4.0L V8 Engine Sound" v2.0 (2023-12-11): https://www.gta5-mods.com/vehicles/mercedes-amg-63-m177-v8-engine-sound-oiv-add-on-fivem
- [S13] gta5-mods, Fadilj "Honda NSX C30A Engine Sound … Audio Occlusion" (2024-07-16): https://gta5-mods.com/vehicles/honda-c30a-engine-sound-oiv-add-on-fivem-sound-audio-occlusion
- [S14] AWCMaster (GPL-3.0): https://github.com/qyful/AWCMaster
- [S15] native-audio-tool (GPL-3.0): https://github.com/JoeSzymkowiczFiveM/native-audio-tool
- [S16] Cfx forum "Sync/Replicate ForceEngineAudio() on vehicles" (2022-06): https://forum.cfx.re/t/sync-replicate-forceengineaudio-on-vehicles/4863996 ; native https://docs.fivem.net/natives/?_0x4F0C413926060B38
- [S17] OpenIV homepage: https://openiv.com/
- [S18] YouTube ymLrNTjGBXA "How to edit GTA V audio files in OpenIV (.awc)", OpenIV Team, 2015-06-20 (no speech)
- [S19] YouTube PqPaP_09Pwg "The Sound of Grand Theft Auto V" (GDC 2014 talk by Alastair MacGregor, Rockstar North; uploaded by RockstarNexus), auto-captions; timestamps cited inline
- [S20] YouTube uchjuXbyAww "How to change the volume of Vehicles Sound Mods in GTA 5 and FiveM", KCMIR0 [00:00:16–00:02:45]
- [S21] YouTube hGvVtjpVYEA "Adding Custom Engine Sounds To Your Fivem Server", HighKey Roleplay [00:00:44–00:02:21]
- [S22] YouTube QgLAOvhVElM "How To Install Add On Engine Sounds for FiveM Cars", w204dude (204, paid vendor) [00:00:44–00:03:07]
- [S23] YouTube Mysfl0RPFqQ "How to Add Real Engine Sounds | GTA V Modding", ZED (singleplayer OIV/dlclist) [00:02:05–00:06:30]
- [S24] Legacy_DMC Gumroad: https://legacydmc.gumroad.com (via search snippet; page is JS-rendered)
- [S25] Legacy_DMC Dynamic docs "Creating Gearshift Audiobanks": https://legacydmc.gitbook.io/dynamic/creating-gearshift-audiobanks
- [S26] Monkys-Audio-Research: https://github.com/Monkeypolice188/Monkys-Audio-Research
- [S27] CamxxCore GitHub (RageAudioTool): https://github.com/camxxcore
- [S28] FiveM-EngineSound-Simulator: https://github.com/MushroomFleet/Fivem-EngineSound-Simulator
- [S29] (warning only) https://github.com/Sachincr2222/GTA-V-Enhanced-AWC-Toolkit
- [S30] Cfx docs server commands, sv_enforceGameBuild list (2372 = tuner/mptuner Los Santos Tuners): https://docs.fivem.net/docs/server-manual/server-commands/
- [S31] gta5-mods Carrera GT V10 sound comments (hash changed between versions; via search snippet): https://www.gta5-mods.com/vehicles/pfister-carrera-gt-v10-engine-sound-add-on-fivem-sound
- [S32] citizenfx/fivem issue #2515 "Addon Audio Limiter" (opened 2024-05-11, open): https://github.com/citizenfx/fivem/issues/2515
- [S33] citizenfx/fivem `code/components/gta-core-five/src/PatchAudioWavePackOverlay.cpp` (AddWavePack/RemoveWavePack, base pack list incl. STREAMED_VEHICLES_GRANULAR(_NPC)): https://github.com/citizenfx/fivem/blob/master/code/components/gta-core-five/src/PatchAudioWavePackOverlay.cpp
- [S34] Jonas-Hack/Granular-Synthesis-for-Engine-Audio (Unity): https://github.com/Jonas-Hack/Granular-Synthesis-for-Engine-Audio
- [S35] citizenfx/fivem issue #2496 "game.dat151.rel streaming incorrectly" (closed 2024-07-17, reporter's own packing error): https://github.com/citizenfx/fivem/issues/2496
- Local: `H:\FiveM\mods\police\car\Mustang\改动记录.md` §声浪; `H:\FiveM\mods\police\car\sound\**\fxmanifest.lua`, `CREDITS.txt`; vanilla `G:\SteamLibrary\steamapps\common\Grand Theft Auto V\...\mptuner\dlc.rpf` (content.xml, dlctuner_*.rel, calico*.awc) read via CodeWalker.Core; `C:\Users\Owner\.claude\projects\H--FiveM\memory\police-siren-tones.md`.

## What the user's installed packs showed (2026-11-08)


Source packs kept next to the resources (.rar/.zip from gta5-mods) and A/B preview mp3s (`试听*.mp3`, `对比_*.mp3`), plus `freesound\` folders with CREDITS.txt (CC0/CC BY).

| resource | base | files | notes |
|---|---|---|---|
| tamustanggt50 (+ tascmustanggt50 in same resource) | TheAdmiester Mustang 5.0 v1.01, 1:1 | game/sounds rel, 2 awc each | fx_version 'adamant'; globbed files; 30 kHz granular |
| dominatorgrt / dominatorhkxx / dominatorbs | clones of tamustanggt50 | game/sounds rel + `<n>.awc`, `<n>_npc.awc` | EQ/saturation/gain variants; all inner records renamed; awc size ≈ base |
| ta183lt1 | TheAdmiester LT1 | game/sounds rel | accel/decel 30 kHz, idle 48 kHz |
| yukon62, vigerozx, vigerohornet | clones of ta183lt1 | | yukon62: ExhaustVolume 800→300, LimiterPops & ExhaustPopsUpgraded → null_sound, idle replaced by CC0 Escalade idle; vigerozx: synthesised supercharger whine; vigerohornet: +3 dB @110 Hz, +1.5 dB @450 Hz, tanh rasp |
| dchallengerhellcat, dghmieng | Hellcat packs | + `_amp.dat10.rel` (AUDIO_SYNTHDATA) | 32 kHz |
| lg81hcredeye | Redeye pack | game/sounds (manifest also declares _amp though no dat10 file present → check) | 32 kHz |
| conqredeye, conqogla1000 | clones of lg81hcredeye + Aquaphobic Charger whine curve | | ogla1000 idle blends CC BY 3.0 Ears68 recording |
| bisontrx | clone of dchallengerhellcat | + amp.dat10 | idle rebuilt from Freesound (CC BY + CC0) |
| tacumminsb | TheAdmiester Cummins | game/sounds | diesel |

Manifest patterns observed: (a) TheAdmiester/'adamant': globbed `files`, explicit data_file; (b) local clones/'cerulean': explicit file list + comment header + CREDITS.txt with base pack URL, original credits, list of changes, "For use on this server only". No `.nametable`, no `stream/` folder. Clone awc sizes are within a few bytes of the base (dominatorgrt.awc 4 012 882 B vs tamustanggt50.awc 4 012 896 B; same stream count) → rate and length preserved.
Possible issue to check: `lg81hcredeye/fxmanifest.lua` declares `data_file "AUDIO_SYNTHDATA" "audioconfig/lg81hcredeye_amp.dat"` but there is no `lg81hcredeye_amp.dat10.rel` in the folder (only game + sounds). Per S8 a missing referenced file can crash on join — worth verifying (it apparently runs on the server now; maybe FiveM tolerates it). Same for `dghmieng` — it does have the amp file, OK.

---

