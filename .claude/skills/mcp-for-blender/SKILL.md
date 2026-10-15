---
name: mcp-for-blender
description: Operate a live Blender session through the ahujasid/mcp-for-blender Codex plugin or MCP server. Use for inspecting or changing an open .blend scene; do not use for conceptual Blender questions or DCC-MCP-specific workflows.
---

# MCP for Blender

Use the connected `blender` MCP as the bridge to the user's open Blender session. This skill governs the bridge workflow; combine it with the relevant modeling, UV, material, rigging, animation, optimization, or export skill when that specialist guidance is needed.

## Connection and authorization

- Before any live Blender access, explain whether the planned calls only inspect the scene or will change it, and obtain the user's approval.
- If the Blender tools are unavailable, report that the MCP or add-on is not connected. Do not install, reconfigure, or launch it without separate approval.
- Keep the add-on bound to localhost. Prefer `BLENDER_MCP_SAFE_MODE=1` and keep telemetry disabled. Do not enable paid or credentialed model-generation providers unless the user explicitly requests one.
- Treat `execute_blender_code` as arbitrary Python execution with the user's permissions. Use it only when structured tools cannot perform the requested operation.

## Workflow

1. Inspect before changing: get scene/object information and capture a viewport image when visual state matters.
2. Confirm the target object, collection, active mode, units, frame, and output path. Do not guess destructive targets.
3. Prefer the smallest reversible operation. For multi-step work, make one coherent change at a time.
4. After every material change, re-inspect the affected data and use a viewport screenshot or render when appearance matters.
5. Save or export only when the user requested it, and preserve the existing `.blend` unless overwrite permission is explicit.

Tool names can vary by plugin version. Discover the live tool list and map logical operations such as scene inspection, object inspection, viewport capture, and Blender Python execution to the names exposed in the current session.

## Acceptance

- Report the objects or files changed and where outputs were written.
- Verify geometry/state numerically where possible and visually when relevant.
- If verification is incomplete, say what could not be checked instead of claiming success.

Source: https://github.com/ahujasid/mcp-for-blender
