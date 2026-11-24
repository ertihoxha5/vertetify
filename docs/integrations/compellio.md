# Compellio onboarding

**Status on 23 November 2026:** sandbox access pending. The local simulator persists synthetic digests in PostgreSQL and returns a locally generated `sim-` reference. Its lookup confirms only a local database match. No vendor host, routes, credentials or response format are configured.

The integration owner maintains this matrix. The project owner obtains answers through the organizer's approved support channel. Review each open row on **25 November 2026 (CET)**. If access is still pending on 30 November, the project owner follows up with the organizer.

| Capability | State | Source / revision | Required follow-up |
| --- | --- | --- | --- |
| Sandbox provisioning | Unavailable to this project | Owner kickoff, 23 Nov | Obtain approved host, scope, tenant binding, access window, credential provisioning and rotation path. |
| Authentication | Unknown | BCBCTI guide revision pending | Obtain scheme, scopes, expiry and environment restrictions. |
| Register | Unknown | Guide revision pending | Confirm exact operation, schema, field allowlist, commitment encoding, size and request IDs. |
| Retrieve and verify | Unknown | Guide revision pending | Confirm reference type, lookup operation, validation semantics, evidence shape, timestamps and finality. |
| Retry and reconciliation | Unknown | Guide revision pending | Confirm idempotency key, duplicate behavior and lookup after an ambiguous write. |
| Limits and lifecycle | Unknown | Guide revision pending | Confirm quotas, throttling, error classes, pending/absent states, retention, revocation and resets. |
| Local simulator | Confirmed locally | Repository implementation, M1 | Keep local references and rehearsal evidence labeled simulator. |

## First approved sandbox rehearsal

1. Owner records written permission, exact environment, documentation revision, allowed synthetic payload, operations and evidence policy. Provision credentials outside the repository.
2. Integration owner prepares one synthetic commitment using the approved schema. Capture the checked commit, environment label and UTC time. Send one authorized registration and retain only permitted sanitized fields.
3. Retrieve the record using the documented reference and check the returned commitment and documented finality criteria. On ambiguous acknowledgement, pause and reconcile using the documented procedure.
4. Accept live evidence only when the permitted write and independent read agree and the documented final state is established. Record sanitized reference policy, times, operation outcomes and proof scope. Omit authorization headers, tokens, private nonce, full payloads and personal data.

The organizer's reply gates the adapter, live proof and scoring evidence. Fixture seeding, simulator readback and local UI/API checks can proceed independently.
