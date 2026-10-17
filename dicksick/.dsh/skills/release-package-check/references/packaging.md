# Packaging evidence

For npm projects use the installed CLI's [npm pack documentation](https://docs.npmjs.com/cli/v11/commands/npm-pack/). Review package files/ignore rules and lifecycle scripts before running packaging commands; dry-run and ignore-scripts have different purposes. A package tarball and a Git checkout can contain different files.

[Changesets](https://github.com/changesets/changesets/blob/main/docs/intro-to-using-changesets.md) can support versions and changelogs, particularly for packages/monorepos. It is not a mandatory release dependency and does not validate every target's install or runtime behavior.

For any format compare declared contents against the actual artifact, not just source files. Check entrypoints, referenced assets, production dependencies and platform/runtime requirements. Verify LICENSE/NOTICE and third-party attribution without inventing license terms.

Never assume a build or npm lifecycle script is read-only; inspect and scope execution separately. Do not sign, publish or push a tag as part of readiness inspection unless that operation is actually requested.
