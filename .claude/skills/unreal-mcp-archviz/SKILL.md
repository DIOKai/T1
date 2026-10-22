---
name: unreal-mcp-archviz
description: Drive Unreal Engine 5 through an MCP server to turn a Blender house into interactive archviz — import it (FBX/glTF/USD at the right scale), light it with Lumen, render cinematics with Movie Render Graph (Path Tracer or Deferred), package a first-person walkthrough .exe, and build a local HTML control panel that moves, rotates, scales, swaps and re-materials furniture through the Remote Control API. Use whenever the user mentions Unreal, UE5, UE 5.8, Lumen, Nanite, Unreal MCP, an interactive house tour, a real-estate listing turned into a walkable 3D apartment, a "Zillow → Blender → Unreal" reel, a web dashboard that changes furniture in a 3D scene, an interactive apartment with a unit/lot info panel, compass minimap, time-of-day slider, section (cut) view, measuring tool or material changer bar, or Pixel Streaming — even if they only say "虚幻引擎", "UE5", "Unreal 看房", "互动展示", "互动看房", "漫游", "换家具面板", "网页控制家具", "把房子放进虚幻", "户型信息面板", "日照时间", "剖切", "测量工具", "换材质".
---

# Unreal MCP archviz

The reel version ("listing → Blender → Unreal → HTML dashboard that swaps the sofa") hides three hard parts: **the MCP can run any code in the editor**, **Blender scale/material/wall-thickness mistakes only show up after Lumen is on**, and **the web panel needs a stable function to call**, not raw actor paths. This skill does those three carefully.

T1 rules apply: ask before using any MCP or other skill, before installing anything (UE, plugins, Node, uv, pip packages), and before destructive editor operations. Free and local only — no paid services, no cloud GPUs, no tunnels. Never write tokens or passphrases into tracked files.

## 0. Before anything: check the setup (ask, don't assume)
Ask in one go:
- UE version (5.8? 5.4–5.7? Launcher or source build) and whether the project is Blueprint-only or C++.
- Is the project in git / Perforce, and is it saved? (Required before any MCP session — see Safety.)
- Hardware: Epic recommends 32 GB RAM, 8 GB+ VRAM, DirectX 12 GPU with current drivers, Windows 11. Lumen hardware ray tracing needs RTX 2000 / RX 6000 / Arc A or newer; software Lumen runs from about a GTX 1070 (SM6).
- Disk: Epic gives no official number; users report ~70 GB for UE 5.8.1 installed (39 GB download), up to 115 GB via Launcher, 160–400 GB for source builds. Reserve **at least 150 GB** on an NVMe SSD for engine + project + DerivedDataCache + packaged builds (experience value).
- What they want out: stills, a video, a walkthrough .exe, a web control panel, or all.

If UE isn't installed, tell the user (install is their action through the Epic Games Launcher, needs an Epic account). Mention licensing (step 6) at this point too.

## 1. Choose the MCP server
Read `references/mcp-servers.md` for the comparison table, exact install lines for **Claude Code and Codex**, and security details. Short version:

| Situation | Use | Why |
|---|---|---|
| UE 5.8 | **Epic's built-in Unreal MCP** (Experimental) | free, no third-party code; HTTP `http://127.0.0.1:8000/mcp`; console `ModelContextProtocol.GenerateClientConfig ClaudeCode` (or `Codex`, `All`) writes the client config |
| Want more tools + guardrails, any UE 5.0–5.8 | **EngineWire** (ChiR24/Unreal_mcp, MIT) | per-project capability token, 62 destructive ops need per-call consent, asset paths limited to `/Game` `/Engine`; needs its C++ plugin (prebuilt binaries for Blueprint projects, exact engine minor version) |
| UE 5.0–5.7, no compiling | **runreal/unreal-mcp** (MIT, Python remote execution) or **unreal-engine-mcp** (PyPI, MIT, documents Codex config, few stars) | no C++ plugin |
| — | UEMCP (`uvx uemcp`) | only if the user insists: 0 GitHub stars, PyPI says UE 5.0–5.6 while README says 5.0–5.7 |
| — | chongdashu/unreal-mcp, ziggymar/unreal-mcp | don't: self-declared experimental and apparently unmaintained / repo 404 |

