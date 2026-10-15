# Schema migration and recovery

Use for table/index/column changes, data backfills and database version upgrades. The main skill's transaction advice applies to suitable transactional writes; it is not a guarantee that schema changes can be rolled back.

## Plan from actual versions

Record the installed oxmysql fork/version, database engine/version, table engine, SQL mode, charset/collation, schema revision, application consumers and target schema. CommunityOx/oxmysql was archived when reviewed on 2026-10-15; do not replace a working resource or change its API solely to follow a new fork.

Inspect the existing migration mechanism first. dbmate is an optional free migration tool supporting MySQL/MariaDB; do not introduce it when the project already has an adequate migration ledger. Check installed-version help and SQL compatibility before proposing commands.

## Migration and recovery sequence

1. Obtain a scoped schema/data sample or authorized metadata read. Keep production connection strings and dumps out of Git and logs.
2. Define preconditions: current schema/version, null/duplicate values, foreign keys, data volume, disk capacity and consumers of affected fields.
3. Prefer expand -> backfill -> switch consumers -> contract when rolling deployments need old/new compatibility. Destructive contraction should occur only after old consumers are gone.
4. Prepare versioned SQL, a migration ledger/checksum strategy, an interruption/retry plan and explicit success assertions. Do not silently rerun a half-completed ALTER.
5. Prepare a consistent backup and prove restoration into a separate database. Record row counts and meaningful application invariants, not just 'backup file exists'.
6. Rehearse upgrade and failure/recovery on an isolated copy with matching engine/version. Record locks, duration, backfill restartability and old/new consumer compatibility.
7. Execute live changes only within the user's actual deployment authorization, then verify invariants and retain recovery evidence.

## Transaction boundary

MariaDB lists statements such as ALTER, CREATE, DROP and TRUNCATE that can implicitly commit. A surrounding MySQL.transaction is not protection against those schema operations. A down migration that recreates a deleted column cannot recreate its lost data. Schema dump, full data backup, inverse SQL and restore are distinct artifacts.

For large or destructive changes, choose a stopping/recovery point appropriate to the data at risk. If the observed schema differs from preconditions, stop the migration plan and inspect; do not force it through.

## Acceptance and output

Deliver exact source/target versions, scoped SQL files, preconditions, backup/restore procedure, rehearsal observations and post-checks. Claim 'recovery tested' only when a restore and relevant application checks actually ran. A static review is not execution.

## Sources

Reviewed 2026-10-15:
- [CommunityOx oxmysql](https://github.com/communityox/oxmysql): archived upstream state.
- [dbmate](https://github.com/amacneil/dbmate): migration ledger, MySQL/MariaDB and tool behavior.
- [MariaDB implicit commits](https://mariadb.com/docs/server/reference/sql-statements/transactions/sql-statements-that-cause-an-implicit-commit): schema transaction limits.

No credentials, migration executable, SQL against a user's database or third-party code are bundled.
