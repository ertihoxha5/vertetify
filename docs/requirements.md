# Registry requirements traceability

Source G is the organizer's Getting Started Guide v1.1. Source W is [DCAP.Web at the reviewed revision](https://github.com/compellio/DCAP.Web/tree/bd265515804cd969479959b7bb3e0f170e332454). Test doubles and simulator tests are labeled separately from the [execution evidence](progress.md).

## Challenge 1 technical acceptance

Candidate `4703420`. The [acceptance record](evidence/compellio-local.md#profile-compliance-acceptance) contains the concrete IDs, service versions, terminal results and browser evidence.

| Guide page and section | Requirement | Implementation and correction | Status | Validation and actual outcome |
| --- | --- | --- | --- | --- |
| 1, step 1 | Use the official deployment separately from the PoC | `start_registry.ps1` uses the pinned upstream Compose file outside Git. PowerShell implements the guide's shell setup on Windows. | Passed | External provider Compose project present. Registry and chain images and bindings inspected. |
| 1, step 2 | Start a funded local chain and inspect Swagger | Registry and Anvil on a private Compose network, loopback host ports 18660 and 18545. | Passed | Both containers running. Swagger reported IETF SATP Registry API 1.0. RPC chain ID 31337; real contract deployment succeeded. |
| 1, step 3 | POST JSON serially, require 201 and retain returned TAR | Dispatcher persists a write marker and TAR. Adapter now checks ID, version, checksum and returned data immediately. | Corrected and passed | Real 201 path and later readback succeeded. Malformed create-response fixture rejected. |
| 1, step 4 | Read latest and historical records; updates preserve previous versions | Adapter checks both GETs and pins immutable diplomas to REST v1. PUT exists in Swagger. | Passed for current scope | Both reads matched. Controlled changed-latest and changed-historical fixtures failed closed. Credential amendment and revocation writes are outside the implemented workflow. |
| 1, step 5 and 3, checksum, JCS, anchoring | Hash exactly the canonical off-chain TAR data and compare the corresponding contract value | RFC 8785 then SHA-256, `totalVersions()` and `getChecksum(uint256)`. Independent script uses Foundry cast and a separate HTTP reader. | Passed | Registry, contract and locally calculated values identical. Deployed contract slot 0 corresponds to REST v1. |
| 1, notes and 3, TAR profile | A profiled record points to a type-defining TAR in its context | Previously only a type field. New diploma envelopes bind a registered Vertetify profile through `@context`. Verify the expected profile definition and its anchor. Preserve pre-profile evidence. | Corrected and passed | New profile and diploma each passed version-specific readback and independent contract comparison. |
| 1, notes | One registration at a time; handle deployment and funding failure | Database session lock covers profile and diploma writes. Lost write responses require review; profile recovery accepts only a proven matching TAR. | Passed within single-writer deployment | Real profile and diploma posted serially. Controlled two-worker and uncertain-write tests passed. Other applications must use their own stack or coordinate writes. |
| 1, step 6 and 3, wallet, gas, network | Local chain suffices. A public testnet would need separate funding, key, RPC and chain ID. | Only the external local Registry signs. No key enters Vertetify. | Local scope passed; public network optional | Funded local deployment and wrong-chain rejection checked. No public transaction performed. |
| 2, steps 1-6 and notes; 3, STIX/TAXII | BCBCTI stack, collections, status, manifests, STIX profile and updates belong to Challenge 3 | Challenge 1 uses the standalone Registry stack. | Out of scope | Organizer headings and the BCBCTI architecture distinguish the two stacks. |
| 3, local chain, smart contract and TAR ID | Separate private records, off-chain JSON and per-record on-chain checksums; recognize reset risk | PostgreSQL retains diploma and nonce. TAR ID identifies the contract and EIP-155 chain. Browser exposes only approved fields after verification. | Passed | Independent read matched the address in the TAR. Anonymous share, disabled share and scoped access checks passed. Wiping the chain invalidates historical proof. |

## Supporting references

| ID and source | Requirement and applicability | Task and implementation | Validation and result | Remaining limitation |
| --- | --- | --- | --- | --- |
| W1 · Deployment and execution | File-backed registry data, local EVM and optional explorer. | REG-01 · distinct Registry and chain volumes, omit explorer. | Reviewed actual upstream compose and documented port differences. | No third-party source copied. Standalone DCAP repository URL returned 404. |
| B1 · brief v1.2 | Issue, register and verify academic credentials through real Registry. | REG-07 / UI-01–03 · complete browser workflow targets local chain and simulator. | [Actual TAR, version and on-chain checksum](evidence/compellio-local.md), [personal walkthrough](manual-testing.md). | Local chain and synthetic issuer authority only. |
| B2 · brief/template v1.2 | Accessible repo, ≤4-page report, ≤2-minute demo, adoption plan. | SUB-01–05 · [competition checklist](challenge.md) and [pilot proposal](adoption.md). | Direct brief and template review. | Final artifacts and delivery tracked separately. |
