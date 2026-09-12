# LCARS-Framework — Available Versions

Generated: 2026-01-30

This file lists the recent repository snapshots, branches and noteworthy commits available locally.

## Branch tips and snapshots

- `tidy/only-runtime` — 1e88ccf — "chore: remove hardcoded tokens, add .env to .gitignore and .env.example, add redaction script"
- `feature/os-mvp` — 1e88ccf — same token-clean commit (points to `1e88ccf`)
- `backup-before-restore-20260130_160239` — 1e88ccf — backup created before restore
- `backup-before-secret-clean` — 717028c — backup from secret-clean flow
- `pre-restore-e526021-20260130_160752` — e526021 — backup made before reset to `e526021`
- `master` — e526021 — "feat: Add OS MVP with Start Menu, Process Supervisor, and Session Manager"

## Notable commits

- 1e88ccf — chore: remove hardcoded tokens, add .env to .gitignore and .env.example, add redaction script
- 717028c — (backup-before-secret-clean) chore: remove hardcoded tokens, add .env to .gitignore and .env.example, add redaction script
- e526021 — feat: Add OS MVP with Start Menu, Process Supervisor, and Session Manager
- e115658 — feat: Add OS MVP with Start Menu, Process Supervisor, and Session Manager (earlier)
- 77ed8c5, 67f4c58, 1fa3c38 — index/stash/untracked snapshots related to secret-clean operations

## Reflog highlights

- Multiple recent `reset`/`checkout` operations moved HEAD between `e526021` and `1e88ccf` around 2026-01-30.
- Backup branches were created before resets: `backup-before-restore-20260130_160239`, `pre-restore-e526021-20260130_160752`.

## Where to inspect more

- Git branches: `git branch --all --verbose --sort=-committerdate`
- Recent commits: `git log --all --decorate --oneline -n 100`
- Reflog (local HEAD movements): `git reflog --date=iso -n 200`
- Raw reflog file: `.git/logs/HEAD`
- Compare snapshots: `git diff --name-status <refA> <refB>` (example: `git diff --name-status backup-before-restore-20260130_160239 master`)

## Recovery notes

- If your changes from "yesterday" were never committed, a hard reset could have overwritten them. Possible recovery steps:
  - Inspect `git fsck --lost-found` for dangling blobs/commits.
  - Search backup branches created above for the state you expect.
  - Check external backups or cloud copies if available.

If you want, I can expand this file with per-file diffs or include the exact `git log` outputs appended below.
