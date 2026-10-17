# Persistence and migration

[Expo SQLite](https://docs.expo.dev/versions/latest/sdk/sqlite/) is the version-specific API reference. Persist the actual domain record and queued intent together when atomicity is required; an in-memory query cache is not a durable outbox. Use bound parameters and explicit transactions, and check the installed API's transaction isolation behavior.

Record schema version and migration ordering. Exercise upgrades from supported old versions, interrupted migrations and restart recovery in a copy. A reverse SQL script does not by itself restore deleted data. Test backup/restore and compatible application versions before promising rollback.

Store account/tenant scope in local records and delivery state. Keep credentials in the project's secure credential mechanism, not serialized queue payloads or exported fixtures. Logout/account switch must not silently deliver another user's pending writes under the new identity.

Inspect [TanStack mutation persistence](https://tanstack.com/query/latest/docs/framework/react/guides/mutations) before relying on resumable mutations; serialized state alone may omit functions required after restart. Use the same supported runtime versions in tests and deployment.

Existing reference for the narrower network/cancellation task: [expo-data-fetching](../../expo-data-fetching/SKILL.md). Select only the relevant skill for a given request.
