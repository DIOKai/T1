---
name: rhino-mcp
description: Drive Rhino 8 and Grasshopper from Claude Code or Codex through McNeel's official Rhino MCP (RhinoAI / Rhino-MCP-Platform) — read the scene, run RhinoCommon Python or C#, build Grasshopper graphs, and do Studio-Tim-Fu-style computational design — site/context awareness, rationalising curved forms into flat panels or developable strips, curvature analysis, facade detail with LunchBox/PanelingTools, and modular block distribution. Rhino is PAID software, so always ask before using it and offer the free Blender route (parametric-facade). Use whenever the user mentions Rhino, Rhinoceros, Grasshopper, RhinoCommon, .3dm/.gh files, Rhino MCP, McNeel, or wants Rhino-style parametric architecture with AI — even if they only say "犀牛", "用Rhino做", "草蜢/Grasshopper", "连接Rhino", "Rhino MCP", "曲面合理化", "幕墙分板", "像 Studio Tim Fu 那样".
---

# Rhino MCP (付费)

**Rhino is paid software. Before using anything here, ask the user: do they own a Rhino 8 licence (or are they inside the 90-day trial), and do they want to use it? Offer `parametric-facade` (Blender Geometry Nodes, free) as the alternative.** Never suggest buying Rhino. The T1 rule (2026-10-22) is that skills for paid software may exist, but the paid part is only used after the user says yes.

Price context, for the user's decision only (rhino3d.com/buy, 2026-10-22, USD): commercial $995, upgrade $595, education $195. The evaluation is a one-time **90 days**; after that Rhino can't save and plug-ins don't load, so the MCP plug-in stops working too (an inference from "plug-ins don't load", not tested). Evaluation copies can't be upgraded.

## Why the official server
McNeel, the company behind Rhino, publishes the server: **mcneel/RhinoAI** (formerly RhinoMCP; MIT; actively updated, plugin v0.3.0 on 2026-09-30). It covers Claude Code and Codex, has dedicated Grasshopper 1 and 2 tools, and documents its privacy behaviour. Setup for both clients is in `references/setup.md`.

Alternative when the user wants a hard safety gate: **tanishqbhattad/rhino-mcp** (MIT). It defaults to `safe` mode (no code execution, no destructive edits) and also has `standard` and `developer` modes. It has no Grasshopper tools and is a personal project.
Don't recommend forks without a licence file (sholtomaud, mustafaisildakcom; SerjoschDuering's README says MIT but the repo has no LICENSE file), and don't use the Replicate rendering option some of them offer: it needs a paid API token.

## Safety: read this before the first call
McNeel's own privacy note says `run_python`, `run_csharp` and `run_command` execute **arbitrary code and commands**, and `open_doc`/`save_doc` can read and write **any file your account can reach**. Results (geometry, script output, viewport images) leave the machine through the AI client. So:
- Ask before using the MCP at all, and say that it runs code inside Rhino.
- Have the user **save the .3dm first** (or `save_doc` to a new name). Undo inside Rhino isn't guaranteed to cover script changes.
- **Ask before anything destructive**: deleting objects or layers, `g1_clear_canvas`, overwriting files, `run_command` with commands like `Purge` or `-Delete`, saving over the original.
- Don't open .3dm or .gh files of unknown origin through it; Grasshopper definitions can contain scripts.

