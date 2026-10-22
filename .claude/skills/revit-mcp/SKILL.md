---
name: revit-mcp
description: Connect Claude Code or Codex to the user's own Autodesk Revit through MCP and work in a live model safely — read levels, views, types and parameters, then build or edit walls, floors, roofs, openings, families and views in small stages approved inside Revit (pyRevit 7 agent runtime, the BIMBridge installer from the "Statue of Liberty in Revit with one Claude prompt" reel, Autodesk's Revit 2027 MCP tech preview, mcp-servers-for-revit) — and turn a Revit model into a three.js scene for camera paths or a flat colour-map video with one colour per material, free via the Leia glTF exporter or IFC plus web-ifc. Use whenever the user mentions Revit, RVT/RFA, pyRevit, BIMBridge, Revit MCP, Revit API scripts, Revit to glTF/three.js/web, or a material colour map of a Revit model — even if they only say "Revit", "BIM", "连接Revit", "Revit MCP", "pyRevit", "Revit 转网页", "Revit 导出 glTF", "用 AI 在 Revit 里建模", "一个 prompt 建自由女神像", "材质色块图".
---

# Revit MCP

The reels make it look like one prompt builds the Statue of Liberty in Revit. What actually makes that work is boring and important: the AI sends **small Python programs** into Revit, Revit shows each change and asks **Keep / Discard**, every kept change is **one undo step**, and the AI looks at a screenshot before the next stage. This skill keeps that loop, because a live Revit model is somebody's project file — a bad script can wreck hours of work, and everything the AI reads is sent to the model provider.

The user has an Autodesk membership, so Revit itself is fine to use and recommend. Anything Autodesk bills on top (cloud credits, APS Design Automation, paid add-ins) still falls under the T1 no-paid rule: don't use or recommend it without asking.

## Always ask first (T1 rule)

Ask before each of these, and say what it will do:
- **Using any Revit MCP** — reading a model sends element names and parameter values to Anthropic/OpenAI; check the project allows that.
- **Installing anything** — pyRevit, BIMBridge, an add-in, npm packages. Never run `irm … | iex` without the user's OK, and read the script first.
- **Changing the model** — every `run_modify` (or create/delete tool). Suggest a copy of the `.rvt` for the first session; never on a central / workshared file without the user saying so.
- **Changing the approval policy** — leave pyRevit at `ask`. `auto` is only for a throwaway copy, and only if the user asks (e.g. for filming).

If the `pyrevit` (or other Revit) MCP tools aren't in the tool list, say the server isn't connected; don't install or configure it on your own.

## 1. Pick the connector

Read `references/connectors.md` for install lines (Claude Code **and** Codex), tool lists and security notes. Short version:

| Situation | Use |
|---|---|
| Default — Revit 2024/2025 (validated), 2022–2027 (loads, agent runtime not validated) | **pyRevit 7 agent runtime** (free, GPL-3.0). Built-in MCP server, named pipe (no network port), approval inside Revit, one undo per change. `pyrevit configs agent enable` + `pyrevit mcp install claude` / `codex`. |
| User saw the BIMBridge reel and wants the same | **BIMBridge** (MIT) is only an installer + two skills on top of pyRevit 7's MCP server. Same result as the line above; read its `install.ps1` with the user before running it — it downloads and silently installs pyRevit. |
| Revit 2027.2+ and wants Autodesk's own | **Autodesk Revit MCP server** (Tech Preview, Read / Write / Experimental installers from Autodesk Account). Inside the membership as far as found; extra cost **not verified** — ask. Prefer the Read installer to start. |
| Wants fixed tools instead of AI-written Python | `mcp-servers-for-revit` (MIT, TS + C# add-in, Revit 2020–2026) or `bimwright/rvt-mcp` (Apache-2.0, 2022–2027). They have **no per-change approval prompt** — dry-run in a copy. |

Don't use bridges that go through pyRevit **Routes** (HTTP port 48884) on a shared machine: pyRevit's own docs say Routes has no authentication.

## 2. Look before you build (read-only)

With pyRevit's runtime, in this order:
1. `get_skill("revit-scripting")` — pyRevit's own contract for scripts; read it before the first run, then the task skill (`modeling`, `views`, `family-editing`, `scheduling`, `drawings`). Don't guess the contract from memory: it changes between pyRevit builds.
2. `get_context` — Revit version, which Python engine (IronPython 2.7 / 3.4 or CPython), active document and view, levels, policy.
3. One `run_query` to list what exists: levels with elevations, wall / floor / roof / ceiling types, loaded door and window families and their types, materials. **Use the exact names it returns — never invent a type or family name.**
4. `lookup_revit_api` whenever you're unsure of a signature: it reflects the API of the Revit that's actually running, which beats any memory of revitapidocs.

Report what you found in metric (Revit stores feet internally). Read `references/revit-api-essentials.md` before writing the first modify script.

## 3. Build in small approved stages

- Restate the plan first: what, main sizes, stages (levels → walls → floors → openings → roofs → materials → views). Ask only what's missing.
- **One `run_modify` per stage**, with a clear `title` (it becomes the Revit prompt text and the undo name `Agent: <title>`). Use `dry_run=true` first when a stage creates or deletes more than a handful of elements.
- Tag what you create (Comments = `ai:<stage>`), so a stage can be re-run by deleting only its own tagged elements. Never touch elements the user didn't ask about.
- After each stage tell the user "approve in Revit (Keep / Discard)", then `capture_view` (`3d` for massing, the plan for layout) and **look at the image** before the next stage. Wrong? Fix it in a new run, not by stacking hacks.
- Large jobs (a statue, a block, a site): keep the data in a workspace module, batches of a few hundred elements, raise `timeout_s` (max 3600). Native walls/floors/roofs first; DirectShape only for sculptural massing the user accepts as non-BIM.
- When done, remind the user to save — saving, syncing and exporting are blocked while a run is active.

Sculptural things like the Statue of Liberty are usually DirectShape meshes or stacked massing — they look right in 3D but aren't schedulable walls/floors. Say so.

## 4. Revit → web (three.js) and the colour-map video

Read `references/revit-to-web.md`. The free routes:
- **glTF exporter add-in "Leia"** (e-verse, MIT, free on the Autodesk App Store): exports a 3D view to glTF/GLB; each glTF material is named after the Revit material and coloured with its *shading colour*. Shortest path to a colour map.
- **IFC route**: Revit's own IFC export → `scripts/ifc_material_colormap.py` (below) → web-ifc / That Open Engine in three.js, painting each element by its material. Or IfcConvert → OBJ with `--use-material-names`.
- **FBX** (built into Revit) → Blender → glTF, when you also want Blender lighting and the `archviz-web-walkthrough` pipeline.

For the colour map: swap every material for an unlit `MeshBasicMaterial` with one flat colour per material, turn tone mapping off, and (for exact masks) antialiasing off. Plan the camera path in the browser, then render frames and encode with ffmpeg (`archviz-cinematic` covers the encoding).

```bash
python scripts/ifc_material_colormap.py model.ifc -o colormap.json --summary
python scripts/ifc_material_colormap.py model.ifc --multi set      # layered walls coloured by the whole wall type
python scripts/ifc_material_colormap.py model.ifc --colors source  # keep Revit's own material colours
```
It's standard-library Python, read-only, and prints which building elements have **no material** (fix those in Revit before rendering, or they'll all share one "no material" colour). Element keys are IFC `#ids`, which are web-ifc's `expressID`. Test fixture: `assets/sample-colormap.ifc`.

