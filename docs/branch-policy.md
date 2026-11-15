# Branch policy

`main` is the sole remote branch and the sole authoritative development line for this repository.

Changes are committed only after local or CI validation. Historical development heads are preserved with immutable archive tags when needed; they are not retained as additional branches. Temporary transfer directories, encoded source fragments, recovery controllers, trigger files, and generated caches are forbidden in the ordinary source tree.

## Public asset branch consolidation — 2026-11-15

The two commits from `research/public-model-transfer-20261104` are preserved in
the `main` merge history. The [public asset catalog](public-model-assets.json)
consolidates their fixed model/source versions, recorded checksums and source
Git blob identities. The two branch-specific one-shot download workflows remain
available through their original commits; they are not installed as active
Actions workflows. This review did not download model weights or execute a solver.
