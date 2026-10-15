---
name: fivem-mcp
description: Inspect and live-test a local FiveM development server or Legacy client through ziyacivan/fivem-mcp. Use for RCON, DevCon, logs, screenshots, NUI, native, and resource smoke tests; not for ordinary source editing alone.
---

# FiveM MCP

Use this skill only for live testing against a FiveM environment the user owns and has placed in scope. Use the ordinary FiveM development skills for code changes; this skill supplies the runtime evidence loop.

## Hard safety boundary

- Ask before connecting or issuing any live command. Connect only to a local development server, normally `127.0.0.1`; never connect this MCP to production.
- RCON is administrator-level access. Never print, echo, commit, or include `FIVEM_RCON_PASSWORD` or `FIVEM_MCPB_TOKEN` in results.
- Keep DevCon on loopback. Do not tunnel or expose its unauthenticated port.
- Treat `server_command`, `trigger_event`, `call_export`, `call_native`, teleport, process termination, keyboard/mouse input, and forced quit as mutating actions. Obtain specific approval when they are not already clearly authorized by the task.
- Client DevCon features require FiveM Legacy; Enhanced does not expose those ports.

## Runtime workflow

1. Call the MCP status tool first and identify the exact server/client connection.
2. Establish a read-only baseline with server information, recent server/client logs, window status, and a screenshot only when it adds evidence.
3. Restart or exercise only the resource in scope. Prefer allowlisted bridge operations and the smallest command needed.
4. Wait for explicit success or error output. Check both server and client logs because failures may appear on only one side.
5. For NUI or gameplay flows, verify the visible result and relevant state; do not use screenshots as the sole proof when logs or bridge state are available.
6. Restore temporary state when safe and report anything left running or modified.

## Result format

Return PASS, FAIL, or NOT VERIFIED for each expectation, with the command or action performed and the observable evidence. Never turn missing evidence into a pass.

Source: https://github.com/ziyacivan/fivem-mcp
