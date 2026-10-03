# Sollumz clip dictionary export and CodeWalker compile

Sources: Sollumz `ycd/operators.py`, `ycd/properties.py`, `ycd/ycdexport.py`, `tools/animationhelper.py`, `sollumz_operators.py`; CodeWalker `Clip.cs`, `XmlMeta.cs`, `YcdFile.cs`; Sollumz wiki (YCD pages); muto-atlas `trunk/tool-pitfalls.md`.

## Objects
Sollumz Tools ▸ Animations ▸ **Create clip dictionary template** creates a Clip Dictionary with **Animations** and **Clips** children; add items with "Create animation" / "Create clip".
- An **Animation** holds the bone data (one Blender Action).
- A **Clip** is what scripts play: metadata pointing at one or more animation ranges. Several clips can use ranges of one animation (vanilla `move_m@generic`: idle 0–30, run 30–60, sprint 60–90).

## Animation fields
| Field | Set to |
|---|---|
| Hash | a name for the animation (e.g. `dio_wave_anim`) |
| Action | the Blender action |
| Target | **the armature DATA block**, not the armature object. Pointing at the object exports 0 bone channels (muto-atlas measured 724 bytes vs 59 KB) |

## Clip fields
| Field | Set to | Why |
|---|---|---|
| **Hash** | **exactly the clip name scripts will use** (e.g. `wave_clip`) | The game looks clips up by Hash (CodeWalker builds the clip map from `<Hash>`; plain text → joaat). Sollumz's default is empty — empty hashes collide and the clip is "not found" silently |
| Name | same name (exported as `pack:/<name>`) | readability |
| Duration | **(end frame − start frame) / 30** | Sollumz writes `rate = animation length / Duration`; anything else changes playback speed. Duration 0 → division by zero |
| Linked Animations | the animation + start/end frame (inclusive) | start actions at frame 0 |
| Tags (optional) | templates: MoVE Event, Audio, Foot, Mover Fixup, Facial, Object, Arms IK | sync events; not needed for simple emotes |

Sollumz sorts animations and clips alphabetically by object name.

## Export
- Clip dictionaries export as **XML only** (`.ycd.xml`); they're outside Sollumz's native/Gen8/Gen9 export system, so those settings don't apply.
- Errors to expect: "Action '…' has no keyframes … Cannot export empty action"; "Channel '…' is unsupported, skipping…" (Euler rotation — switch to quaternion); exported file tiny (Target set to the object).

## Compile with CodeWalker
CodeWalker ▸ RPF Explorer ▸ **Import XML** recognises `*.ycd.xml` and builds a binary `.ycd`. Put only the binary `.ycd` in the resource. CodeWalker's ped viewer previews clips from game data only; it doesn't list a loose resource `.ycd`.

## Naming
- Dictionary name = the `.ycd` file name without extension (FiveM registers streamed files by extension and file name). Lowercase, no spaces, unique — `@` is fine (`dio@wave`).
- Clip name = the clip Hash inside.

## Checklist before compiling
- [ ] Scene at 30 fps; pose bones in quaternion mode
- [ ] Constraints/IK baked; action starts at frame 0
- [ ] Animation Target = armature data
- [ ] Every clip has Hash = clip name; Duration = (end − start) / 30
- [ ] `check_anim_resource.py <export folder>` shows no errors (empty hash, Rate ≠ 1, fps ≠ 30)
