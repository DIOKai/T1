---
name: fivem-voice-radio
description: Integrate and diagnose FiveM proximity voice, radio channels, calls, mute states, and pma-voice resource lifecycle. Use for voice transport and radio authorization; ordinary sound effects and music belong to an audio-asset workflow.
---

# FiveM Voice and Radio

First identify the installed voice resource/version, FXServer/client build, framework, radio/phone integrations, current convars, symptoms and reproduction clients. Preserve the existing configuration before proposing changes. Loading this skill does not authorize installing a resource or connecting to a live server.

Read [voice-integration.md](references/voice-integration.md) for version-sensitive pma-voice behavior and the two-client acceptance matrix.

## Diagnose before editing

1. Separate microphone/device failure, proximity transport, channel membership, radio authorization, UI display and audio mixing. A talking icon proves none of the other layers.
2. Inspect other resources that set voice natives or own a second voice system. Avoid simultaneous competing proximity controllers.
3. Verify the installed exports and state types from its source. Old phone/call names and saved keybinds can survive an update.
4. For restricted channels, derive identity/job/item entitlement on the server and use the installed channel-check mechanism. A client UI restriction alone does not authorize a channel.
5. Handle disconnect, reconnect, duty/item changes, death/restraint, resource restart and phone integration separately. Do not assume routing buckets automatically enforce the project's voice privacy requirement.
6. Make the smallest scoped change, then retest with at least two authorized local-test clients.

## Deliver

Report exact resource/version, changed convars/files, expected versus observed behavior and pass/fail/not-run by scenario. Distinguish config review from actual audio heard on two clients. Never claim a single-client test proves radio isolation or intelligibility.
