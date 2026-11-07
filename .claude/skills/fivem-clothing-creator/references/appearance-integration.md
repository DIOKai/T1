# Getting the clothes into the appearance menu (illenium-appearance and others)

Researched 2026-11-08. Code read via GitHub: iLLeniumStudios/illenium-appearance `shared/blacklist.lua`, `shared/config.lua`, `game/customization.lua` (MIT, not archived, last push 2024-12-11; README: do not run `main`, use a release). "(unverified)" = inference.

## 1. No registration needed

- New add-on drawables appear automatically at the **end of each category**. The menu reads the ped's drawable and texture counts; there is no per-item list to edit (inferred from the code; YrsNjOoeqL0 [3:58]).
- qb-clothing and fivem-appearance read the counts the same way (not separately researched).
- If an item does not show in the menu, the problem is the pack (names, meta, entitlement), not the menu. Run `check_clothing_resource.py` and the entitlement check first.

## 2. Installing illenium-appearance (summary)

UNSTJyMc6Dw [0:06–4:58]: depends on ox_lib; remove qb-clothing, fivem-appearance and the tattoo resources, and the qb-clothing dependency in qb-apartments/qb-houses; add `playeroutfits` and run the SQL; adjust multicharacter; a migration command from qb-clothing exists. On Qbox follow the framework's own notes; do not mix qb-core and qbx_core instructions.

## 3. Blacklist: hide items per job, gang, ACE or citizen

`shared/blacklist.lua`, enforced in `game/customization.lua` lines 31–111:

```lua
Config.Blacklist = {
  male = {
    hair = {},
    components = { masks = {}, upperBody = {}, lowerBody = {}, bags = {}, shoes = {},
                   scarfAndChains = {}, shirts = {}, bodyArmor = {}, decals = {}, jackets = {} },
    props = { hats = {}, glasses = {}, ear = {}, watches = {}, bracelets = {} },
  },
  female = { --[[ same shape ]] },
}
-- one entry, e.g. in components.jackets:
{ drawables = { 400, 401 }, textures = { 2, 3 }, jobs = { 'police' }, gangs = { 'ballas' }, aces = { 'vip' }, citizenids = { 'ABC123' } }
```

- With `textures`, only those textures are hidden, and only when the current drawable matches; without `textures` the whole drawable is hidden.
- The item is allowed if the player matches **any** of jobs, gangs, aces or citizenids. ACEs come from a server callback and must be listed in `Config.Aces`.
- Category → slot mapping (inferred from the names; verify before writing a blacklist):

| illenium name | slot |
|---|---|
| masks | component 1 (berd) |
| upperBody | 3 (uppr, "arms") |
| lowerBody | 4 (lowr) |
| bags | 5 (hand) |
| shoes | 6 (feet) |
| scarfAndChains | 7 (teef) |
| shirts | 8 (accs) |
| bodyArmor | 9 (task) |
| decals | 10 (decl) |
| jackets | 11 (jbib) |
| hats / glasses / ear / watches / bracelets | props 0 / 1 / 2 / 6 / 7 |

**It is only a client-side menu filter.** It hides choices in the menu; it does not stop a modified client from setting the component (reading of the code). Do not treat it as security for job uniforms. If it matters (for example a police uniform that grants recognition), check on the server and follow `fivem-security`.

## 4. Other config worth knowing (`shared/config.lua` 5–98, 560–640)

- `Config.DisableComponents` / `Config.DisableProps`: turn whole categories off (for clothing-as-items setups).
- `Config.PreventTrackerRemoval` + `Config.TrackerClothingOptions`: reserve an accessory drawable for a tracker.
- `Config.ClothingRooms` and job outfits: per slot `{ item = <drawable>, texture = <n> }` using the names pants, arms, t-shirt, vest, torso2, shoes, accessory, bag, hat, glass, mask. Each jacket ("torso2") is paired with an "arms" value (for example torso2 55 + arms 19, lines 607–628).
- `Config.AutomaticFade`.

## 5. Absolute drawable numbers shift

- Global drawable numbers depend on the game build and on `ensure` order (DCT shop-meta-file, placeholders-dummy-ids; DCT "R" relative vs "A" actual numbers, ba86DBN396k [56:37–57:43]).
- So **blacklists, job outfits and saved outfits that store absolute numbers break** when a pack is added, removed or reordered, or the server build changes (`sv_enforceGameBuild`).
- After any of those changes: open the menu on the local test server, write down the new numbers of the custom items, update `Config.Blacklist` / job outfits, and tell the user that players' saved outfits may point at different items.
- Keep the clothing packs' `ensure` order fixed in server.cfg, and add new packs at the end so existing numbers move as little as possible (inference).

## 6. Hand-off checklist for the user

1. Which pack holds the item, gender, category (illenium name), and the number seen in the menu on the test server.
2. Which "arms" (upperBody) value to pair with each new top.
3. Blacklist entries, if any, with a note that they are cosmetic only.
4. The reminder that numbers must be rechecked after packs or builds change.
