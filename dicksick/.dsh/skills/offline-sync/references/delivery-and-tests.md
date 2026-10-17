# Delivery contract and fault tests

A useful operation record has a stable operation ID, entity ID, account scope, intended mutation, base/server version and delivery state. Keep retries of one intent under the same identity. The exact schema and timeout/attempt budgets belong to the product contract.

Fault cases to exercise:
1. Crash after local commit but before sending.
2. Server commits, but its acknowledgement is lost.
3. Duplicate delivery or two workers race for one record.
4. Older response arrives after a newer operation.
5. Offline edit conflicts with a server update or deletion.
6. Credential expiry, permission revocation and account switch.
7. App/schema upgrade with an existing queue.
8. Cancel/background/restart while an operation is in flight.

Assert both visible data and backend side-effect counts. A mocked deduplication success does not prove a deployed server supports idempotency. Network reachable is not equivalent to an authenticated, healthy backend. Return blocked/conflict operations to an explicit user resolution path rather than retrying forever.

Supplementary learning: [Expo SQLite CRUD tutorial](https://www.youtube.com/watch?v=vgPdAARd6Gw), Aaron Saunders, 2024-12-10. Only metadata/chapters were checked; CRUD examples do not establish correct synchronization.
