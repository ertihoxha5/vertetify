# Vertetify

Vertetify is a proof of concept for issuing and verifying digital university diplomas. It is being developed for **BlockJump Kosovo Open Innovation Challenges 2026**, Challenge 1 · Certifications.

## Why Vertetify?

Verifying a diploma can mean contacting the issuing university and waiting for a manual check. Vertetify explores a simpler workflow where a graduate shares a diploma by QR code and a verifier can check its authenticity online.

## Credential workflow

Open [the homepage](http://127.0.0.1:8184) for the environment label, [the public verifier](http://127.0.0.1:8184/verify) to paste a graduate's share, or [the workspace](http://127.0.0.1:8184/?workspace) for registrar, graduate and auditor sign-in. The [candidate walkthrough](docs/manual-testing.md) includes the physical-phone and independent reviewer checks.

1. An authorized university registrar issues a synthetic diploma.
2. Vertetify registers a cryptographic proof through the Compellio Registry API.
3. The graduate reviews the four disclosure fields and shares an expiring QR link.
4. The verifier opens the link and sees the verification result and when it was checked.

## Project status

The local app supports synthetic registrar drafts, queued issuance, a graduate wallet, QR sharing and anonymous verification. The default deployment uses a labeled simulator. A separate Compose override selects the official local Compellio Registry and blockchain. Consult the [progress and acceptance record](docs/progress.md) for actual validation results and remaining release gates.

## Stack

- **Frontend** — React and TypeScript
- **Backend** — FastAPI and Python
- **Database** — PostgreSQL
- **Registry integration** — Compellio Registry API

## Privacy

The proof of concept uses synthetic diplomas and fictional institutions. The design keeps diploma details in the application and sends only the approved proof data to the registry. API credentials stay outside the repository.

## Getting started

From the repository root, use Python 3.12 and Docker with Compose v2.20 or newer and Linux containers. The first build needs network access for images and locked dependencies.

```sh
python scripts/setup.py
docker compose up -d --build --wait
```

Open [the local workspace](http://127.0.0.1:8184). FastAPI serves the frontend and API from the same origin. The app exposes only a loopback port. PostgreSQL uses a project-private volume. Change `WEB_PORT` in the ignored `.env` if port 8184 is occupied. Setup generates a random local database password once. Keep that value with its volume across restarts.

```sh
docker compose ps -a
docker compose run --rm worker python worker.py seed
docker compose run --rm worker python worker.py rehearse
docker compose down
```

The setup worker exits after applying migrations and fixtures. A dispatcher processes issuance requests. The legacy worker rehearsal exercises the simulator only. Health endpoints are `/api/health/live` and `/api/health/ready`. Use the [personal testing walkthrough](docs/manual-testing.md) for accounts, passwords, browser steps and expected outcomes. Use the [Compellio setup guide](docs/integrations/compellio.md) to run the official provider in a separate environment.

## Connect to PostgreSQL

In a terminal at the project root, open the running database with:

```powershell
docker compose exec db psql -U vertetify -d vertetify
```

Use `\dt` to list tables, `SELECT name FROM tenants ORDER BY name;` to view the two synthetic institutions and `\q` to exit.

For a desktop SQL client, enable the loopback port on the database service:

```powershell
docker compose -f compose.yaml -f compose.database.yaml up -d --wait db
```

In pgAdmin or DBeaver choose PostgreSQL, host `127.0.0.1`, port `55432`, database and username `vertetify`. Use the existing `POSTGRES_PASSWORD` from your private local `.env`. The connection is local TCP, with SSL disabled. If the port is occupied, set `POSTGRES_HOST_PORT` in `.env` and repeat the command. To keep desktop SQL access when starting the whole official Registry deployment, include both `-f compose.registry.yaml` and `-f compose.database.yaml` after `-f compose.yaml`.

## Baseline checks

```sh
python scripts/smoke.py
```

The smoke command creates a unique Compose project with its own database, generated password and ephemeral loopback port. It builds the frontend with strict TypeScript checks, migrates and seeds the database, checks HTTP responses, runs the backend tests and rehearses a simulated registration and lookup. It removes its own containers and volume on exit. Run it twice for independent fresh starts.

For individual source checks, run the following from the root with Node 22.12+ and Python in an activated virtual environment.

```sh
npm --prefix frontend ci
npm --prefix frontend run build
python -m pip install -r backend/requirements.txt ruff==0.12.3
python -m ruff check backend scripts
```

See [challenge discovery](docs/challenge.md), [Compellio onboarding](docs/integrations/compellio.md) and the [milestone evidence index](docs/evidence/index.md).

Built by Erti Hoxha.

## Jury materials

Read the [competition report](docs/submission/report.pdf), watch the [recorded browser demonstration](docs/submission/demo.mp4), or inspect the [actual TAR evidence](docs/evidence/compellio-local.md). The [architecture decisions](docs/architecture.md) and [requirements traceability](docs/requirements.md) connect the implementation to the organizer guide.
