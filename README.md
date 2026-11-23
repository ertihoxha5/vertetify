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

Early development. The first milestone covers the repository setup, local development environment, and a clearly labeled registry simulator. The live Compellio integration is planned once sandbox access and the official API instructions are confirmed.

## Planned stack

- **Frontend** — React and TypeScript
- **Backend** — FastAPI and Python
- **Database** — PostgreSQL
- **Registry integration** — Compellio Registry API

## Privacy

The proof of concept uses synthetic diplomas and fictional institutions. The design keeps diploma details in the application and sends only the approved proof data to the registry. API credentials stay outside the repository.

## Getting started

Local setup and test commands will be added once the first milestone is complete.

Built by Erti Hoxha.
