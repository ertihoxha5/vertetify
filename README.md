# Vertetify

Vertetify is a proof of concept for issuing and verifying digital university diplomas. It is being developed for **BlockJump Kosovo Open Innovation Challenges 2026**, Challenge 1 · Certifications.

## Why Vertetify?

Verifying a diploma can mean contacting the issuing university and waiting for a manual check. Vertetify explores a simpler workflow where a graduate shares a diploma by QR code and a verifier can check its authenticity online.

## How it will work

1. An authorized university registrar issues a synthetic diploma.
2. Vertetify registers a cryptographic proof through the Compellio Registry API.
3. The graduate shares a QR link and chooses which diploma details to disclose.
4. The verifier opens the link and sees the verification result and when it was checked.

## Project status

The local foundation serves a read-only synthetic institution workspace through FastAPI and React. A one-shot worker migrates PostgreSQL, seeds two fictional tenants and can rehearse a simulated registration and lookup. Issuance, graduate sharing, production authentication and live provider verification are later milestones.

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

The setup worker exits successfully after applying migrations and fixtures. Repeat seeding preserves existing rows. The rehearsal writes and reads a synthetic digest and prints a simulator reference. The fixture roles are sample records. The browser exposes only institution names and counts. Health endpoints are `/api/health/live` and `/api/health/ready`.

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
