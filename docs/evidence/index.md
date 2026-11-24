# Foundation evidence · 23 November 2026

For the subsequent official-provider run, see [actual local-chain verification](compellio-local.md).

Checked the local working tree based on `158ff97` (README-only baseline). The implementation was uncommitted at verification time. Host tools included Python 3.12.1, Node 24.19.0, Docker Engine 29.5.2 and Compose 5.1.3. The Linux image build used Node 22, Python 3.12 and PostgreSQL 16.

| Gate | Command / artifact | Observed result |
| --- | --- | --- |
| M0 discovery | [Challenge record](../challenge.md) and [compatibility matrix](../integrations/compellio.md) | Local scope and open questions recorded. Brief and template links were inaccessible during discovery. Applicant category, final channel and provider access remain open. |
| M1 build | `npm run build` in frontend | Strict TypeScript and Vite production build passed. |
| M1 lint | `ruff check backend scripts` | Passed. |
| Configuration | `python scripts/setup.py`, `docker compose config --quiet`, `git check-ignore .env` | Generated local password, valid Compose configuration, ignored local environment. |
| Startup | `docker compose up -d --build --wait --wait-timeout 120` | Database and web healthy, setup worker exited successfully. Initially port 8080 was occupied. Retested on 8184 and confirmed the workspace API returned two institutions with member counts 1 and 2. |
| Fresh run 1 | `python scripts/smoke.py` | New volume, cached build, ready in 14.0 s. HTTP shell, liveness, readiness and workspace checks passed. Three backend tests passed. Local simulator write/read matched. Exit 0. |
| Fresh run 2 | `python scripts/smoke.py` | Independent new volume, cached build, ready in 12.8 s. Same HTTP checks, three backend tests and simulator rehearsal passed. Exit 0. |

The tests cover repeated schema setup and seeding, scoped receipt lookup, repeat registration, fixture counts and rejection of hosted/live configurations. Both temporary test projects were removed. The normal local project remains available on loopback. CI is configured to rerun lint and the isolated suite on pushes and pull requests. Remote CI and live Compellio evidence are pending.