## 5. Hand off (separate skills — ask first)

- IFC editing, validation, clash checks → `ifc-mcp`; open BIM authoring in Blender → `bonsai-project-setup` → `bonsai-walls` / `bonsai-openings` / `bonsai-roofs` / `bonsai-stairs` / `bonsai-spaces-grid` → `bonsai-drawings`.
- Building from a floor plan image → `floorplan-to-blender` (its layout JSON's levels / walls / openings map onto Revit levels, `Wall.Create` and family instances just like onto Bonsai).
- DWG work → the `autocad` MCP (user has AutoCAD in the membership).
- Interactive web tour, collision, hotspots → `archviz-web-walkthrough` (+ `threejs-web` for the three.js parts).
- Camera moves, film encoding, and a colour-map pass rendered in Blender instead of the browser → `archviz-cinematic`; colour-map stills or video → photoreal stills or clips → `ai-archviz-render` (ControlNet, or Wan2.2 Fun Control / VACE driven by the colour-map video; local ComfyUI is free, its paid services need the user's OK).
- Quantities from the model → `quantity-surveyor` (rates and measurement rules come from the user).

## Limits (say them, don't hide them)
- Nothing here was run against a live Revit: the authoring machine has no Revit. pyRevit's runtime is labelled **experimental**; its docs validate Revit 2024 and 2025 only. Tool names and commands are from pyRevit 7.0.0 release notes and docs (2026-10-06) — if `get_context`/the tool list differ, trust what's running.
- `readonly` policy is not a sandbox: `run_query` still runs arbitrary Python as the user (file system, network). Rollback protects the model, not the PC. Only connect trusted agents and don't paste untrusted text into prompts that drive Revit.
- pyRevit keeps every script, response and capture in plain text under `%APPDATA%\pyRevit\agent` for 14 days — mention it for confidential projects.
- Autodesk's official MCP: details come from Autodesk blog posts; tool names, Claude Code/Codex setup and whether it uses cloud credits are **not verified**.
- Whether IfcConvert's `.glb` keeps material names is **not verified** (its docs list `--use-material-names` for OBJ/DAE only). Leia's App Store build for Revit 2027 is **not verified** (the repo has a 2027 project).
- `ifc_material_colormap.py` colours each element by one material: the first layer/constituent by default, or the whole set with `--multi set`. True per-layer colouring needs geometry split by layer (IfcConvert `--enable-layerset-slicing`). It parses STEP text only (no `.ifczip` / `.ifcxml`); ~12 MB takes about 5 s.

Sources: see `references/connectors.md`, `references/revit-to-web.md`, and the research note `docs/skill-batches/archviz-batch2-2026-10-22-research/revit-mcp.md` in the T1 repo.
