# Milestone review · 24 November 2026

## Signed-in dashboard and homepage

The workspace now opens directly into a role-specific dashboard after authentication. Its navigation links to the current account's records, sharing, team or operational tasks. The public homepage adds a section index, a keyboard-operated disclosure specimen, registry and accreditation explanations, and motion that respects reduced-motion preferences. [Homepage](evidence/dashboard/home.png) · [Registrar dashboard](evidence/dashboard/registrar.png).

Edge at 390 and 1440 pixels passed the disclosure switch, reduced-motion, dashboard navigation, issuance form, sign-out and horizontal overflow checks. The wallet browser regression passed keyboard login, QR decoding, signed-out verification and reopening a disabled link. These checks used the existing local Compellio stack and synthetic records. Physical-phone acceptance remains pending.

## Institution access and workspace acceptance · 25 November

Implementation `69cb3be` extends the previous redesign at `253247a`. Use the [personal walkthrough](manual-testing.md) for commands, fixture passwords and expected screens.

| Phase | Status and observed evidence |
| --- | --- |
| Public entry and guide (M4) | Production build passed. Edge at 390 and 1440 pixels activated the synthetic walkthrough with the keyboard, checked horizontal overflow and opened the public verifier. Hero motion and walkthrough transitions respect reduced motion. No live graduate capability is embedded in the example. |
| University and graduate (M2/M4) | Scoped registrar counts, selected holder, matched version and last successful issuance check. Owner detail, disclosure, per-diploma active shares, QR and disable passed in Edge on the actual local chain. |
| Institutional identity and operations (M2) | The disposable HTTP test submitted a pending institution, checked sign-in and write denial, approved and redeemed a one-time first-admin invitation, assigned registrar and graduate memberships and verified a registrar could neither list nor issue another institution's credential. Staff role change invalidated its session. The operator received aggregate results and an empty diploma list. Invites use a private manual handoff. |
| Registry and release QA (M3/M5) | Fresh PostgreSQL stack ready in 32.0 s. All 16 tests passed in 4.091 s, then the simulator journey and worker rehearsal passed. The [new real-chain proof](evidence/compellio-local.md) records matching v1 checksums, a signed-out result and the exact TAR. The browser decoded the rendered QR to the same share URL and reopened the disabled link in the same tab. Controlled tests cover unavailable and expired outcomes. |

`python scripts/check_access.py` also passed on the real stack in separate Edge contexts. A synthetic campus moved from pending to approved, its first administrator activated and signed in, and the team invitation screen and live chain-health panel worked.

The [homepage](evidence/institution-access/home-desktop.png), [receipt](evidence/institution-access/registrar-receipt.png) and [public verifier](evidence/institution-access/verifier-mobile.png) captures use synthetic data. Mobile evidence is browser emulation. Physical-device testing and separate clean-checkout reviewer acceptance remain pending. Local synthetic identity is validated within the documented scope; hosted identity and operational account recovery remain open. Final report and video review remain M6 work and submission remains M7.

## Candidate acceptance on 25 November 2026

Baseline `5b08fb9`, implementation `5782da2`, acceptance candidate `bc47642`. This section supersedes the earlier milestone snapshots below. The [official requirements matrix](challenge.md), [Registry evidence](evidence/compellio-local.md) and [manual review checklist](manual-testing.md) cover different parts of acceptance.

| Task | Status | Change and evidence | Remaining dependency |
| --- | --- | --- | --- |
| M0 CH-01 and M1 ENG-05 | Completed for baseline | Current organizer downloads matched archived files byte for byte. Baseline production build compiled 31 modules. Baseline smoke passed 14 tests in 0.922 s and both simulator rehearsals. | See M7 for final delivery. |
| M2 DOM-02, local identity | Completed for local fixture policy | Expanded PostgreSQL tests and role journey exercise membership, expiry, logout, same-institution non-owner, second institution, link expiry, disabled links and limited disclosure. | Hosted identity, MFA and operational security remain open plan items. |
| M3 REG-03 to REG-07 | Completed for local candidate | First baseline POST lost its response. The documented find operation returned one matching TAR; the read-only reconciliation matched all evidence. A longer bounded registration timeout preserves serialized, single-attempt writes. Fresh candidate evidence linked above. | Chain operator controls this local chain. |
| M4 UI-01 to UI-05 | Completed for desktop and emulated screens | Supplied PNG, verifier-first landing page, registrar table and keyboard-dismissable receipt, graduate disclosure and same-origin paste. Edge exercised the three roles and public verifier. | Physical phone check under M5. |
| M5 QA | In Progress | Automated checks, screenshots, failure-state fixtures and owner walkthrough. | Physical phone and separate clean-checkout reviewer pending. |
| M6 / M7 | In Progress / Pending | Existing report and video describe prior UI. | Finalize materials at project end, verify recipient access, deliver and retain confirmation. |

