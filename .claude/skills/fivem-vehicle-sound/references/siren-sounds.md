# Custom siren sounds (server-side siren packs)

How a FiveM server ships its own siren tones (wail, yelp, priority, horn…) that a siren controller such as Renewed-Sirensync or LVC plays on emergency vehicles. Lights and siren *patterns* (carcols `<Sirens>`, sequencers) are a different thing — see `fivem-vehicle-mod` → `references/police-emergency.md`.

Facts marked **[verified]** were checked on 2026-11-08 against the vanilla game files (G:\…\x64\audio\audio_rel.rpf, read-only) and by rebuilding the user's own pack byte-for-byte.

## How it fits together

```
siren controller (Lua)          PlaySoundFromEntity(soundId, "lore_fed_wail", veh, "lore_sirens_federal", false, 0)
                                                    audioName ─┘                 audioRef ─┘
dat54  SoundSet  lore_sirens_federal   →  entry ScriptName lore_fed_wail  →  ChildSound lore_fed_wail_snd
dat54  SimpleSound lore_fed_wail_snd   →  ContainerName dlc_lore_sirens/federal, FileName lore_fed_wail
awc    dlc_lore_sirens/federal.awc     →  stream lore_fed_wail (PCM, LoopPoint 0 = loops from the start)
client RequestScriptAudioBank('DLC_LORE_SIRENS\\FEDERAL', false)  — the bank must be loaded before playing
```

Resource files: `dlc_<pack>/<bank>.awc` (one wave bank per tier/agency), `data/<pack>_sounds.dat54.rel` (+ optional `.nametable` with the container paths), `fxmanifest.lua` with `data_file 'AUDIO_WAVEPACK' 'dlc_<pack>'` and `data_file 'AUDIO_SOUNDDATA' 'data/<pack>_sounds.dat'` (path stops at `.dat`, see `workflows.md` §4), `client.lua` that requests the banks.

## Rules that decide whether you hear anything

1. **Names in the REL must be hashed in lowercase. [verified]** The game lowercases audio names before hashing: vanilla `sounds.dat54.rel` / `dlc_gtao_sounds.dat54.rel` contain the lowercase-name hash of `HUD_FRONTEND_DEFAULT_SOUNDSET`, `SELECT`, `BACK`, `NAV_UP_DOWN`, never the uppercase one. CodeWalker hashes the text **as written** (`JenkHash.GenHash`, `XmlRel.GetHash` are case-sensitive: `ADDER` ≠ `adder`), so a REL built from XML with `LORE_SIRENS_FEDERAL` is silent in game. Write every SoundSet / ScriptName / sound name in lowercase. Callers can still pass any case — the game lowercases their string too.
2. **SoundSet entries end up sorted by name hash. [verified]** CodeWalker sorts them by the hash of the ScriptName text when it imports the XML (tested 2026-11-08: shuffled entries came back ascending by hash), so you don't need to sort by hand — but it sorts by the hash of what you *wrote*, so uppercase names are also sorted into the wrong order (another reason rule 1 matters). The script sorts anyway, which is harmless.
3. **AWC streams:** mono 16-bit PCM WAV only (CodeWalker import), `Samples` must equal the WAV length (CodeWalker does not update it), `LoopPoint 0` so the tone loops seamlessly. Odd sample counts are fine for plain PCM banks **[verified: the user's working banks have odd counts]** — don't pad, a padded sample is a gap at every loop. Make the loop itself seamless first (`audio-loop-editing`).
4. **SimpleSound header** copied from vanilla sirens: `Flags 0x0020E000`, `ReleaseTime 50`, `DopplerFactor 30`, `Category vehicles_sirens` (siren volume slider / ducking), `VolumeCurveScale 300` (carries far).
5. **Banks loaded on the client** with `RequestScriptAudioBank('DLC_<PACK>\\<BANK>', false)` (loop until true), released on resource stop.
6. Clients must **reconnect** after installing or changing audio data; restart the server for a first install.

## Build with the script

`scripts/siren_pack.ps1` (needs only the user's CodeWalker folder with `CodeWalker.Core.dll`; ask before running):

```
<WavRoot>\federal\WAIL.wav, YELP.wav, HORN.wav …
<WavRoot>\state\…   <WavRoot>\county\…   <WavRoot>\city\…

powershell -ExecutionPolicy Bypass -File siren_pack.ps1 build -CodeWalker <CW> -WavRoot <WavRoot> -Pack lore_sirens -Prefix LORE -BankCodes "federal=FED,state=STA,county=COU,city=CIT" -Out <work>\out
```

Names: SoundSet `lore_sirens_<bank>`, sound `lore_<code>_<tone>` (shown uppercase in `TONES.txt` for people; stored lowercase). It writes the AWCs, the dat54 (lowercase, sorted), nametable, fxmanifest, client.lua and `TONES.txt`, then **reloads the REL and fails if any name is not lowercase-hashed**. `dump` exports an existing pack (XML + WAVs); pass `-NamesFile` (a `TONES.txt` or the siren controller's config) so hashes print as names.

Verified 2026-11-08: rebuilding the user's federal bank from its own exported WAVs gives a **byte-identical** `federal.awc`; the REL matches the October build in every container, stream and header field — the only change is the corrected lowercase name hashes.

## Getting the tones

- Free sources: record your own, or use packs whose licence allows reuse; many "siren packs" on gta5-mods are ripped from manufacturers' demo recordings or other games → own server only, never re-upload or sell (`fivem-vehicle-sound` licensing).
- Packs that only ship a `RESIDENT.rpf` replacement: open it in CodeWalker, export `vehicles.awc` to XML + WAVs; stream names are hashes (`joaat(name) & 0x1FFFFFFF`) — compare with the vanilla RESIDENT.rpf to see which slots the pack actually replaced (user's notes, police-siren-tones memory).
- Trim each tone to a seamless loop (zero crossing, matching level at both ends), mono, 16-bit; keep the original rate (44.1 kHz is typical).

## Wiring a controller (Renewed-Sirensync example)

Per vehicle model or group: `audioRef = 'lore_sirens_federal'` (any case), each siren mode's `audioName = 'LORE_FED_WAIL'`, horn `audioName = 'LORE_FED_HORN'`. The controller syncs state through state bags and calls `PlaySoundFromEntity`. Test on the local server: each mode on each tier, horn while a siren plays, two clients hearing the same vehicle, after a reconnect.

## Troubleshooting

| Symptom | Cause → fix |
|---|---|
| Siren silent, no errors | names hashed in uppercase (rebuild with the script); bank not requested; wrong audioRef; client not reconnected |
| Default GTA siren plays instead | the controller fell back because the sound was not found → same causes as above |
| Click / gap each loop | loop not seamless, or a padded/trailing silent sample |
| Very quiet or cut off at distance | header changed from the vanilla siren values (`VolumeCurveScale`, category) |
| Only some tones work | two tones share a name, or some names were written in uppercase and others in lowercase |
| Crash on join | `data_file` points at a missing file |
