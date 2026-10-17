# Manifest helper contract

Python standard library only. The helper walks one explicit local directory without following symlinks or Windows reparse points and streams SHA-256 hashes for regular files. It outputs relative forward-slash paths, byte sizes, hashes, findings and required-path checks. It writes no files, extracts no archives and executes no package code.

--required is repeatable and accepts only normalized relative forward-slash file paths. Absolute paths, empty/dot/dot-dot components, colons and backslashes are rejected. Every required item must be an included regular file, not merely an existing directory or a skipped link.

Potential sensitive/development filenames are warnings only; content is not searched. A .pem name may be a public certificate, and a harmless filename does not prove the file contains no secret. Filename matching is not a secret scanner.

Unreadable, changed-during-read, link/reparse or special files leave scanning incomplete. A nonempty package with no scan errors/missing requirements returns exit0; empty packages and required-path/scan errors return exit2 with a JSON report. Invalid CLI input also exits2. Warnings alone do not fail the helper. These are scan results, not release approval.

Root paths are local inputs; concurrent writers are outside the helper's trust model. Use a stable staging snapshot. Compare the final archive bytes separately; hashing a staging file before a later rebuild is insufficient.