Final candidate simulator smoke: fresh stack ready in 63.5 seconds, 15 tests passed in 0.895 seconds, HTTP journey and worker rehearsal passed. TypeScript production build and Ruff passed. Two Edge runs exceeded the navigation load timeout. Direct requests to HTML, JS, CSS, PNG and workspace returned HTTP 200; the test now waits for DOM and logo readiness and runs the loopback browser directly. The ensuing full browser journey passed. Screenshots contain synthetic records only.

### Access matrix from deployed rules

| Actor | Private list and operations | Evidence |
| --- | --- | --- |
| Juniper registrar | Lists institution's credentials in this mode, creates synthetic drafts, confirms issuance for own institution. | HTTP journey, record table and dialog in Edge. |
| Juniper graduate | Lists own issued diplomas; creates, lists and disables own shares. Same-tenant sibling holder denied sharing another graduate's diploma. | Isolated two-holder check, share lifecycle across sign-out, wallet browser test. |
| Alder auditor | Authenticated workspace with empty diploma list. Cannot issue or manage Juniper shares. | Auditor sign-in and empty UI, HTTP role denials. |
| Anonymous | Private endpoints require a session. A valid capability and current evidence allow only award, programme, award date and issuer ID. | Anonymous share journey, expiry, disabled link, pending and mismatched evidence tests. |
| Changed or expired session | Membership rechecked on each call. Idle limit 30 minutes, absolute limit eight hours, logout invalidates the stored session. | Idle expiry and changed role tested; absolute-time condition reviewed in `flows.actor`. |

## 25 November · Workspace and graduate share management

The verified registry implementation and competition materials are preserved in `486bca2` and `97d8501`. Commit `c321571` adds opt-in database access from a desktop SQL client. A password-authenticated host connection to PostgreSQL 16.16 on loopback port 55432 returned the expected database, user and two synthetic institutions.

The workspace and public verifier now use a shared visual identity, responsive layouts and role-specific forms. The graduate wallet lists active shares after a new sign-in. Each row has an independent management identifier and expiry. The private list returns no bearer tokens. Older shares gain identifiers through additive migration 004.

The actual Registry journey issued TAR `urn:tar:eip155.31337:0xdc64a140aa3e981100a9beca4e685f962f0cf6c9`. After signing back in, the holder disabled one share and the sibling link still verified. Anonymous and auditor management requests were denied. The mobile keyboard and same-tab verifier regression passed. TypeScript and Ruff checks passed. The 42.5-second submission video records the earlier validated interface.

On 25 November, a fresh isolated PostgreSQL volume passed all 14 tests in 0.805 seconds using the locally built images. The HTTP journey returned `matched_simulator` and the worker rehearsal matched its synthetic digest. Docker removed the temporary stack and volume. A clean build attempt encountered a Docker Hub TLS timeout.

Baseline commit `2fb2deb` contains the previously verified M1 foundation. This record uses Pending, In Progress, Implemented, Testing, Completed and Blocked. Completed denotes a validated scope. Suggested commit subjects below are proposals.

| Task / milestone | Status | Functionality, files and decision | Test or evidence; limitation | Suggested commit / next |
| --- | --- | --- | --- | --- |
| CH-01, REG-01 / M0 | Completed for onboarding and participation | `challenge.md`, `requirements.md`, `integrations/compellio.md`. Owner confirmed individual eligibility and local Docker scope. | Read official brief/template and all three guide pages. Reviewed W deployment, ABI and BCBCTI applicability. Final artifact channel remains a delivery question. | docs: record official local registry contract / REG-03 |
| ARC-01, OPS-01 / M0 | Completed for local foundation | Modular monolith, domain-separated commitment and explicitly selected provider mode. Evidence index remains historical. | Source review and published hash vector. | docs: reconcile architecture and evidence / M2 |
| ENG-01–05 / M1 | Completed for original foundation | Preserve original workspace, seed and simulator rehearsal. Added dispatcher and an opt-in external network override. | Original two fresh starts documented in [baseline evidence](evidence/index.md). Current run results below. | feat: extend local foundation for issuance / DOM-01 |
| DOM-01, DOM-03, DOM-05 / M2 | In Progress | `002_issuance.sql`, `issuance.py`. Immutable snapshot, private nonce, tenant-scoped shares and audit events. Queue intent is the state on the credential row. | Fresh native PostgreSQL migration and repeated issue HTTP requests passed. Two competing dispatchers, uncertain POST recovery and append-only audit guards are implemented. Concurrent dispatch and uncertain-write reconciliation passed in the isolated suite. | feat: persist tenant-scoped diploma issuance / DOM-02 |
| DOM-02 / M2 | In Progress | `flows.py`, `main.py`. Local credential sign-in, hashed opaque sessions, origin and custom-header checks, tenant and ownership checks. | Authenticated registrar/holder/auditor and anonymous fixture journey passed. Hosted identity and additional security tests pending. | feat: authorize local diploma workflows / QA-01 |
| DOM-04 / M2 | Completed | `proof.py`, `test_proof.py`. Profile v1 uses NFC, RFC 8785, a private random 32-byte nonce and SHA-256 with the plan's domain prefix. | Exact p26 digest, key reorder, equivalent Unicode input, field change and nonce change passed. | feat: implement canonical diploma commitments / REG-04 |
| REG-03–07 / M3 | Completed for local-chain acceptance | `registry.py`, `issuance.py`, external setup script and Compose override. Durable pre-write state and serialized POST. Verify current and historical records plus local EVM checksum. | See dated actual-provider evidence below. Mocked mismatch, wrong chain, invalid RPC and matching responses passed. The operator can attach a known matching TAR using the read-only reconciliation command. Unknown references remain in review. | feat: verify Compellio TARs on the local chain / release-path rehearsal |
| UI-01–04 / M4 | Completed for local demonstration | `credentials.tsx`, `main.tsx`, `style.css`. Registrar review, wallet, QR/text share, anonymous verifier and source-specific result. | Strict TypeScript/build and simulator HTTP journey passed. Phone/keyboard validation tracked separately. | feat: add registrar wallet and public verification views / UI-05 |
| UI-05, QA-01–05 / M4–M5 | In Progress | `journey.py`, `test_registry.py`, `scripts/smoke.py`. Bounded local QA only. | Partial role and disclosure matrix tested. Local performance, service restart and outage checks passed. Physical phone review and independent release acceptance remain open. | test: exercise synthetic diploma journeys / candidate review |
| SUB-04 / M6 | Implemented | `adoption.md` documents buyer, user, outreach and measurable pilot. | Hypotheses only. No stakeholder interviews represented as completed. | docs: outline registrar pilot / owner review |
| SUB-01–03, SUB-05 / M6 | In Progress | Official-template report, actual-path demo, accessible repository and independent reviewer handoff. | The local report and video are present. Publish the reviewed release and verify recipient access before delivery. | docs: prepare competition artifacts / M7 |
| M7 submission and jury | Pending | Check links, freeze release, deliver through confirmed channel and retain acknowledgement. | Owner decision required before external submission. | release: identify jury candidate / owner submission |

