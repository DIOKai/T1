---
name: sketchup-mcp
description: Use SketchUp with AI — Trimble's official SketchUp connector for Claude (cloud modelling, returns a .skp), the open-source sketchup-mcp2 server for desktop SketchUp, and the free route of bringing SketchUp models into Blender (Sketchup_Importer) to turn a basic model into a cinematic render. SketchUp's useful tiers are PAID, so ask before using any paid part and offer the free Blender route. Use whenever the user mentions SketchUp, .skp files, Trimble, 3D Warehouse, SketchUp MCP, or wants to model or render something they built in SketchUp — even if they only say "草图大师", "SU", "SketchUp建模", "把SU模型做成电影感", "skp转Blender", "连接SketchUp".
---

# SketchUp MCP (付费)

**SketchUp's desktop and export features are paid, and the official AI connector is free only up to a quota. Before using anything here, ask the user what they have (Free / Go / Pro / Studio, or just a .skp file) and whether they want to use the paid part. Offer the free route: .skp → Blender → `floorplan-to-blender` / `archviz`.** Never suggest buying a plan (T1 rule, 2026-10-22).

## What each SketchUp plan can do
Official plans page, 2026-10-22, USD per user per month billed yearly: **Go $10.75** (web + iPad only, no desktop), **Pro $33.25** (desktop + LayOut), **Studio $71.58** (adds V-Ray and Revit import). SketchUp Free (web) is for hobby/non-commercial use (the forum says so; the official wording is 未验证). Go's month-to-month price of $19.99 comes from engineering.com and is 未验证 on the official page.

Export formats (official help table):

| Format | Free | Go | Pro | Studio |
|---|---|---|---|---|
| .stl | ✓ | ✓ | ✓ | ✓ |
| .dae, .fbx, .obj, .3ds | ✗ | ✓ | ✓ | ✓ |
| glTF, .usdz, .ifc | ✗ | ✗ | ✓ | ✓ |

STL has no materials or UVs, so SketchUp Free can't feed a good render directly. The free path is the **.skp file itself** into Blender (below).

## Option A: Trimble's official connector (Claude; cloud; free quota)
- Released 2026-04-28, Trimble's first MCP connector. Enable "Trimble SketchUp" in Claude's connector settings (claude.ai/customize/connectors) and sign in with a **Trimble ID**. No SketchUp install needed.
- Claude models in a **cloud SketchUp session**, checking dimensions as it goes. You can point at screenshots to request changes, and get a 2D preview plus a **.skp download link** that opens in SketchUp Web/Desktop/iPad/iPhone.
- Registry tools (2026-10-22): `build_model`, `get_docs`, `save_model`; endpoint `https://api.sketchup.com/mcp/v1/sketchup/mcp`. A third-party review describes a Python-execution tool instead of `build_model` (未验证): trust the tool list you see once connected.
- Free quota: Trimble says the free entitlement saves **up to 30 models**; engineering.com says **30 .skp per month** without a subscription and unlimited with a paid one. Total vs monthly is 未验证. Beyond the quota it needs a paid entitlement: ask, don't push.
- Reportedly it can only **create new** models, not edit or render existing ones, and models don't persist between sessions, so download them (third-party claim, 未验证).
- Ask before connecting: it uses an external service and a login, and the prompts and models go to Trimble's cloud.
- **Claude Code:** connectors enabled on claude.ai may show up in Claude Code when signed in with the same claude.ai account. Adding it by hand (`claude mcp add --transport http sketchup https://api.sketchup.com/mcp/v1/sketchup/mcp`) is an inference (未验证; Trimble's OAuth may only allow Claude's own connector flow).
- **Codex:** unknown. Trimble says Claude is the only third-party assistant it officially supports, and no Codex instructions exist. Don't promise it works there; use option B or C in Codex.