Quick lines (Epic built-in, UE 5.8):
```bash
# Claude Code (the generated .mcp.json is authoritative; this equivalent line is unverified)
claude mcp add --transport http unreal-mcp http://127.0.0.1:8000/mcp
# Codex (unverified against the generated TOML)
codex mcp add unreal-mcp --url http://127.0.0.1:8000/mcp
```
```toml
# ~/.codex/config.toml
[mcp_servers.unreal-mcp]
url = "http://127.0.0.1:8000/mcp"
tool_timeout_sec = 600   # UE imports / shader compiles often exceed the 60 s default (experience value)
```
With Tool Search on, `tools/list` only shows `list_toolsets`, `describe_toolset`, `call_tool` — call `list_toolsets` first. Tools run serially on the game thread: **never call them in parallel**. Expect 5–15+ minutes per complex response (Puget Systems test); it speeds up work you understand, it doesn't design systems for you.

## Safety (all servers)
Every one of these servers lets the agent run arbitrary Python / console commands / asset deletes inside the editor. So:
1. **Project in version control and saved** before the first call; commit before each big step (import, material pass, lighting pass). Back up a project with no VCS before the first session.
2. **Localhost only.** Keep the default 127.0.0.1 binding; never 0.0.0.0, never a tunnel, never raise the multicast TTL above 0 for remote-execution servers. Epic's MCP and Python remote execution have **no authentication**.
3. **Ask before destructive operations**: deleting/replacing assets or actors, `save all`, overwriting a level, running a console command that changes project settings, packaging over an existing build folder.
4. Keep `bEnableRemotePythonExecution`, `bAllowConsoleCommandRemoteExecution` and any-remote-function-call settings **off** in Remote Control unless the user asks.
5. Tokens (EngineWire `Saved/MCP/capability-token`, Remote Control passphrase) stay in env vars or untracked files — never in `.mcp.json`/`config.toml` that gets committed.

## 2. Blender → Unreal
Read `references/blender-to-unreal.md`. The rules that break scenes if skipped:
- **Separate meshes**: walls, floors, ceilings and each furniture piece are separate objects. Lumen does not support a whole room plus furniture as one mesh.
- **Walls ≥ 10 cm thick** (software Lumen leaks light through thinner walls). `floorplan-to-blender` layouts already carry thickness — check it.
- **Scale**: Blender metres → UE centimetres. FBX: Apply Scalings = **FBX Units Scale** (not FBX All), Apply Unit on, Forward −Z / Up Y. After import an actor showing Scale (100, 100, 100) instead of (1, 1, 1) means the export was wrong — fix the export, don't rescale in UE. glTF (via Interchange, UE 5.2+): unit conversion unverified — measure a door after import (should read ~200–210 cm).
- **Materials**: only Principled BSDF values survive (base colour, roughness, metallic, alpha, IOR, normal via Normal Map node). Procedural/emission/SSS/clearcoat don't — bake textures or rebuild in UE. Build **one master material + material instances**; swapping furniture finish = swapping instances (which the web panel needs).
- **Furniture pivots at bottom centre** so the panel's move/scale behaves (experience value).
- No lightmap UVs needed with Lumen; turn off Generate Lightmap UVs when importing Nanite meshes.
- **Nanite**: on for opaque/masked high-poly furniture and shell; **glass and anything translucent cannot be Nanite**.

Import through the MCP (asset import tool or `unreal` Python in the editor) into `/Game/Archviz/<Project>/…`, then place in a new level. Verify: actor scales are 1, a door measures ~2 m, no mesh floats (check from the side), every window has a real room behind it (user rule from earlier projects).

## 3. Light with Lumen
Read `references/lumen-and-rendering.md`. Project Settings: Dynamic GI = Lumen, Reflections = Lumen, Generate Mesh Distance Fields on (software Lumen), hardware ray tracing on if the GPU allows. Indoor: Post Process Volume (unbound) with exposure fixed for the interior, Lumen Scene Detail up if small objects go black in reflections, Max Trace Distance / thicker walls for leaks, Hit Lighting for Reflections for the best mirrors (HWRT only). Small emissive meshes get culled — enable Emissive Light Source on them. Lumen doesn't do Forward Shading or VR.

