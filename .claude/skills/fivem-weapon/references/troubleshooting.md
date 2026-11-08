# Troubleshooting and acceptance

Run `scripts/check_weapon_resource.py <resource> --ox <ox_inventory> --xml <export folder>` first; most rows below are checker codes.

## 1. Symptom → cause

| Symptom | Likely cause | Checker code | Source |
|---|---|---|---|
| Item in ox inventory, **nothing in hand** | ox key/model ≠ weapons.meta `Name` → unknown hash | OX_MISSING | ox loader (L) |
| | weapons.meta not loaded: data_file typo, not in `files {}`, XML broken | DATA_FILE_UNKNOWN, NOT_IN_FILES, META_PARSE | resource-manifest docs |
| | resource not started (`ensure` missing, category not ensured) | — | server-layout memory |
| Weapon selected but **invisible** | `Model` ≠ archetype `modelName` ≠ ydr name | MODEL_NO_ARCHETYPE, MODEL_NOT_STREAMED | 2019 guide 293807 |
| | only `_hi.ydr` streamed ("HD-only cannot be streamed") | HI_WITHOUT_BASE | 2019 guide |
| | ydr outside `stream/`, or still XML | NOT_IN_STREAM, XML_IN_STREAM, NOT_RSC7 | — |
| | mesh not skinned (no armature / vertex groups) | XML_NO_SKELETON | Sollumz rigging docs |
| Held as a floating prop / offset | not aligned to the template; transforms not applied | — | ook_3D [01:02]; Desertos [06:57] |
| Parts don't move / whole gun moves | vertex groups ≠ bone names; Armature modifier missing or on the mag | XML_BONES_MISSING | ook_3D [03:07], [04:53] |
| Muzzle flash wrong place | `Gun_Muzzle` position | — | Desertos [17:59] |
| Mag floats / jitters when firing | `WAPClip` misplaced; bone limits | — | ook_3D [12:33]–[14:50] |
| Attachment won't attach | not in AttachPoints; bone missing in skeleton (musket has no WAP); component model not streamed/archetyped; not in an ox Components list | COMPONENT_UNDEFINED, XML_ATTACH_BONE_MISSING, OX_COMPONENT_MISSING | (L) ox code |
| Attachment at gun origin | component root bone ≠ `AttachBone` (AAP*) | COMPONENT_BONE, XML_COMPONENT_ROOT | (V) |
| Crash on reload | mag model missing from weaponarchetypes | COMPONENT_NO_ARCHETYPE | 2019 thread replies |
| CWeaponManager crash on reconnect | FiveM failing to unmount weapon metas; restart the client | — | 2019 thread replies |
| Not in wheel / name NULL | Slot not in SlotNavigateOrder, duplicate OrderNumber, no AddTextEntry | SLOT_NOT_IN_NAV, ORDER_DUPLICATE, NO_TEXT_ENTRY | melee guide 246436 |
| Wrong holding animation / T-pose arms | no weaponanimations entry for `Name` | NO_ANIMATION | 2019 guide |
| Damage feels vanilla / no damage | meta not loaded (see row 2); edited a field the template overrides; server artifact problem reported | — | forum.cfx.re/t/2603053 (unverified) |
| Purple / missing textures | `txdName` ≠ ytd; texture names ≠ shader parameters | TXD_MISSING | (V) structure |
| Falls through floor when dropped | no collision in the base ydr | XML_NO_BOUNDS | (V) |
| Streaming warnings | ytd > 16 MiB (vanilla carbine is exactly 16 MiB) | ASSET_OVER_16MIB | FXServer tiers |
| Slow first draw | streaming on first use | — | Bizarre [03:10] |

### "Shows in the inventory but invisible in hand" — order to check

1. F8 console / client log when equipping: resource errors, `Couldn't find weapon` style messages.
2. ox key or `model` = weapons.meta `Name` (`--ox`).
3. Manifest: types spelled right, every meta in `files {}`, weapons.meta last; the resource is ensured.
4. `Model` = archetype `modelName` = `stream/<model>.ydr`; base ydr streamed, not only `_hi`.
5. Binary, not XML; RSC7 header.
6. Skeleton: mesh parented to the template armature, vertex groups = bone names, Armature modifier on the weapon armature (`--xml`).
7. Hand-test with a plain native to rule out ox: `GiveWeaponToPed(PlayerPedId(), joaat('WEAPON_TYPE38'), 10, false, true)` on a local test server.

## 2. In-game acceptance list

Local test server only (the `fivem` MCP can run commands there — ask first, never production).

- [ ] Third person: grip in hand, both hands placed, no clipping through the arm.
- [ ] First person: iron sights / scope line up; reticule; scope zoom.
- [ ] Fire: muzzle flash at the muzzle, shell ejection at the port, recoil, sound fits the fire mode.
- [ ] Reload: mag/clip moves with the hand, bolt cycles; no crash.
- [ ] Each attachment on and off (ox component items); suppressed flash from the suppressor tip.
- [ ] Tints (if the palette shader is used).
- [ ] Drop the weapon: lands on its collision.
- [ ] Wheel: segment, order, name.
- [ ] ox: equip/unequip, durability, ammo item, image; reconnect → still works.
- [ ] Damage against a second player vs the design value; server logs show the anti-cheat hooks still see it.
- [ ] resmon / streaming: no warnings in the server console.
