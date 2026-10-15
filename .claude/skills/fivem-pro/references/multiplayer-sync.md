# Multiplayer synchronization diagnosis

Read for disagreement between clients, duplicate/missing entities, stale state after reconnect or ownership changes. This is a focused workflow, not permission to connect to a production server.

## Reproduce and identify

Record client A/B server IDs, resource/build, network ID versus local entity handle, entity type, owner, routing bucket, coordinates and the action timeline. A client player index or entity handle is local to that client; do not transmit it as if it were a global identifier.

Separate these cases before editing:
- Never created on the intended authority.
- Created but outside the client's scope or bucket.
- Created twice by different owners/resources.
- Exists but state/attachments/appearance are applied before local availability.
- Recreated after death/reconnect while old IDs or callbacks are retained.

Prefer server authority for persistent shared entities and record the intended cleanup/respawn owner. Do not add a client-local spawn loop to repair a missing networked entity without identifying its lifecycle.

## State and ownership

Check network scope before using an ID on a client. Ownership can migrate; initialization must tolerate later availability and repeated delivery without duplicating side effects. Use bounded readiness handling and cancel stale work on stop/logout; do not spin indefinitely.

State Bags have serialization and shallow-update behavior. Assign the intended key through the supported API; mutating a nested Lua table is not proof of replication. State set by a client is not automatically authoritative or replicated. Do not use a client-writable state value as the sole job/item/payment authorization.

A routing bucket partitions entity state but is not a blanket interior/voice solution. Voice privacy needs its own test. Recheck identity, bucket and scope when an entity migrates or a player reconnects.

## Acceptance with two clients

| Scenario | Evidence |
| --- | --- |
| A creates/updates, B observes | Same intended networked entity and state, not two local copies |
| B enters/leaves scope | Correct reappearance/reapplication without duplicate spawn |
| Owner disconnects | Defined migration/cleanup/respawn behavior; no orphan/stale action |
| Resource restart | No duplicate entities/handlers or stuck references |
| Death/respawn/reconnect | New IDs resolved and stale callbacks canceled |
| Bucket transition | Intended isolation and return; voice checked separately |
| Simultaneous actions | Server decides once where required; no duplicate persistent write/reward |

Log expected/observed results and mark missing clients or scenarios not run. Client milliseconds do not become server cost merely by multiplying by player count; measure the relevant execution path.

## Sources

Reviewed 2026-10-15: [Cfx OneSync](https://docs.fivem.net/docs/scripting-reference/onesync/), [State Bags](https://docs.fivem.net/docs/scripting-manual/networking/state-bags/), and [network/local IDs](https://docs.fivem.net/docs/scripting-manual/networking/ids/). Verify current native/API signatures before writing version-specific code.
