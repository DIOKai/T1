# Unreal MCP servers: comparison, install, security

Researched 2026-10-22. Star counts and versions change; re-check the repo before recommending. "Unverified" = not confirmed on a primary page.

## Comparison

| Server | License | UE versions | Connection | Needs | Tools | Auth / guardrails | Notes |
|---|---|---|---|---|---|---|---|
| **Epic Unreal MCP** (built-in plugin `ModelContextProtocol`) | part of UE | 5.8 | HTTP/SSE `http://127.0.0.1:8000/mcp` (no stdio, no WebSocket) | enable plugins **Unreal MCP** + **All Toolsets**, restart | toolsets (SceneTools, ActorTools, MaterialInstanceTools, ObjectTools…); with Tool Search on only `list_toolsets` / `describe_toolset` / `call_tool` | localhost-only, rejects non-loopback Origin, **no auth** | **Experimental**; custom tools in Python (`unreal.ToolsetDefinition`) or C++, then `ModelContextProtocol.RefreshTools` |
| **EngineWire** (ChiR24/Unreal_mcp) | MIT | 5.0–5.8 | Route A: plugin's Streamable HTTP `http://127.0.0.1:3000/mcp`; Route B: Node 20.19+ stdio ↔ WebSocket 8090 | copy `EngineWire` into `<Project>/Plugins/`, compile (prebuilt binaries only for the same engine minor + platform) | one MCP tool `unreal` (search/describe/execute/configure) over ~400 capabilities | capability token, 62 destructive ops need per-call consent, asset paths limited to `/Game` `/Engine`, chained/quit console commands blocked | ~967 stars; npm stable 0.5.30, 0.6 beta |
| **runreal/unreal-mcp** | MIT | 5.4+ tested | Python remote execution (UDP multicast + TCP) | Node; Python Editor Script Plugin + Enable Remote Execution | ~20 (Python, console, assets, outliner, actors, screenshot, camera) | none; binding to 0.0.0.0 exposes it to LAN | ~116 stars |
| **unreal-engine-mcp** (PyPI) | MIT | 5.0+ (author tested 5.8) | Python remote execution, or `UE_MCP_TRANSPORT=remotecontrol` (HTTP 30010) | Python + pip | 162 incl. glTF/FBX import, BuildCookRun packaging | localhost; multicast TTL 0 default; PyPI provenance | only ~5 stars; the only one documenting Codex config |
| **UEMCP** (ATDev, `uvx uemcp`) | MIT | PyPI "5.0–5.6", README "5.0–5.7" (contradiction) | Python remote execution (239.0.0.1:6766 + TCP) | uv | 29 or 31 (page disagrees) incl. `ue_python`, `ue_save_all` | **none** | **0 stars**, v0.1.0 (2026-06-12) — not a first choice |
| db-lyon/ue-mcp (npm) | MIT | 5.4–5.8, Windows | TS stdio + C++ bridge (WebSocket) | Node 18+, Visual Studio | 2,040+ actions | write guard, VCS guard, git snapshots | `npx ue-mcp init` auto-edits client configs — ask first; stars unknown |
| chongdashu/unreal-mcp | MIT | 5.5+ | Python FastMCP ↔ TCP 55557 C++ plugin | compile with VS | actors, Blueprint graphs | none mentioned | self-declared experimental, last push 2025-04 (unverified) — **don't** |
| ziggymar/unreal-mcp | ? | ? | ? | ? | ? | ? | repo returns 404 — **don't** |

## Install lines (ask the user before each)

### Epic Unreal MCP (UE 5.8)
1. Edit > Plugins: enable **Unreal MCP** and **All Toolsets** (Terminal optional), restart.
2. Editor Preferences > General > Model Context Protocol: Auto Start Server (off by default), port 8000, path `/mcp`, Enable Tool Search (on). Or console: `ModelContextProtocol.StartServer`.
3. Console: `ModelContextProtocol.GenerateClientConfig ClaudeCode` (or `Codex`, `All`) — writes the config in the project root. The Codex TOML is written **once**; delete the old one to regenerate.

