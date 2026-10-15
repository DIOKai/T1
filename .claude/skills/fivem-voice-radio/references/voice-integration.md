# Voice integration and acceptance

## pma-voice decisions

Read the installed README and exact exports first. Upstream has changed phone terminology to call terminology; do not mix old voice_enablePhones/phone state with current call APIs. Validate the local version rather than blindly upgrading it.

Use one intended audio mode. Native-audio submix behavior and distance modes need compatible settings. Inspect who writes proximity/voice natives before blaming microphone permissions.

Existing players can retain keybind/volume settings; changing a default does not prove existing profiles changed. Test a clean profile and an existing one. disableRadio is a bit field in the reviewed pma-voice source; treating it as a boolean can mishandle multiple simultaneous disable reasons.

Restricted channels need server-side entitlement and a revocation path when that entitlement disappears. Inspect current addChannelCheck and setPlayerRadio documentation/signatures; this skill does not pin an unverified API call into every server.

## Acceptance matrix

Use named test clients A/B, known channels, distance points, and recorded configuration:
- A/B nearby: hear each other; outside the agreed proximity range: cannot.
- Same permitted radio channel: both directions work; unrelated channel: no radio audio.
- Unauthorized role/item: channel request denied server-side and UI reflects actual state.
- Death/restraint/item loss/duty change: project-defined radio restrictions activate and recover correctly.
- Join/leave/call/disconnect/reconnect/resource restart: no stale membership or stuck transmit.
- Existing versus clean keybind profile: intended controls work.
- Bucket/interior changes: explicitly test required privacy; do not infer it.
- Simultaneous radio and phone/proximity: no unintended doubled audio or volume behavior.

Record actual audibility independently from UI events. Any unavailable second client or audio observation remains not run.

## Sources

Reviewed 2026-10-15:
- [Cfx voice](https://docs.fivem.net/docs/scripting-manual/voice/).
- [pma-voice README](https://github.com/AvarianKnight/pma-voice): settings, API routing, incompatibilities and state types. MIT upstream; no upstream code is bundled here.
- [pma-voice channel checks](https://github.com/AvarianKnight/pma-voice/blob/main/docs/server-setters/addChannelCheck.md): verify against the installed revision before implementation.

Offline review cases: a working HUD with silent audio needs transport/device diagnosis; removing a radio item must revoke an already joined restricted channel; one client cannot verify isolation.
