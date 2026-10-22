---
name: site-plan-agent-build
description: Build a whole 3D scene (temple complex, village, campus, park, street block) entirely from code with several agents in parallel without them colliding — first write one site-plan JSON in metres (zones with bounding boxes and owner agents, every building's footprint, height and anchor, water, paths, interface points), check it with a script that catches overlapping zones, buildings in the pond, floating objects and two agents owning one file, then brief one Claude Code or Codex subagent per zone, compare each zone with reference photos from matching cameras, integrate, and plan close-up-then-pull-out shots. three.js/WebGPU or Blender bpy. Use whenever the user wants a procedural scene with no downloaded models, a "built entirely by code" showcase like the viral Japanese temple video, several agents building one scene, or a site plan before modelling — even if they only say "用代码盖建筑", "多个代理一起盖", "寺庙场景", "程序化场景", "没有模型全部代码生成", "分区建造", "先画总平面图", "每个区一个 agent", "塔盖进池塘里了".
---

# Site plan → parallel agents → one scene

The viral "temple built only by code" videos (unverified which tool the author used) work because of their first prompt: **draw the site plan first, every building's position in metres**. Without it each agent invents its own scale, origin and style, and — as the author put it — the pagoda ends up in the pond. Research on multi-agent systems says the same thing in general terms: parallel agents make hidden decisions (scale, style, coordinates) that conflict, and they don't coordinate well on their own (sources in `docs/skill-batches/archviz-batch2-2026-10-22-research/site-plan-agent-build.md`). So this skill moves every shared decision into one checked file before any agent starts, gives every agent its own ground and its own files, and keeps integration and review with the lead.

T1 rules apply throughout: ask before using this skill and each one it hands off to; say before you send subagents out (they cost tokens and run a while); nothing floats, every building stands on the ground or a podium, windows are real glass with real interiors behind them; free tools only.

## Workflow

### 1. Agree the brief (lead, with the user)
Ask once, together: what the scene is, how big (site size in metres), the target (three.js in a browser, or Blender), real-time or rendered film, reference photos (ask for files, don't scrape), the "must have" list (e.g. five-storey pagoda, red arched bridge, raked gravel garden, stone lanterns, gold-trimmed pillars, cherry trees), and how faithful it must be to a real place. Subagents can't ask the user questions (Claude Code removes AskUserQuestion from them), so every question gets asked now.

### 2. Write the site plan (the step that matters most)
Write `site-plan.json` in the schema of `references/site-plan-schema.md`; start from `assets/example-site-plan.json` (a small temple complex). It holds: site bounds and ground level, the grid, style and palette, zones (bbox + owner agent + the files that agent owns), every element (footprint, height, anchor, base_y), water, paths, interface points where zones meet, and optionally the shots. Place landmarks first (pagoda, hall, gate), then access (paths, bridge), then repeated detail (lanterns, trees).

For real architecture, take proportions from reliable sources and say which numbers are guesses — `references/site-plan-schema.md` has a short cited temple table (pagoda bays and tiers, sōrin parts, torii members, taikobashi, karesansui). Show the user the plan as an SVG before going on.

### 3. Check it — no agent goes out until it passes
```bash
python scripts/check_site_plan.py site-plan.json --svg site-plan.svg
```
Read-only, standard library. ERRORs: zones overlapping or outside the site, elements outside their zone, two elements overlapping in plan and height, a building standing in water (unless it is a bridge with abutments on both banks or sits on the water bed), height ≤ 0, anything floating or sunk relative to the ground or its support, overhanging its support, missing supports or support loops, paths running into water with no bridge, interface points not on the shared zone edge, one file owned by two agents. WARNs: paths running into buildings (mark gates `passable`), clearance too small, camera moves that fly through buildings or don't actually pull out. Fix every ERROR; explain or fix every WARN. Open the SVG with the user (red outline = problem).

### 4. Set up the code skeleton (lead only)
Before dispatching, the lead writes the shared files listed in `shared_files` — materials/palette, a small kit of helpers (podium, roof tier, lantern, tree), the entry file that imports every zone module, and an empty stub for each zone with the agreed signature. Zone agents may **read** shared files but never edit them; if they need a change they report it. Commit this skeleton so every agent starts from the same state.

### 5. Brief one agent per zone
Read `references/agent-orchestration.md` — it has the brief template. Each brief contains the objective, the zone's slice of the plan (copied in, plus the plan path), the files it owns and may not leave, the interface contract (function signature, coordinate frame, ground level), style rules, the done-check, and what to return. Then dispatch them in parallel:
- **Claude Code**: Agent tool subagents (background by default in many setups; each has its own context window and doesn't see your conversation, so the brief must be complete). Optional `isolation: worktree` gives each its own git worktree; merge afterwards. Agent teams are experimental and off by default — only if the user has them enabled.
- **OpenAI Codex**: subagents are on by default in current releases and run only when you ask for them; custom agents live in `.codex/agents/*.toml`. Codex warns that parallel write-heavy agents can conflict — the file-ownership rule above is what prevents that. If subagents aren't available, run the zones one after another with the same briefs.
3–5 agents is plenty; one agent may own two small zones.

### 6. Review each zone against references
When a zone agent reports, the lead (or a fresh review agent) screenshots that zone from the **same camera as each reference photo**, puts them side by side and walks the checklist in `references/agent-orchestration.md` (silhouette and proportions, tier counts, colours, parts present, grounding, nothing poking past the zone bbox). Pixel metrics like SSIM need aligned images of the same thing and are a poor judge of "looks like the photo"; use them only to detect unintended changes between two versions from the same camera. Send fixes back as a short numbered list; two or three rounds per zone is normal.

### 7. Integrate (lead only)
Load all zones, re-run the checker, then check in the scene: each zone's actual bounding box against its plan bbox, interface points line up (path widths and levels match), nothing floats (look from low angles), no z-fighting at zone edges, frame rate on the target device. Whole-scene screenshots from the reference cameras again.

### 8. Shots
Read `references/shot-plan.md`: ~10 shots, each opening on a small object (lantern cap, bracket set, a petal on the gravel) and pulling back until the landmark is in frame. Shots can live in the plan's `shots` array so the checker catches camera paths through walls. Blender films → `archviz-cinematic`; three.js camera rigs → `threejs-camera-controls-and-rigs`.

## Hand-offs (ask before using each)
- three.js: `threejs-procedural-buildings-and-cities` (massing, facades, placement compiler), `threejs-procedural-geometry` (roof curves, arches, sweeps, instancing), `threejs-object-sculptor` (one object from photos, e.g. a lantern), `threejs-procedural-vegetation` (cherry trees), `threejs-water-optics` (pond), `threejs-sky-atmosphere-and-haze`, `threejs-visual-validation`, `threejs-performance`.
- Blender: `floorplan-to-blender` (one building's walls/openings from a layout), `parametric-facade`, `archviz`, `archviz-cinematic` — all through the `blender` MCP, which needs its own OK.
- Multi-agent discipline: `superpowers:dispatching-parallel-agents`, `superpowers:subagent-driven-development` (Claude Code plugins; Codex skips them).

## Limits (say them, don't hide them)
- The checker works in plan view with boxes: footprint × height. It can't see roof curves, eaves overhang, terrain slopes (`anchor: terrain` only gets a warning), or actual geometry — the integration step checks that.
- Overlap is measured by sampling (default 0.05 m² counts); thin features under that slip through.
- The orchestration and review steps were written from the docs and research notes, not run end-to-end on a real scene when this skill was made; only `check_site_plan.py` was tested (on the example and 18 broken copies).
- Codex subagent tool names aren't documented on the page that was read; the skill says "ask Codex to spawn subagents" rather than naming a tool. Behaviour depends on the installed version.
- Temple proportions in the schema reference are examples from cited sources; the 10:9:8:7:6 roof ratio and lantern proportions are unverified starting points.
