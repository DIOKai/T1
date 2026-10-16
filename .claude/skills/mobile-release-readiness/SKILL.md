---
name: mobile-release-readiness
description: "Assess and fix mobile app release readiness across accessibility, localization, privacy, secrets, backup and restore, monitoring, migrations and rollback. Use before beta/store release or for a release audit; does not itself authorize publishing, deleting data or enabling third-party collection."
---

# Mobile Release Readiness

## Establish scope and evidence
Read [sources](references/sources.md). Identify app version/commit, platforms, minimum OS, package lock, build profile, release audience, backend migration, collected data and actual release authorization. Follow the existing product brief and repository rules. Use existing testing, security and design skills for specialized findings; do not substitute a checklist for their execution.

Create a compact evidence table: check, result, evidence, owner/action. Use PASS, FAIL, NOT TESTED or NOT APPLICABLE. A missing tool/device/account is NOT TESTED, never PASS.

## Review and fix within scope
1. Build/reproduce the intended release configuration. Check app IDs, version/build numbers, signing ownership and environment separation without exposing keys. Remove debug endpoints and ensure production credentials are server-side where required.
2. Exercise account creation/login/logout, expired sessions, admin access, account switching and deletion where supported. Verify server-side authorization, log redaction, permissions, retention and user-facing privacy statements against actual behavior. Consult current store rules for the app's category/region; do not give a blanket compliance guarantee.
3. Check VoiceOver/TalkBack labels, roles, states, focus order and modal focus. Test large text without clipping, contrast, touch targets and reduced motion on supported platforms. Automated accessibility scans do not replace screen-reader testing.
4. Use locale-aware dates, numbers, currency and plurals. Test missing translations, long strings, RTL if supported, system/per-app language changes and time-zone boundaries. Do not concatenate translated fragments or hardcode Malaysian/US formatting for all users.
5. Separate database, object storage, auth configuration and secrets in the backup inventory. Record retention, recovery objectives and access ownership. Verify a restore into an isolated destination; database metadata alone does not restore uploaded object bytes. Use a consistent recovery point or reconcile an object manifest against database references after restore. Reconcile restored data with app/schema versions.
6. Plan backward-compatible backend/schema rollout. Specify which app versions remain supported, when migrations run, rollback boundaries and recovery from failed migrations. An OTA update cannot replace arbitrary native module or entitlement changes; confirm runtime compatibility before recommending one.
7. Use existing authorized crash/health monitoring with readable symbols/source maps and redacted context. Define an actionable alert and owner. Do not enable session replay or capture private user content by default.
8. Run critical functional, offline, notification and purchase tests only where applicable. Verify release performance on the slowest supported class of device; record startup, memory and jank evidence rather than universal invented thresholds.
9. Prepare a staged rollout and stop/rollback criteria. Verify store metadata, screenshots, support contact, privacy declarations and account-deletion links where required. Do not submit/publish or run a destructive restore without scope authorization.

## Handoff
Lead with release blockers, then a check/evidence table and ordered fixes. Include exact build/commit and devices used, tests not run, rollback and backup ownership. Say ready only for the checks actually supported by evidence; a successful compilation or clean screenshot is insufficient.
