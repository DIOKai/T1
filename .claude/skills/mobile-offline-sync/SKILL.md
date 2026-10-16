---
name: mobile-offline-sync
description: "Design, implement or debug offline-first mobile storage, durable upload queues, reconnect sync, schema migrations, conflicts and account isolation in Expo or React Native. Use for offline edits and cross-device sync; not for cache-only requests or automatically adopting a sync vendor."
---

# Mobile Offline and Sync

## Establish the contract
Read [sources](references/sources.md) and inspect existing persistence, auth and backend policies. Identify which entities must work offline, which actions require a server, supported SDK versions, retention, multi-account behavior and device-loss expectations. Reuse the current architecture; do not install PowerSync or any other service automatically.

Choose the smallest adequate design:
- A disposable response cache for read-only data.
- Local SQLite plus a durable outbox for controlled offline writes.
- An existing supported sync engine for complex replication.
PowerSync has official skills; consult its current SDK/service docs when selected. Cloud hosting, self-hosting and licensing are separate choices. Do not assume hosted sync is free or that a local database automatically syncs.

## Implement reliably
1. Define local schema, stable client-generated IDs, server revision/version fields, unique operation IDs and deletion tombstones. Scope every local row and queued operation to the owning account/tenant.
2. Commit a local edit and its outbox operation in one database transaction. Render UI from the local database and expose pending/synced/conflicted/failed status. Persist the queue across process death.
3. Replay with bounded batches and backoff. Use server-side idempotency keys or an operation ledger with atomic application so a network timeout followed by retry cannot duplicate writes.
4. Authenticate and authorize again on the server. The queue is untrusted input; local account IDs are not authorization. Pause on expired credentials. Handle validation failures as actionable failures instead of retrying forever.
5. Define conflict policy per entity. Use optimistic revision checks for contested edits; choose explicit merge or user resolution when losing an edit matters. Use last-write-wins only when its data-loss tradeoff is accepted. Do not rely on device clocks to order authoritative writes.
6. Pull changes with resumable cursors and durable checkpoints. Do not advance a cursor before changes commit. Define tombstone retention and a full-resync path when a cursor expires; prevent stale clients from resurrecting deleted records.
7. On logout or account switch, stop the sync worker, isolate/remove the old account's local data, and handle pending edits deliberately before removal. Never send account A's queue using account B's session. Capture account identity and a session generation on each in-flight request; discard late responses after logout/switch so they cannot populate the new account's store.
8. Add migration steps and rollback/recovery strategy. Do not silently delete the database when migration fails. Store tokens in platform secure storage; SQLite is not encrypted by default. Decide encryption and backup behavior separately.
9. Treat attachments as a separate resumable queue with ownership, size limits, checksums and cleanup. Do not claim the SQL database backup includes file bytes.

## Verification and handoff
Exercise offline create/edit/delete; close and reopen; reconnect; lose the response after the server commits; edit the same entity on two devices; replay a tombstone; expire credentials; switch accounts; upgrade an older database; fail an attachment midway. Verify no duplicate effects or cross-account data.

Return schema, queue protocol, conflict policy, migration/recovery steps and observed tests. Label device, backend and failure cases not actually tested. A successful local write is not proof of cloud sync.
