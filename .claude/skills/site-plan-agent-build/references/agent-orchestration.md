# Running one agent per zone

Why it's done this way (sources in the research note): subagents start with their own empty context and don't see your conversation; vague briefs make them duplicate work or misread the task; they don't coordinate well in real time; and every action carries hidden decisions (scale, style) that clash when agents choose separately. So: decide everything shared up front, give each agent a complete brief and its own files, and keep integration with the lead.

## Roles
| role | does | never does |
|---|---|---|
| Lead (main session) | talks to the user, writes and checks `site-plan.json`, writes shared files and stubs, dispatches, reviews, integrates, edits the plan | builds a zone itself while its agent is running |
| Zone agent | builds only its zone in only its files, self-checks, reports | edits the plan, shared files or another zone's files; asks the user (it can't) |
| Review agent (optional, fresh) | screenshots from reference cameras, fills the checklist | fixes code (it reports; the zone agent fixes) |

## Tool notes (verify on the installed version)
- **Claude Code**: dispatch with the Agent tool, several calls in one message to run them in parallel (default limit 20 at once). Each subagent loads CLAUDE.md but not your conversation. `isolation: worktree` (in an agent definition or on the call) gives a separate git worktree — then each agent commits on its own branch and the lead merges. Without worktrees, file ownership is what keeps them apart. Agent teams (shared task list, messaging) exist but are experimental and off by default (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`); their docs say "Break the work so each teammate owns a different set of files."
- **OpenAI Codex**: subagents are enabled by default in current releases (`[agents]` config) and are spawned when you ask for them; reusable roles go in `.codex/agents/<name>.toml` with `name`, `description`, `developer_instructions`. They inherit the parent's sandbox and approvals. Codex's own docs warn that parallel write-heavy agents can create conflicts. An older docs page calls multi-agent experimental — check the installed version.
- Without subagents (or if the user prefers): run the same briefs one after another in the main session. Slower, same result.

## Brief template (copy, fill, send one per zone)
```
You are building zone "<zone_id>" of a procedural scene. You have no other context than this brief.

OBJECTIVE
Build <description> exactly where site-plan.json puts it, procedurally in code (no downloaded models).

READ FIRST (read-only)
- <abs path>/site-plan.json  — the single source of truth. Your zone, elements, water, paths and interfaces are copied below.
- <abs path>/src/shared/materials.js, kit.js — use these materials and helpers; do not edit them.
- Reference photos for your zone: <paths> (camera notes: <...>)

YOUR SLICE OF THE PLAN
<paste the zone object, its elements, water, paths, interfaces>

FILES YOU OWN (create/edit only these)
- <abs path>/src/zones/<zone_id>.js
If you need a change anywhere else (shared kit, the plan, a neighbour's file), stop and report it.

CONTRACT
- three.js: export function build<Zone>(ctx) returning a THREE.Group. Children in site coordinates (metres, x east, z south, y up). ctx = { THREE, materials, kit, seed }.
- Blender: def build(ctx) creating everything under a collection named "ZONE_<zone_id>"; site → Blender axes as in the plan's "axes".
- Ground is y = <ground_y>. Every object rests on the ground, its support's top, or the water bed — nothing floats, nothing sinks, nothing overhangs without support.
- Stay inside bbox <bbox>; eaves and branches included.
- At each interface point, match the note exactly: <interfaces>.
- Use the plan's palette only. Instance repeated parts (lanterns, rafters, tiles, petals).
- Deterministic: seeded random only (seed = ctx.seed + "<zone_id>").

DONE WHEN
1. The page/scene loads with only your zone enabled and no console errors.
2. Your group's bounding box is inside the zone bbox (print it).
3. Every element id in your slice exists as a named object (name = element id) at its footprint and height (print a table: id, centre, size, base, top).
4. Screenshots from the cameras listed with your reference photos are saved to <abs path>/review/<zone_id>/.

RETURN (short)
- files changed; the table from (3); the bbox from (2); screenshot paths
- every number you had to guess; anything you could not do; any change you need from the lead
```
Keep briefs complete but short; the plan file carries the detail. Ask for the screenshots and tables as files and paths, not pasted in the reply (cheaper and avoids the "game of telephone").

## Review loop (per zone)
1. Render the zone from a camera that matches each reference photo (same position/height, same focal length; for three.js set `camera.position`, `lookAt`, `fov` from the photo notes; capture the canvas or use Playwright `page.screenshot()`).
2. Put reference and screenshot side by side (same height) and go through the checklist. Each line gets pass / fail + what is visible:
   - silhouette and proportions (height-to-width, roof curve, tier count, how much each tier shrinks)
   - the parts the user listed are present (bracket sets under every roof, finial parts, railing posts on the bridge, lantern sections)
   - colours from the palette, material roughness reads right (lacquer vs. stone vs. gravel)
   - grounding — look from a low angle: no gaps under podiums, lanterns, rocks; no floating eaves
   - zone edges — nothing crosses the bbox, interface paths line up
   - real glass with an interior behind it where there are windows (T1 rule); doors that open onto something
   - performance — draw calls / triangles reasonable for the target (see `threejs-performance`)
3. Send the zone agent a numbered fix list (≤ 7 items, most visible first). Re-review. Stop after 2–3 rounds and tell the user what is still off.

About metrics: SSIM-type scores assume two aligned images of the same scene ("corresponding locations in two images"); a render and a real photo differ in lens, light and detail, so the score says little about likeness. Use pixel diffs only for regression — same code, same camera, before vs. after a change.

## Integration (lead)
1. Merge worktrees/branches if used; resolve nothing by hand in zone files — send it back to the owner.
2. Re-run `check_site_plan.py` (the plan may have changed during review).
3. Load all zones. For every zone print its real bounding box against the plan bbox; for every element id, real centre/size vs. plan (tolerance ~0.1 m).
4. Walk the interfaces: same path width and level on both sides, no gap, no z-fighting where ground planes meet (one ground owner, or offset decals by a few mm).
5. Whole-scene screenshots from the reference cameras and a low-angle orbit to catch anything floating.
6. Report to the user: what was built, what was checked, what was guessed, what is still off.