## Tools (official server)
From `rhino/plugin/Tools/*.cs`, 2026-10-22:
- Scene: `get_context` (one read-only call: selection, viewports, document and Grasshopper summary). **Call it first.** Also `list_objects`, `get_selection`, `set_selection`, `get_viewport_image`, `set_camera`, `zoom_to_layer`, `zoom_to_object`, `set_layer_material`, `open_doc`, `save_doc`, `close_doc`, `get_commands`, `ask_user`.
- Code: `run_python` (CPython 3 through Rhino's ScriptEditor), `run_csharp`, `run_command` (Rhino command line). In scripts use the injected **`__rhino_doc__`** as the document. The tool description says not to rely on `scriptcontext.doc` / `rhinoscriptsyntax`. So `__rhino_doc__.Objects.AddBrep(b)` (an inference from that description).
- `manage_plugin_commands`: register a C# script as a reusable Rhino command (**Rhino 9+ only**).
- Grasshopper 1: `g1_start`, `g1_search_components`, `g1_describe_component`, `g1_place_component`, `g1_place_slider`, `g1_connect`, `g1_connect_many`, `g1_apply_graph` (sliders + components + wires in one call; prefer it), `g1_get_canvas_graph`, `g1_solve_graph`, `g1_delete_component`, `g1_clear_canvas`. Grasshopper 2: the same with `g2_*` (`g2_solve_canvas`).

The tool list can change between versions; trust what the connected server reports.

## Workflow for Studio-Tim-Fu-style tasks
Studio Tim Fu (London; founder ex-Zaha Hadid Architects) took the Cacao Greenhouse from Midjourney concepts into Rhino + Grasshopper for structure, facade rationalisation and detailing, and ended up with all-flat metal and glass panels. Their "agent" that does context awareness, rationalisation, facade detail and block distribution isn't publicly documented (未验证, probably from social media), so treat the steps below as our method, not theirs.

1. **Context**: `get_context`, then `list_objects` by layer. Report units (`__rhino_doc__.ModelUnitSystem`), tolerance, the site boundary and neighbouring masses. Ask for anything missing: north, setbacks, height limit.
2. **Analyse the form**: sample `Surface.CurvatureAt(u, v)` on a grid and report Gaussian curvature. Near-zero areas can use flat or single-curved panels; high |K| areas need triangles, smaller panels or cold-bent glass.
3. **Rationalise**: choose per zone between planar quads (check each with `Plane.FitPlaneToPoints` deviation), triangles, or developable strips (`Brep.CreateDevelopableLoft`), and unroll strips for cutting (`Unroller`). Report panel count, how many are flat within tolerance, and the worst deviation.
4. **Facade detail**: panels from LunchBox or PanelingTools (`ptPanelGridQuads` has a max-deviation option for flat quads), then mullions by offsetting panel edges and fins on the floor lines. Attractor variation: panel centre → distance → remap. Everything attaches to slabs or structure (the user's rule: nothing floats).
5. **Modular blocks**: slice floors with `Brep.CreateContourCurves`, place modules on top faces only, origins at their base.
6. **Hand over**: `save_doc` to a new name; export to Blender (OBJ/FBX) for `archviz` rendering if the user wants Cycles; give exact numbers.

Code patterns, API signatures and plug-in notes are in `references/facade-techniques.md`.

## Limits
- Not tested on a real Rhino here: no Rhino on the authoring machine. Commands and tool names come from the official repo and docs as of 2026-10-22.
- The two Claude Code install routes (`MCPConnect` prompt vs the `/plugin` marketplace) aren't confirmed: which works best on current versions is 未验证.
- Planarizing with Kangaroo 2 needs Grasshopper; that Kangaroo 2 ships with Rhino 7+ and has a Planarize goal is 未验证.
- Whether PanelingTools comes preinstalled in Rhino 8 is 未验证; LunchBox installs from PackageManager (free, LGPL, Windows-first; Mac only "nominal testing").
- Engineering values (panel sizes, glass, deviations) are for design study; a facade engineer decides the real ones.

## Sources
- Official server: https://github.com/mcneel/RhinoAI ; docs https://mcneel.github.io/RhinoAI/ ; privacy https://github.com/mcneel/RhinoAI/blob/main/PRIVACY.md
- Alternative: https://github.com/tanishqbhattad/rhino-mcp
- Pricing: https://www.rhino3d.com/buy/ ; evaluation: https://www.rhino3d.com/downloadeval/ , https://discourse.mcneel.com/t/rhino-8-evaluation-after-the-90-day-trial-expires/181869
- Studio Tim Fu: https://aecmag.com/features/studio-tim-fu-ai-driven-design/
- McNeel forum, AI category: https://discourse.mcneel.com/c/rhino/artificial-intelligence-rhino/162
