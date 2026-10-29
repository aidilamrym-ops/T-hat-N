# Archive policy

Status: 2026-10-25.

This directory is reserved for **non-sealed** historical material only.

Sealed certificates and audit reports referenced by
`reports/FENCE_REGISTRY.md` must remain at their registered paths under
`reports/`. Moving them breaks the machine-checkable `sha256LF <hash> <path>`
certificate lines and the registry guard.

Current state:

- Audit reports (`AUDIT_*.md`) remain in `reports/`.
- Figure-eight r4 prereg, receipt, and report remain in `reports/`.
- Temporary scratch files are not stored here; they belong outside the
  repository.


