# Framework integration and server authority

(L) = read in the user's server files (read-only): ox_inventory 2.48.0 at `H:\FiveM\Server\txData\Qbox_C3A86D.base\resources\[ox]\ox_inventory`, qbx_core `shared/weapons.lua`. For general ox item fields and exports see the `ox-inventory` skill; for event security see `fivem-security`. Ask before using either.

## 1. ox_inventory (the user's server)

`data/weapons.lua` returns `{ Weapons = {}, Components = {}, Ammo = {} }` (+ `Tints`) (L).

```lua
-- Weapons
['WEAPON_TYPE38'] = {          -- key = weapons.meta <Name> (or set model = 'WEAPON_TYPE38')
    label = 'Type 38 Rifle',
    weight = 3900,
    durability = 0.05,         -- default 0.05 when omitted
    ammoname = 'ammo-type38',  -- an Ammo item; melee has none; throwables add throwable = true
},
-- Components: add new hashes in back-ticks to the right list
['at_scope_type38'] = {
    label = 'Type 97 Scope', type = 'sight', weight = 300,
    client = { component = { `COMPONENT_TYPE38_SCOPE` }, usetime = 2500 },
},
-- Ammo
['ammo-type38'] = { label = '6.5x50mm', weight = 10 },
```

Loader facts (L, `modules/items/shared.lua` ~76–106): `v.model = v.model or k`, `v.hash = joaat(v.model)`, weapons do not stack unless `throwable`. So the key/model must equal the meta `Name` — otherwise the item exists, `GiveWeaponToPed` gets an unknown hash and the hand stays empty.

Equip path (L, `modules/weapon/client.lua` 41–85): `GiveWeaponToPed(ped, hash, 0, false, true)`, tint from metadata, components through `DoesWeaponTakeWeaponComponent` + `GiveWeaponComponentToPed`, `SetCurrentPedWeapon`, `SetPedAmmo`. A component therefore needs **both** an AttachPoints entry in weapons.meta **and** an ox Components entry listing its hash; default clips need no ox item.

- Rifle suppressor on a rifle → heavy-suppressor list (Kamaryn `8gV077l0qPk` [01:48]–[03:01]).
- Image: `web/images/<ITEM NAME>.png` exactly as the key (`WEAPON_CARBINERIFLE.png`, `ammo-rifle.png`) (L); wrong name → no picture (QbDork `p33vuz4FZYQ` [16:18]).
- Ammo type only decides which ammo item loads the gun, not damage (Zeroskyrim `vPFcvAx9BU0` [02:11]).
- After editing `data/weapons.lua` restart ox_inventory (or the server); edits are data, not code — `qbox-lua-check` still helps on Lua edits.

Checker: `check_weapon_resource.py <res> --ox <ox_inventory>` checks key/model, ammo item, image, and non-default components.

## 2. Qbox and QBCore

- **Qbox**: `qbx_core/shared/weapons.lua` header (L): "@deprecated … If you are utilizing QB-Core bridge functionality you will need to populate weapons here … If not please add your weapons in ox_inventory/data/weapons.lua". ox_inventory is the source of truth; only touch qbx's list when a bridge script asks for it.
- **QBCore** (Kamaryn `-iYB4CQIwvc` [03:34]–[11:50], TaterTot [11:58]–[15:14]): `qb-core/shared/items.lua` (`type = 'weapon'`, `ammotype = 'AMMO_RIFLE'`, `unique = true`), `qb-core/shared/weapons.lua` (`name, label, weapontype, ammotype, damagereason`), `qb-weapons/config.lua` (durability, attachments), `qb-smallresources` weapdraw and recoil, `qb-jewelery` (case-smash weapons), `qb-ambulancejob` (damage type), `ps-dispatch` (shot alerts).
- On any server, grep the resources for an existing weapon name (e.g. `WEAPON_CARBINERIFLE`) to find other lists the new gun must join (dispatch, holsters, recoil, evidence).

## 3. Natives

- Client: `GIVE_WEAPON_TO_PED(ped, hash, ammo, isHidden, forceInHand)`, `GIVE_WEAPON_COMPONENT_TO_PED`, `SET_PED_AMMO`, `HAS_PED_GOT_WEAPON(ped, hash, false)`, `SET_PED_WEAPON_TINT_INDEX` (0–7, MK2 separate), `SET_WEAPON_DAMAGE_MODIFIER(hash, mult)` ("does NOT need to be called every frame"), `ADD_TEXT_ENTRY` (citizenfx natives `WEAPON/*.md`).
- Server RPC natives exist for `GIVE_WEAPON_TO_PED`, `GIVE_WEAPON_COMPONENT_TO_PED`, `REMOVE_WEAPON_FROM_PED`, `REMOVE_ALL_PED_WEAPONS`, `REMOVE_WEAPON_COMPONENT_FROM_PED`, `SET_CURRENT_PED_WEAPON`, `SET_PED_AMMO` (citizenfx/fivem `ext/natives/rpc_spec_natives.lua`). Server `GET_SELECTED_PED_WEAPON`; the HUD-selected weapon "is not available to FXServer" (native-decls).

## 4. Server authority (user rule)

- Weapon stats live in client-side metas; a cheater can forge hits regardless of what the meta says.
- Give weapons only from the server inventory (`exports.ox_inventory:AddItem` in server code after a server-side check). Never a client event like `TriggerServerEvent('giveWeapon', 'WEAPON_TYPE38')`.
- Ammo, durability, component items: counted and removed server-side (ox does this when weapons are items).
- Damage: hook `weaponDamageEvent`, `giveWeaponEvent`, `removeAllWeaponsEvent` — code in `fivem-security/rules/net-game-events.md` (do not duplicate). Add the new weapon hash to any max-damage or allowed-weapon tables there.
- Shops, crafting, loot: `qbox-economy-integrity` for dupes/refunds, `game-balance-economy` for prices; damage values are a design decision — write them down with the reason.
- Audit a downloaded weapon script with `fivem-security-audit` before running it.

## 5. Weapon wheel and HUD

- Wheel segment = `WheelSlot`; position = `SlotNavigateOrder` OrderNumber; name = `HumanNameHash` + `AddTextEntry`.
- Custom wheel **icons**: only "a very complicated process involving hex editing" was found (forum.cfx.re/t/1309791, 2020) — no clean free method (gap).
- An add-on weapon reported missing from the wheel after reconnect until re-given (same thread, 2021); ox_inventory re-equips from the item, so this mostly affects script-given weapons.
- First draw of a new gun can lag while it streams (Bizarre `64tDogV3GW8` [03:10]).
