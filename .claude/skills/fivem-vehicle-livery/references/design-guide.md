# Livery design guide (police, sheriff, state, federal, fire/EMS)

Real-world conventions here come from tutorials, reference sites and secondary sources — no official livery standard was read (unverified as "rules"; treat them as good defaults). Sources: `sources.md`.

## 1. Names and marks: the user's fictional agencies only

Livery text and badges use only the server's own agencies (agreed lore, memory `police-radio-dispatch-design`):

| Level | Agencies on cars | Notes |
|---|---|---|
| City | **LSPD** | Los Santos Police Department |
| County | **LSCSO** (Los Santos County, HQ Davis), **BCSO** (Blaine County, Sandy Shores), **RCSO** (Paleto Bay) | RCSO's full county name: ask the user (Roxwood vs "Raton" not settled) |
| State (SADPS) | **SASP** (south of the Blockz wall), **SAST** (north, checkpoints) | SADPS itself is the parent department, not a patrol livery |
| Federal | **FIB**, **FFRB** (under FDOJ); **NOOSE**, **FCBA**, **LSPA** (port + sea) | Federal cars are often unmarked or low-profile |

- Never use real agency names, badges, state seals, real department crests or real US-state flags. Tutorials that trace a real county (0JALZnODuag Pickens County SO; 0eCBJCMn_Jg Harris County) — copy the layout idea, not the crest. Design original stars, shields and seals.
- Never put real car makes or models in livery text ("Dodge", "Ford", "Charger", "Tahoe", "Hellcat", "PPV"…). Use GTA brands/names (Bravado, Vapid, Declasse, Bison, Dominator…) — the user's brand rule. Cfx.re's licence terms warn that real brands "may result in legal action" and "De-badging … alone does not mean your server is fully compliant" (press reports; read fivem.net/terms for the current wording). BrendonSapp157 (JkdthK3tHgo 02:44): "we don't run IRL cars because it's against terms of services".
- Vanilla GTA already uses "LSPD", "Los Santos County Sheriff", "Blaine County", "San Andreas", "Los Santos County Fire Department" (vanilla textures).
- The Star of Life is reportedly a registered certification mark in the US (unverified) — design an original medical symbol. EMS liveries are low priority on this server (no player EMS; NPC ambulance planned).

Pair with `branding` (agency identity sheet: colours, star/shield, type), `color-theory`, `typography` — ask first. Fonts: free with a licence that allows use (OFL fonts are fine); the user's Ram-style lettering is Saira Expanded Black (OFL).

## 2. Patterns

- **US patrol**: base colour (black-and-white doors, all white, all black, slicktop for unmarked), a side stripe or swoosh following a body line, agency name on the front doors, star/badge on the doors, "POLICE" / "SHERIFF" / "STATE TROOPER" large on the rear quarters or doors, "DIAL 911", unit number on the rear quarters, trunk/tailgate and the **roof**. Vanilla: police roof "32"/"42", polgauntlet roof "672" (vanilla textures).
- **Sheriff (county)**: traditionally star badges, often green/tan/brown or black-and-white; one colour scheme per county keeps LSCSO / BCSO / RCSO apart at a glance.
- **State (SASP / SAST)**: highway look — one colour family for both, different rocker/door text; Battenburg is an option if the user wants a European look (ask; GTA is US-themed).
- **Battenburg** (UK/Europe): one row (half) or two rows (full) of alternating rectangles, fluorescent + retroreflective, conspicuous "from up to 500 metres"; blocks ≥ 600×300 mm, about seven per side; police yellow/blue, ambulance yellow/green, fire yellow/red; outline roof pillars (Wikipedia "Battenburg markings" — article carries citation warnings). Sillitoe tartan is the older black/white chequer.
- **Fire apparatus rear chevrons** (NFPA 1901 since 2009, secondary sources): ≥ 50 % of the rear surface, stripes 6 in wide at 45° sloping down and away from the centre, alternating red and (fluorescent) yellow, retroreflective — check the current NFPA edition before quoting it.
- **Federal**: unmarked or a small door seal + "FIB" in low-contrast reflective style; FCBA/LSPA can be fully marked (border/port patrol). Ask the user per agency.
- **Reverse text on the hood**: ambulances use mirrored "AMBULANCE" so drivers read it in mirrors (vanilla `ambulance_sign_1` has it). Police cars normally don't (unverified for real fleets) — verify with the user before adding.

## 3. Size and legibility (game-scaled)

Measured texel density of a full-body template (vanilla polgauntlet, both sides ≈ 3.3 m² each; the user's shelby20pd is the same within 3 %):

| Texture size | px per cm of body | 25 cm "SHERIFF" | 10 cm small text |
|---|---|---|---|
| 1024 | ≈ 2.0 | ≈ 50 px | ≈ 20 px (too small) |
| 2048 | ≈ 4.0 | ≈ 99 px | ≈ 40 px (minimum) |
| 4096 | ≈ 7.9 | ≈ 198 px | ≈ 79 px |

`livery_template.py` prints the real density for each car (it varies: the user's 23DChargerHenPEpd centre panels are only 2.4 px/cm at 2048).

- Real-world sign rules: about 1 in of letter height per 10 ft of reading distance (sign industry); FHWA/MUTCD 30 ft per inch (≈ 3.6 m per cm) at 20/40 acuity; US Access Board legibility index ≈ 35 ft/in. A 25 cm word is readable to roughly 90 m by the 30 ft/in rule.
- Below about **40 px letter height**, DXT compression and mips smear text (empirical, unverified). Put fine print (DIAL 911, small unit numbers) where the density is highest and the panel is flat.
- Roof unit numbers large (≈ 50–60 cm, guideline) and rotated so a helicopter reads them; check the roof island's FRONT arrow in the template.
- Contrast: dark on light paint or the reverse; outline light text over mixed backgrounds (dgVnz0Inf78 17:40). Test with every colour the job config spawns (vanilla police carvariations use primary 0 black / secondary 111 white).
- Badge sources ≥ 500×500 px, scaled once (0JALZnODuag 06:11–07:53).

## 4. Colours in game

- Livery pixels replace the paint, so painted livery areas lose the metallic paint look ("primer grey" look) and colours read lighter in game (BigPilotGuy U8vTQpWMn9Q 35:12, 41:29). → leave the body colour transparent where possible and let the spawn colour do the base; darken livery colours slightly; check in game.
- DXT banding: avoid long smooth gradients on large areas; flat colour blocks compress best.
- Reflective-stripe looks: the livery layer has no separate retroreflective input in the shader parameter list; "reflective livery" tutorials use ZModeler 3 (paid) and probably edit spec/material (unverified).

## 5. Before painting a fleet

1. Agency sheet per department: name text, badge, 2–3 colours, font, unit-number format (e.g. `LSCSO 2-14`), where each item goes.
2. One car first: checker test, then one livery, test in game, then the rest.
3. Name files by department and index (`<prefix>_sign_2` = LSCSO patrol, `_sign_3` = LSCSO K9 …) and keep a list for the job config and the AddTextEntry labels.
