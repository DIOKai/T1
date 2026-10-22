# Setting up the Rhino MCP (Claude Code and Codex)

Ask the user before each step. Each one installs something or changes a config file, and Rhino itself is paid (licence or the 90-day trial).

## 1. Rhino side (both clients)
1. Rhino 8 only (it can also go into Rhino 9 WIP/BETA).
2. In Rhino run `PackageManager`, search **Rhino-MCP-Platform**, install it. (Link form: `rhino8://package/search?name=Rhino-MCP-Platform`.)
3. Run `MCPConnect`. It prints the prompt or command your client needs.

## 2a. Claude Code
**Documented route:** paste the prompt that `MCPConnect` prints into a new Claude Code session and restart Claude Code when it says so.

**Plugin route** (in the repo's `cc-plugin/README.md`, currently commented out of the docs site):
```
/plugin marketplace add mcneel/RhinoAI
/plugin install mcneel@rhino-mcp
```
- The plugin's `.mcp.json`: `"rhino": {"type": "stdio", "command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/router-launcher.mjs"]}`, so it needs Node.js.
- Its README says to run `MCPStart` in Rhino first; default port **10500** (`http://localhost:10500`).
- It also ships slash commands (`/rhino-mcp:snapshot`, `/rhino-mcp:scene`, `/rhino-mcp:launch-rhino(s)`, `/rhino-mcp:install-mcp`) and agents (rhino-modeler, drafter, inspector, organizer, teacher, grasshopper-scripter/reviewer/teacher).
- Which route is more reliable on current versions is 未验证. Prefer `MCPConnect`, since that's what the docs show now.

Not documented, inferred from the Codex config below (未验证): `claude mcp add rhino -- rhino-mcp-router --default-version 8`. Use it only if `MCPConnect` prints the same thing.

## 2b. OpenAI Codex
`~/.codex/config.toml`:
```toml
[mcp_servers.rhino]
command = "rhino-mcp-router"
args = ["--default-version", "8"]   # "9" = Rhino 9 WIP/BETA
```
Run `MCPConnect` in Rhino first; it prints the exact command Codex needs (and how `rhino-mcp-router` gets onto the PATH).

## 2c. Claude Desktop (for reference)
Install the `.mcpb` connector from the releases page (`connector-v0.1.6/connector.mcpb`). It installs the Rhino plug-in by itself.

## 3. Check it works
Call `get_context` (read-only). It should return the open document, units, selection and viewports. If it fails: is Rhino open, the plug-in loaded (trial not expired), and `MCPStart`/`MCPConnect` run in this Rhino session?

## Alternative: tanishqbhattad/rhino-mcp (safety gate)
- Local only, per-user auth token, `127.0.0.1:9544`. Mode via `RHINO_AIBRIDGE_MODE` = `safe` (default: no code, no destructive edits) / `standard` / `developer`. 128 tools in lean (21) / standard (76) / full (128) sets. `execute_python3` (CPython) needs Rhino 8.11+ and developer mode; `execute_script` is IronPython 2.
- Install: `INSTALL.bat`, then `PlugInManager` → `RhinoAIBridge.rhp`.
- Codex:
  ```toml
  [mcp_servers.rhino_architect]
  command = "uv"
  args = ["--directory", "<path>/server", "run", "--frozen", "rhino-architect"]
  ```
- Claude Code: the README only shows Claude Desktop. The equivalent `claude mcp add rhino_architect -- uv --directory <path>/server run --frozen rhino-architect` is an inference (未验证).

## Sources
- https://mcneel.github.io/RhinoAI/docs/getting-started/cc-plugin/
- https://github.com/mcneel/RhinoAI/blob/main/cc-plugin/README.md
- https://mcneel.github.io/RhinoAI/docs/getting-started/codex/
- https://github.com/mcneel/RhinoAI (README, releases)
- https://github.com/tanishqbhattad/rhino-mcp