Claude Code — start `claude` from the project root to pick up the generated `.mcp.json`, or (equivalent, unverified):
```bash
claude mcp add --transport http unreal-mcp http://127.0.0.1:8000/mcp
```
Codex (unverified against the generated file):
```bash
codex mcp add unreal-mcp --url http://127.0.0.1:8000/mcp
```
```toml
[mcp_servers.unreal-mcp]
url = "http://127.0.0.1:8000/mcp"
startup_timeout_sec = 30
tool_timeout_sec = 600
```

### EngineWire
Token: `<Project>/Saved/MCP/capability-token` (delete + restart to rotate). Keep it out of git — put it in an env var.
```bash
# Claude Code (from the repo README)
claude mcp add --transport http unreal-engine http://127.0.0.1:3000/mcp --header "X-MCP-Capability-Token: <token>"
```
`claude mcp add` writes the header into the user/local config; don't use `--scope project` (that writes `.mcp.json`, which may be committed).
```toml
# Codex (derived from Codex docs, unverified)
[mcp_servers.unreal-engine]
url = "http://127.0.0.1:3000/mcp"
http_headers = { "X-MCP-Capability-Token" = "<token>" }
tool_timeout_sec = 600
```
Route B (stdio): `npx -y unreal-engine-mcp-server@beta` with env `UE_PROJECT_PATH` — the `@beta` tag is required or npm installs the mismatched 0.5.30.

### runreal/unreal-mcp (no compile)
UE: enable Python Editor Script Plugin; Project Settings > Python > Enable Remote Execution.
```bash
claude mcp add unreal -- npx -y @runreal/unreal-mcp      # unverified, general syntax
codex mcp add unreal -- npx -y @runreal/unreal-mcp       # unverified
```

### unreal-engine-mcp (PyPI)
```bash
pip install unreal-engine-mcp
claude mcp add unreal-mcp -- python -m unreal_mcp.server   # or: uvx unreal-engine-mcp
```
```toml
[mcp_servers.unreal-mcp]
command = "python"            # the python that has the package; use an absolute path if unsure
args = ["-m", "unreal_mcp.server"]
```

### UEMCP
```bash
claude mcp add unreal -- uvx uemcp
codex mcp add unreal -- uvx uemcp     # unverified
```

Codex general syntax (official): stdio `codex mcp add <name> --env K=V -- <command>`; HTTP `codex mcp add <name> --url <url>`; `config.toml` keys `command`/`args`/`[mcp_servers.x.env]` or `url`/`bearer_token_env_var`/`http_headers`; `startup_timeout_sec` (default 10), `tool_timeout_sec` (default 60).

## Security checklist
- All of these execute arbitrary code/commands inside the editor. Project in VCS, saved, committed before each session.
- Bind 127.0.0.1 only. No 0.0.0.0, no ngrok/cloudflared tunnels, multicast TTL 0.
- Epic MCP, Python remote execution and UEMCP have **no authentication**: anything on the PC that can reach the port can drive the editor.
- Don't call tools in parallel (game thread is serial).
- Ask before delete/replace/save-all/package/console commands that change settings. EngineWire's per-call consent helps; the others rely on you.
- Tokens and passphrases in env vars or untracked files only.

## Sources
- Epic, Unreal MCP in Unreal Editor: https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-mcp-in-unreal-editor
- Puget Systems test (2026-07-09): https://www.pugetsystems.com/?p=48127
- UEMCP: https://pypi.org/project/uemcp/ , https://github.com/ATDev-Inc/uemcp
- EngineWire: https://github.com/ChiR24/Unreal_mcp
- chongdashu: https://github.com/chongdashu/unreal-mcp
- runreal: https://github.com/runreal/unreal-mcp
- unreal-engine-mcp: https://pypi.org/project/unreal-engine-mcp/ , https://github.com/FFZackFair92/unreal-engine-mcp
- ue-mcp: https://cdn.jsdelivr.net/gh/db-lyon/ue-mcp@main/README.md
- Codex MCP config: https://learn.chatgpt.com/docs/extend/mcp?surface=cli