## Option B: zinin/sketchup-mcp2 (open source, MIT; needs desktop SketchUp = Pro or Studio, paid)
- Most actively maintained (v0.4.0, 2026-10-20). A Ruby extension (.rbz) inside desktop SketchUp opens `127.0.0.1:9876`; the client runs with `uvx sketchup-mcp2`.
- Tools: create/delete/transform, boolean, chamfer/fillet, joinery, `export_scene` (skp/obj/dae/stl/png/jpg), `get_viewport_screenshot` (SketchUp 2026+), `undo`, and `eval_ruby` (arbitrary Ruby). Each change is wrapped in one operation, so a single undo reverts it.
- **Security:** `eval_ruby` is **on by default** and can run any Ruby with the user's file access. Suggest turning it off (Plugins → MCP Server → Settings) unless a task really needs it, and ask before any `eval_ruby` call. Save the .skp first.
- Claude Code (`.mcp.json` in the project, or `claude mcp add`), as in the README:
  ```json
  {"mcpServers": {"sketchup": {"command": "uvx", "args": ["sketchup-mcp2"],
    "env": {"SKETCHUP_MCP_HOST": "127.0.0.1", "SKETCHUP_MCP_PORT": "9876", "SKETCHUP_MCP_TIMEOUT": "60"}}}}
  ```
- Codex (`~/.codex/config.toml`). The README has no Codex section; this is the generic Codex format (未验证):
  ```toml
  [mcp_servers.sketchup]
  command = "uvx"
  args = ["sketchup-mcp2"]
  env = { SKETCHUP_MCP_HOST = "127.0.0.1", SKETCHUP_MCP_PORT = "9876", SKETCHUP_MCP_TIMEOUT = "60" }
  ```
- Others seen (not recommended over zinin): mhyrr/sketchup-mcp (popular, README says MIT but the repo has no LICENSE file, `eval_ruby` too), andyluu98/vn-sketchup-mcp (MIT fork with Claude Code/Codex installers), Shattenjagger/sketchup-mcp-bridge (MIT), SidhNor/sketchup-mcp-server (AGPL-3.0; terrain).

## Option C (free): SketchUp model → Blender → cinematic
1. Get a .skp: the user's own file, one from option A, or a 3D Warehouse model (check its licence). Whether SketchUp Free's web app can download .skp is 未验证.
2. Import with **RedHaloStudio/Sketchup_Importer** 0.27.0 (2026-01-26; release notes: supports Blender 5.1 alpha and SketchUp 2026.1). Install: Edit → Preferences → Add-ons → Install (the zip) → enable "Import-Export: Sketchup importer" → File → Import → Import Sketchup Scene (.skp). It has no Linux support. Groups with nested transforms can import wrong; explode and regroup them in SketchUp. Its licence isn't detected on GitHub (未验证), so mention that before the user redistributes anything. Installing an add-on changes Blender: ask first. Older alternative: martijnberger/sketchup_importer (Blender 4.x; 5.x 未验证).
3. If the user has Go or Pro, exporting FBX/DAE/OBJ (Go+) or glTF (Pro+) also works.
4. Clean up in Blender (through the `blender` MCP, ask first): merge duplicate materials, fix flipped normals (SketchUp's back faces), apply real-world scale, and make sure nothing floats (the user's rule).
5. Hand off: walls and openings from a plan → `floorplan-to-blender`; facade patterns → `parametric-facade`; PBR materials, HDRI, sun, camera paths → `archviz` (and `archviz-cinematic` if installed); free models → `free-3d-assets`. Paid importers (SimLab, SKP Editor, Easy Warehouse) aren't recommended.

## Limits
- Nothing here was run: no SketchUp or Blender on the authoring machine. Facts are from the sources below as of 2026-10-22.
- That the open-source servers need Pro/Studio is an inference: they need desktop SketchUp, Go has no desktop app, and Free can't load extensions.
- Connector quota, tool names and edit ability are 未验证 as noted above.

## Sources
- Trimble announcement: https://news.trimble.com/2026-04-28-Trimble-Links-SketchUp-with-Anthropics-Claude,-Bringing-New-Conversational-AI-powered-Capabilities-to-3D-Modeling
- engineering.com: https://www.engineering.com/now-sketchup-has-an-mcp-server-for-claude-based-3d-modeling/
- Third-party review: https://hackceleration.com/resources/integrations/claude/sketchup
- Plans: https://sketchup.trimble.com/en/plans-and-pricing ; export table: https://help.sketchup.com/en/sketchup/using-sketchup-data-other-modeling-programs-or-tools ; Free licence forum: https://forums.sketchup.com/t/export-formats/129818
- https://github.com/zinin/sketchup-mcp2 , https://github.com/mhyrr/sketchup-mcp
- https://github.com/RedHaloStudio/Sketchup_Importer , https://github.com/martijnberger/sketchup_importer
