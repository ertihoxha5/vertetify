# Local proof-of-concept architecture

## ADR 1 · Shared application and transactional worker

FastAPI serves the compiled React app at the same origin. PostgreSQL holds tenant membership, session handles, diploma snapshots, queue state, references, shares and audit events. The setup worker migrates and seeds the database. The dispatcher claims queued work under a database session lock. A registrar creates a sealed draft and confirms issuance separately. The transition to queued and its audit event commit together. The dispatcher commits its dispatch marker before asking the provider to write. A restart with an uncertain write moves the record to review.

## ADR 2 · Two checksums with distinct purposes

The private diploma commitment binds the normalized academic fields to a random nonce. Its input is the domain-separated prefix, 32-byte nonce and RFC 8785 canonical diploma bytes. The Registry receives a versioned type and this commitment. Its checksum binds the canonical **envelope** to the TAR contract. A verifier recomputes the private commitment and the envelope checksum, reads the latest and original REST records, checks chain ID and compares the checksum stored in the sole contract version. See [actual provider evidence](evidence/compellio-local.md).

## ADR 3 · Explicit evidence source and disclosure

The default mode uses a PostgreSQL simulator receipt. The registry override uses the official external Docker network and distinct chain references. The credential row, session and share lookup are mode-scoped. Public verification requires a live, enabled share before and after the evidence read. It returns only the four approved academic fields on a match. An unavailable provider yields a dated failure result. The local app has synthetic issuer authority and loopback-only HTTP. The approved hosted identity and institutional trust arrangements are separate deployment work.

## Source map

| Location | Responsibility |
| --- | --- |
| `backend/main.py`, `flows.py` | Same-origin routes, local sign-in, role and object checks, public projection |
| `backend/migrations/`, `store.py` | Versioned data model, tenant constraints, immutable snapshots and transition guards |
| `backend/issuance.py`, `dispatch.py`, `reconcile.py` | Durable issue state, serialized dispatch, bounded read retries, verified manual recovery |
| `backend/proof.py`, `registry.py`, `worker.py` | Canonical diploma proof, official provider adapter, setup and local simulator |
| `frontend/src/` | Registrar, holder, institution and anonymous verification views |
| `scripts/`, Compose files | Startup, external provider setup, isolated test and browser verification |

The [task tracker](progress.md) records security and release limitations. [Manual testing](manual-testing.md) covers the supported local identity and actor workflows.
## Local identity and operations extension

Migration 005 adds institution requests, 48-hour invitations, invited accounts, append-only access events and daily verification counts. Approval, first-admin invitation, activation and staff permission changes are transactional. The operator is a local fixture in a separate platform tenant. An approved institution has one first administrator; team invitations grant a registrar, auditor or holder role within that tenant. Staff permission changes invalidate active sessions. Generated account passwords and invitation capabilities are high-entropy random values. The database stores keyed digests for both, scoped to the environment. Public request status uses an opaque request UUID and returns only pending or approved.

The registrar selects a holder from active membership in its own institution. Graduate detail pages select from the server's owner-scoped list, and the share-list query checks the same holder and tenant. The operator dashboard uses counts of issuance events and aggregate verification outcomes. Outcome counters contain only UTC day, registry mode, result and count. Registry health samples Swagger and chain identity independently. Hosted identity, contact verification, email delivery, account recovery and independent release acceptance remain outside the validated local flow.
