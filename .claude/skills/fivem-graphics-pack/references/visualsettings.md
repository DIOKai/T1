# visualsettings

`visualsettings.dat` (in the game's `common` data) holds several hundred global render constants that the timecycle doesn't cover: vehicle light emissive strength (`car.headlight.night.emissive.on`, `car.taillight.*`, `car.defaultlight.*`), ped lights (`pedLight.color.red`), distant lights (`distantlights.*`), search lights, traffic lights, puddles and rain (`puddles.*`, `rain.*`), tonemapping (`Tonemapping.*`), bokeh and adaptive DOF (`bokeh.*`, `adaptivedof.*`), LOD lights, imposters. Night-time "better lights" packs mostly change these.

## How to apply it in FiveM

There is **no `data_file` type** for visualsettings. Placing a `visualsettings.dat` in a resource does nothing on its own. Use the CFX client native (`extra-natives-five/src/VisualSettingsNatives.cpp`):

```lua
SetVisualSettingFloat('car.headlight.night.emissive.on', 120.0)
```

Implementation facts, from the source:
- It stores an override for that name and **reloads the whole visualsettings file** on every call, so set everything once at resource start, not every frame.
- The override is **removed when the resource that set it stops** — stopping the pack restores vanilla.
- `GetVisualSettingFloat(name)` reads the current value.
- Pass the value as a float (`120.0`, or `tonumber(v) + 0.0`), which is what published packs do.

A common pattern is to ship your own `visualsettings.dat` as a plain file and parse it in a client script:

```lua
-- fxmanifest.lua: files { 'visualsettings.dat' }  client_script 'visual.lua'
CreateThread(function()
    local text = LoadResourceFile(GetCurrentResourceName(), 'visualsettings.dat')
    if not text then return end
    for line in text:gmatch('[^\r\n]+') do
        local name, value = line:match('^%s*([%w%._]+)%s+([%-%d%.]+)')
        if name and not line:match('^%s*[#/]') and tonumber(value) then
            SetVisualSettingFloat(name, tonumber(value) + 0.0)
        end
    end
end)
```

Only list the keys you change, not a full copy of the vanilla file — it's clearer and avoids shipping values you never meant to touch. Published packs skip `weather.CycleDuration` when bulk-applying; leave weather timing to a weather sync resource.

## Getting the vanilla names and values

Export `common/data/visualsettings.dat` from **the user's own game** with CodeWalker or OpenIV and copy the names you need. Don't copy another pack's tuned file unless its licence allows it (many popular packs have no licence at all, which means no permission).

## Tuning tips (rules of thumb)

- Vehicle lights look "better" at night mostly through `car.*.night.emissive.on` and `car.headlight.*` intensity/falloff values; raise in small steps — high values bloom out in rain.
- Change one group at a time, compare screenshots at the same place, time and weather.
- These apply to everyone on the server; give players a toggle if a change is strong.
