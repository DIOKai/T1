---
name: fivem-vehicle-mod
description: Build, fix and ship FiveM add-on vehicle resources (GTA V car mods) — the stream/ files (.yft, _hi.yft, .ytd), the data/ meta files (vehicles.meta, handling.meta, carcols.meta, carvariations.meta, vehiclelayouts.meta), fxmanifest data_file entries, modkits/tuning parts, liveries, sirens, LODs, texture limits, engine sounds, GTA V Enhanced conversion, and pre-release checks. Use this whenever the user wants to add, convert, tune, optimize or debug a custom car/bike/truck/police vehicle for FiveM or a car pack — including "车不能生成", "改装菜单没东西", "没有引擎声", "贴图掉了", "handling 不生效", "addon car", "debadge", "handling.meta", "警车", "模组警车", "警灯", "警笛", "siren", "lightbar", "ELS" — even if they never say "skill" or "resource". Pair with muto-atlas (/vehicle) for GTA bone names and vanilla specs, and with the Blender/Sollumz skills when the model itself is being built.
---

# FiveM add-on vehicle mods

A FiveM vehicle resource is three things that must agree with each other: the **models and textures** in `stream/`, the **meta files** in `data/`, and the **fxmanifest.lua** that tells the game which meta file is which. Almost every "my car doesn't work" report is one of those three disagreeing — a name spelled differently in two files, a meta file not declared, or an id that another car already uses. So the workflow below is built around keeping names consistent and checking them mechanically before anything reaches the server.

Reference files (read the one you need, not all of them):
- `references/resource-and-meta.md` — folder layout, fxmanifest template, what each meta file controls, which names must match across files, field-by-field notes.
- `references/handling.md` — handling.meta fields, units, sane ranges, how to tune.
- `references/modkits-liveries-sirens.md` — carcols/carvariations: modkit ids, tuning parts, liveries, sirens, lights.
- `references/modeling-sollumz.md` — how modded cars are built in Blender + Sollumz: importing a vanilla base, rigging parts to GTA bones, vehicle shaders and paint layers, light IDs, windows, LODs, export options.
- `references/police-emergency.md` — police/EMS/fire vehicles: siren bones and carcols siren settings (sequencers, wig-wag), extras (`extra_ten`!), liveries, emergency flags, police job configs (qbx_police, qb-policejob), siren controllers (Renewed-Sirensync, LVC) and custom server-side siren sounds.
- `references/performance-and-enhanced.md` — what FiveM's size warnings really mean, texture/poly budgets, LODs, client texture caps, GTA V Enhanced conversion.
- `references/troubleshooting.md` — symptom → cause → fix table.
- `references/tools.md` — exact usage and known quirks of every tool below.

## Workflow

### 1. Name and plan
- Pick a lowercase spawn name with no spaces. It becomes `modelName`, the `.yft`/`.ytd` file names and usually the `handlingId`/`gameName`, so changing it later means touching every file.
- Check it doesn't collide with a vanilla vehicle: `npx -y -p fivem-joaat-hash joaat --reverse <name>` (a "known vehicle" hit means pick another name, or the add-on silently replaces the vanilla car).
- If the car will have tuning parts or a livery kit, reserve a **modkit id** now that no other vehicle on the server uses (see `references/modkits-liveries-sirens.md`). Run the cross-check script on the whole cars folder to see which ids are taken.

### 2. Model (only if building or editing the model)
Read `references/modeling-sollumz.md` first (vanilla-base vs custom-model routes, Sollumz settings). Hand this to the Blender skills (`vehicle-artist`, `hard-surface`, `retopology`, `lod-pipeline`, `uv-workflow`, `texture-workflow`) through the `blender` MCP, and follow the GTA rules from the project CLAUDE.md: GTA's fixed vehicle bone names (look them up with muto-atlas `/vehicle` — doors, wheels, windows, lights only work when the bone name is exact), Sollumz bounds for collision, LOD0 under ~50k triangles. Export with Sollumz to `<name>.yft`, `<name>_hi.yft` and `<name>.ytd` (+ `<name>+hi.ytd` if the high-detail textures are split out).

### 3. Build the resource
Use the layout and fxmanifest template in `references/resource-and-meta.md`. Start the meta files from a similar vanilla vehicle rather than from scratch — muto-atlas `/vehicle <vanilla>` gives its handlingId, layout, modkit and class, which are good defaults for class, layout, audio and handling.

### 4. Handling
Two good starting points, then tune in game:
- copy the handling of a similar vanilla car (via muto-atlas), or
- a preset: `npx -y -p fivem-handling-presets fivem-handling show <preset>` to read it, and `fivem-handling apply <preset> <file> -o <out>` to write it — always with `-o`, on a file that contains only this one car (see the quirks in `references/tools.md`; the tool rewrites every car in the file and overwrites in place without `-o`).

Then tune live on a **dev server** with vehicleDebug (Right Alt in a vehicle), click "Copy Handling", and paste the lines back over the matching fields in handling.meta. Changes made in vehicleDebug are client-side only and vanish on respawn, so nothing is saved until it's pasted into the file. `references/handling.md` explains what each field does.

### 5. Tuning parts, liveries, sirens
See `references/modkits-liveries-sirens.md`; for police/EMS/fire vehicles follow `references/police-emergency.md` (siren setting, extras, liveries, job config, siren controller). The two classic breakages are a modkit id shared with another car (tuning menu empty or shows the other car's parts) and a siren/light settings id shared with another car.

### 6. Check before it goes on the server
Run both checks; they catch different things:
1. `python .claude/skills/fivem-vehicle-mod/scripts/check_vehicle_resource.py <resource-or-cars-folder>` — names that must match across files, modkit/siren/light id collisions and ranges, handlingName overrides between resources, invalid data_file types (e.g. `DLCTEXT_FILE`), files{}/data_file entries (understands globs), asset sizes against FiveM's 16/48 MiB warning levels. Point it at the whole `resources/[cars]` folder to catch collisions between packs. Exit code 1 means errors.
2. `npx -y fivem-vehicle-validator <resource>` (bin name `fivem-validate`) — manifest basics, required vehicles.meta fields, handling value ranges, stream file presence, junk files, nested resources. It reports a false error when files{} uses globs like `'data/**/*.meta'`, and it treats 16 MB as a hard limit (it's really FiveM's warning level); trust the cross-check script for those cases.
3. After `ensure`, read the **server console**: FXServer prints `Asset … uses N MiB of physical/virtual memory` for heavy assets — that's the real size check, since memory use can exceed file size.

Fix errors first, then warnings that make sense. Explain each finding to the user in plain words — what will break in game and how to fix it.

### 7. Test in game
On the dev server: `refresh`, `ensure <resource>`, read the server console and the client F8 console (data_file and handling messages appear there), spawn the car, then walk the checklist — textures at all distances, doors/hood/trunk open, wheels turn and steer, lights and indicators, engine sound, tuning menu shows the right parts, livery switches, siren works (emergency vehicles), handling feels right. Anything wrong → `references/troubleshooting.md`.

## Ground rules
- Never invent meta field names, flag names, data_file types or bone names. If unsure, check the reference files, muto-atlas, or a vanilla vehicle's files — a made-up value usually fails silently in game, which is the worst kind of bug.
- The npx tools download packages the first time they run; say so before the first run. The cross-check script is local, read-only and needs only Python.
- Only test on a dev server. vehicleDebug's `vehdebug` command is unrestricted by default.
- Prefer free tools. The npm tools print links to a FiveMRides web optimizer; it is not part of this workflow and its pricing is unverified, so don't recommend it.