## 4. Cinematics (Movie Render Graph)
Level Sequence with a Cine Camera Actor (camera moves can follow `archviz-cinematic`'s shot list), then Movie Render Graph: Temporal Samples on the Sampling Method node (global), Spatial Samples on the Renderer node (per layer); each layer is **Path Tracer** (ground truth, slow — one user reports ~7 min per HD frame indoors) or **Deferred** (Lumen, fast). Render a 10-frame test at low samples before the full sequence and tell the user the estimated total time. MRG still lacks some MRQ features (ProRes, high-resolution tiling, nDisplay — check current docs). Whether MRG is out of beta in 5.8: unverified.

## 5. Interactive walkthrough + web control panel
- Interactive features from the Unreal archviz reels (unit/lot info panel, compass + minimap, time of day, section cut, measuring tool, master material + instances for the changer bar): read `references/interactive-features.md`. Put them all on one `BP_ArchvizController` actor so UMG and the web panel call the same functions.
- Walkthrough: First Person template pawn, collision on walls/floors (simple box collisions on furniture), then Platforms > Windows > Package Project (or `RunUAT BuildCookRun`). Packaging is long — ask first, and package to a fresh folder.
- Control panel: read `references/remote-control-panel.md`. Enable the **Remote Control API** plugin (HTTP 30010, WebSocket 30020, bound to 127.0.0.1). Prefer a **FurnitureManager Blueprint actor** with BlueprintCallable `SetSlotMaterial(Slot, MaterialInstance)`, `SwapSlotMesh(Slot, Mesh)` etc., so the page doesn't depend on long actor paths and the packaged build works (no editor Python there).
- `assets/furniture-panel/index.html` is a working, dependency-free panel: edit its `CONFIG` block (actor object paths, material-swap function), open it in a browser on the same PC. It sends `PUT /remote/object/call` with `SetActorLocation` / `SetActorRotation` / `SetActorScale3D` and logs every request/response. It refuses non-localhost hosts unless `ALLOW_NON_LOCALHOST_TARGET` is set to true by hand.
- Probe the server first (read-only, never writes):
  ```bash
  python scripts/rc_probe.py                       # GET /remote/info + /remote/presets
  python scripts/rc_probe.py --describe "/Game/Maps/House.House:PersistentLevel.Sofa_2"
  ```
- Packaged build: launch with `-RCWebControlEnable -RCWebInterfaceEnable`, otherwise Remote Control is off.
- Opening `index.html` from `file://` sends `Origin: null`; if UE rejects it, either serve the folder with `python -m http.server 8080 --bind 127.0.0.1` and set `AllowedOrigin`, or keep restrictions off on a localhost-only server (untested combination — check the log).
- Pixel Streaming (browser/phone view of the running app): local / LAN only, free. Public hosting needs your own server or cloud GPU — **costs money, ask first and don't recommend it by default**. The signalling-server setup downloads files (`get_ps_servers`, `setup.bat`) — ask before running.

## 6. Licensing (tell the user before commercial use)
Read `references/licensing.md`. Summary: free for students, hobbyists and companies under US$1M annual gross revenue. Non-game companies above US$1M need an Unreal Subscription, **US$1,850 per seat per year** (archviz renders, videos, linear content). Games: 5% royalty above US$1M lifetime gross. Renders and videos you deliver to a client carry no royalty; a walkthrough app made for a single client as work-for-hire was royalty-free under the old EULA, but if the client later sells it to the public, royalties may apply. Epic's license/EULA pages could not be fetched when this skill was written — **tell the user to read the current EULA at unrealengine.com/eula before selling anything**.

## 7. Report to the user
UE version + MCP used, what was imported (counts, any scale fixes), lighting settings changed, render settings and time, packaged build path, panel config used, rc_probe output, every step skipped or unverified, and every setting changed in Project Settings (so they can revert).

## Limits (say them, don't hide them)
- Written from documentation and research notes; **not run against a live Unreal Editor** (no UE on the authoring machine). The panel and `rc_probe.py` were tested only against a local stub HTTP server.
- Epic's Unreal MCP is Experimental: tool names and formats can change between 5.8.x releases — always `list_toolsets` instead of trusting names here.
- The exact files `GenerateClientConfig` writes for Claude Code/Codex weren't seen; the equivalent `claude mcp add` / `codex mcp add` lines are derived from general syntax.
- Remote Control default security values, the web-app port (30000?) and CORS behaviour with `file://` are unverified.
- Blueprint graphs can't be written from Python; the FurnitureManager actor's logic is built by hand or via an MCP that supports Blueprint nodes (EngineWire).
- Related skills (ask before using): `floorplan-to-blender` (the house), `archviz` + `set-dressing` + `free-3d-assets` (furnish), `archviz-cinematic` (shots), `archviz-web-walkthrough` (browser-only alternative without UE), `impeccable`/`frontend-design` (prettier panel).
