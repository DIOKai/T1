---
name: fivem-authorized-asset-workflow
description: Safely inventory, back up, inspect, convert, and modify legally obtained FiveM/GTA V assets when the license permits it. Use for purchased files, source handoff, format conversion, provenance, or editability checks; never for decrypting or bypassing Asset Escrow or DRM.
---

# FiveM Authorized Asset Workflow

Help the user work with purchased or commissioned assets without crossing technical-protection or license boundaries.

## Classify before touching the asset

Read [references/authorization.md](references/authorization.md), then record:

- acquisition source, purchaser/account, receipt or entitlement evidence;
- license terms, permitted servers, modification and redistribution rights;
- whether the user has author-provided source/unlocked files;
- which files are ordinary readable files and which are escrowed, encrypted, obfuscated, or entitlement-gated;
- requested outcome and whether it requires access the license does not grant.

If authority is unclear, pause before conversion or modification and ask for the license text or vendor confirmation.

## Allowed workflow

1. Make a read-only inventory and hashes before changes.
2. Preserve the original archive and establish a separate working copy.
3. Inspect readable manifests, metadata, textures, meshes, logs, and source files.
4. Convert only unprotected files using official or openly documented tools such as Sollumz and CodeWalker-compatible workflows.
5. Keep a change record and preserve attribution/notices required by the license.
6. Validate the modified resource on a local server tied to the user's legitimate entitlement.

## Stop conditions

Stop and offer a lawful alternative when the task would require:

- extracting or decrypting Asset Escrow-protected content;
- defeating an entitlement, subscription, license check, password, or DRM;
- patching a binary solely to bypass protection;
- redistributing source or assets beyond the granted license;
- using leaked keys, stolen accounts, or unauthorized copies.

Suitable alternatives include asking the creator for an unlocked development package, requesting a customization from the creator, obtaining written edit permission, using an `escrow_ignore`-provided configuration/source file, or rebuilding an original replacement from assets the user owns.

Do not imply that purchase alone grants source access. Distinguish “may run” from “may inspect, modify, or redistribute.”
