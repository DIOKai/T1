# Optional scoped memory and review

Memory is disabled by default. Enable only when the user chooses a dedicated location and identifiers. Never discover or copy another user's existing memory. Use a separate location per user; every read/write also requires explicit user and project scope. No automatic general/organisation sharing or background uploads are provided. Use a distinct project key for transferable lessons only if explicitly chosen; it is still isolated within that user.

Before promising cross-session memory, verify that the chosen root is durable storage available in a later session; a successful write in a temporary sandbox proves only that session's write. If durability is unknown, label the record session-only and offer an export to a user-chosen persistent location. Do not assume that all folders in a cloud or desktop host have the same lifecycle.

The optional Python 3.10+ standard-library helper is resolved relative to this package:

```text
python3 scripts/memory.py --root <chosen-directory> --user <user-key> --project <project-key> add --file <record.json>
python3 scripts/memory.py --root <chosen-directory> --user <user-key> --project <project-key> list --status verified
python3 scripts/memory.py --root <chosen-directory> --user <user-key> --project <project-key> correct <id> --file <correction.json>
python3 scripts/memory.py --root <chosen-directory> --user <user-key> --project <project-key> check
python3 scripts/memory.py --root <chosen-directory> --user <user-key> --project <project-key> recover --confirm
```

Run from the package directory or prefix the script with its resolved package location. Root is always required; no home-directory or harness default. Scope identifiers are hashed into storage names and retained inside the envelope for validation. This prevents accidental cross-scope reads, not hostile access: directory permissions and OS security remain the user's responsibility.

A record requires `summary`, `status` (`tentative` or `verified`), `kind` (`decision`, `observation`, `lesson`), and nonempty `evidence` entries with `source`, `locator` and `verification`. Optional `details` holds concise constraints/version/basis. The helper assigns ID, scope and timestamp. Verified means corroborated by explicit decision, actually inspected evidence, calculation or observed test; the schema cannot prove that evidence is true. Source observations are not automatically policy approval. Critic/semantic suggestions alone stay tentative. Do not retain full project datasets, credentials, hidden answer keys or unnecessary personal/supplier facts.

Correction appends a replacement, marks the original superseded and links both while preserving history. Tentative records cannot retire verified records; verify evidence first or save a separate tentative suggestion. List filters are exact scope. Reassess relevance and dated facts before reuse; price evidence needs location, date, currency, unit and scope. Memory is retrieval, not model retraining.

Atomic write, an exclusive lock and a validated previous-copy backup protect ordinary writes. Corruption, wrong scope or unresolved lock fails visibly and does not reset data. `recover --confirm` is an explicit rollback to the validated previous copy, preserving the damaged/current file under a recovery filename. It may discard the latest valid change; inspect both first. A stale lock is not removed automatically: establish no writer is active, preserve evidence and remove it manually only then. Concurrent readers see the prior or new complete snapshot. This helper offers local convenience, not encrypted storage, distributed transactions or automatic cloud synchronisation.

If the primary file is missing but a previous copy survives, reads and additions refuse to treat the store as new. Preserve that copy and use explicit recovery after inspection; do not overwrite it with an empty-store backup. A genuinely new scope with no primary or previous copy may start empty.

## Quality review

Check calculations, dimensions/units, duplicate scope, source validity, state semantics, coding reconciliation and practical usefulness. Significant decisions benefit from an independent reviewer when available and within the user's authorised scope. Give a tester the request, skill and raw inputs without expected answers or previous critiques. A critic assesses actual outputs against fixed criteria. Preserve defects/corrections and rerun affected tasks plus unseen variants; do not weaken criteria to obtain a pass.

Optional Jev or another semantic adapter may inspect a narrow ambiguity: scope-pair overlap, claim support or selection among complete user-supplied code definitions. Include an unresolved/no-match outcome and minimal authorised excerpts. Never treat adapter confidence as approval, a crosswalk, arithmetic verification or evidence of regulatory compliance. Numeric suffixes are not mappings. If unavailable, perform exact membership/source checks, pairwise scope reasoning, calculation and independent review where available; identify any adapter check as not run. Core work does not depend on it. External transmission needs the user's authority and relevant data/reference permission.

Controlled tests and AI rubric scores do not establish professional certification, an empirical human percentile or universal model/harness compatibility. Report which tasks, tools and environments were actually exercised.