## Results and personal verification

- Fresh temporary PostgreSQL, FastAPI and dispatcher: five tests passed in 0.329 s, then the HTTP journey returned `matched_simulator` at 2026-11-24T19:52:40Z. It exercised login, denied roles, draft, repeat issue, wallet share, anonymous verification, disable and logout. The test cluster was stopped afterward.
- Six focused proof and Registry contract tests passed in 0.095 s, including the two proof tests from the earlier run. These are local fixtures.
- TypeScript and Vite built 30 modules. Python Ruff checks passed. See [manual testing](manual-testing.md) for reproducible commands, accounts, URLs and expected results.
- Actual provider results are recorded separately from simulator results. The external environment requires Docker; its engine stalled during setup and was restarted with the owner's permission.

## Architecture and residual risks

FastAPI serves React, local auth and scoped private/public routes. PostgreSQL stores diploma snapshots and nonces, per-mode receipts or TAR references, member roles, sessions, disclosure capabilities and minimal event names. Mode-specific HMAC labels isolate demo logins, sessions and share tokens. The local password seed currently derives from the private database environment. Rotating it invalidates local fixture credentials and existing shares/sessions. Use only synthetic records on loopback. Hosted OIDC/MFA, separate operational secret rotation, rate limiting, revocation with step-up, and accreditation governance require further work. The public route whitelists four fields after successful current proof and capability recheck.

OpenAPI at `/docs` lists session, draft, issue, wallet, share and public routes. The same-origin browser client supplies the custom mutation header. The API and dispatcher share domain code. Provider unavailability never selects the simulator.

## Actual provider and release-candidate results

- The [sanitized TAR record](evidence/compellio-local.md) documents the successful three-role journey and the same checksum after restarting the Registry and chain.
- Final fresh Compose fixture run on 24 November reached readiness in 27.1 seconds. All 14 unit/integration tests passed in 0.750 seconds, followed by the simulated HTTP journey and legacy simulator rehearsal. Tests include cross-tenant constraints, session timeout, changed membership, duplicate-worker exclusion and uncertain-write reconciliation. The temporary project was removed.
- Ten sequential anonymous verification requests on the local chain had a median of 0.695 s and nearest-rank p95 of 1.109 s. During an intentional local Registry API stop the verifier returned proof_unavailable and omitted diploma details. The same share verified after recovery and was then disabled.
- Edge desktop captured the real registrar, holder and anonymous verifier workflow. A 390 × 844 browser viewport loaded the application shell. The [one-page organizer-template report](submission/report.pdf) contains the supplied contact and two artifact links. The [42.5-second H.264 demonstration](submission/demo.mp4) shows a real local-chain issuance and a subsequently disabled share.
- The report links to the repository's main branch and the expected video path. Recipient access and the hosted video link require publication of these working-tree changes. No external submission or reviewer-access change was made.
- The mobile browser regression found a stale result when a disabled link was reopened in the same tab. The verifier now rechecks fragment navigation and discards superseded responses. After rebuilding, keyboard sign-in, 390-pixel wallet, anonymous 320-pixel verifier, absence of horizontal overflow and same-tab invalidation passed. A separate PostgreSQL restore preserved the existing issued record and TAR reference.
