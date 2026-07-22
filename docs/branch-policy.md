# Branch policy

`main` is the sole long-lived and authoritative branch.

Short-lived branches are allowed only while implementing or validating a bounded change. Before deletion, their unique commits and artifacts must be audited and either integrated, superseded with an explicit rationale, or preserved by an immutable archive tag. Temporary transfer directories and encoded source fragments are forbidden in the ordinary source tree.
